"""Sleep timer: counts down, fades the picture (and sound) over the last seconds, then powers the projector off.

State is published as `sk19_pro.sleep_timer` ("idle" / "running") and persisted, so a restart
mid-countdown picks the timer back up instead of dropping it. The result of the last run is kept in
the entity's `last_run` attribute.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.event import async_track_point_in_utc_time, async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

STATE_ID = "sk19_pro.sleep_timer"
FADE_STEP_S = 4
OFF_ATTEMPTS = 3
OFF_WAIT_S = 20          # how long to wait for the device to confirm power-off before retrying
REAPPLY_DELAY_S = 25     # after the next power-on, wait this long (the device drops early writes) before re-applying
_STALE = timedelta(minutes=2)  # a timer that expired this long ago (while HA was down) is dropped


class SleepTimer:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store: Store = Store(hass, 1, "sk19_pro.sleep_timer")
        self._end: datetime | None = None
        self._minutes = 0
        self._fade_s = 60
        self._base: str | None = None
        self._origs: dict[str, Any] = {}   # entity_id -> level/state before the fade started
        self._pending_restore: dict[str, Any] = {}  # values to put back at the next power-on
        self._last_run: dict[str, Any] | None = None
        self._unsub: list[CALLBACK_TYPE] = []
        self._fade_task: asyncio.Task | None = None
        self._finishing = False
        self._unsub_poweron: CALLBACK_TYPE | None = None

    # ---- entities -------------------------------------------------------------------------
    def _find_base(self) -> str | None:
        for eid in self.hass.states.async_entity_ids("select"):
            if eid.endswith("_projection_scene"):
                return eid[len("select.") : -len("_projection_scene")]
        return None

    def _master(self, base: str | None = None) -> str:
        return f"switch.{base or self._base}_master"

    def _targets(self) -> list[tuple[str, str]]:
        """(kind, entity_id) for everything that gets faded. Volume only matters when sound is on."""
        b = self._base
        out = [("number", f"number.{b}_projection_brightness")]
        # Writing the colour light's brightness drops the device out of a lighting scene, so only
        # fade it when it is a plain colour (no scene selected).
        scene = self.hass.states.get(f"select.{b}_colour_scene")
        if scene is None or scene.state in ("unknown", "unavailable", ""):
            out.append(("light", f"light.{b}_colour"))
        sound = self.hass.states.get(f"switch.{b}_sound")
        if sound is not None and sound.state == "on":
            out.append(("number", f"number.{b}_volume"))
        return out

    def _remember(self) -> dict[str, float | str]:
        """Things that are restored but not faded: after a power cycle the device reports defaults
        for them (music "off", no lighting scene) until something changes."""
        b = self._base
        out: dict[str, float | str] = {}
        for ent in (f"switch.{b}_sound", f"switch.{b}_play"):
            st = self.hass.states.get(ent)
            if st is not None and st.state in ("on", "off"):
                out[ent] = st.state
        scene = self.hass.states.get(f"select.{b}_colour_scene")
        if scene is not None and scene.state not in ("unknown", "unavailable", ""):
            out[f"select.{b}_colour_scene"] = scene.state
        return out

    # ---- public ---------------------------------------------------------------------------
    async def async_setup(self) -> None:
        data = await self._store.async_load() or {}
        self._last_run = data.get("last_run")
        self._pending_restore = dict(data.get("pending_restore") or {})
        self._base = data.get("base")
        if self._pending_restore and self._base:
            self._watch_poweron()
        end = dt_util.parse_datetime(data["end"]) if data.get("end") else None
        if end is None:
            self._publish()
            return
        if dt_util.utcnow() - end > _STALE:
            # expired while HA was down: nothing to turn off, but a fade may have left levels low
            origs = dict(data.get("origs") or {})
            if origs:
                self._pending_restore = {**self._pending_restore, **origs}
                self._watch_poweron()
            self._end = None
            await self._persist()
            self._publish()
            return
        self._end, self._minutes = end, int(data.get("minutes", 0))
        self._fade_s = int(data.get("fade_s", 60))
        self._origs = dict(data.get("origs") or {})
        self._arm()

    async def async_start(self, minutes: int, fade_s: int = 60, base: str | None = None) -> None:
        await self.async_cancel()
        self._base = base or self._find_base()
        if not self._base:
            raise ServiceValidationError("No SK19 projector found; add it in the Tuya Local integration first")
        self._minutes = minutes
        self._fade_s = max(0, min(fade_s, minutes * 60))
        self._end = dt_util.utcnow() + timedelta(minutes=minutes)
        self._origs = {}
        await self._persist()
        self._arm()

    async def async_cancel(self) -> None:
        """Stop the timer; if a fade is in progress, put the levels back."""
        if self._end is None:
            return
        await self._finish("cancelled", restore=True)

    # ---- scheduling -----------------------------------------------------------------------
    def _arm(self) -> None:
        assert self._end is not None
        self._disarm()
        now = dt_util.utcnow()
        fade_at = self._end - timedelta(seconds=self._fade_s)
        if self._fade_s and fade_at > now:
            self._unsub.append(async_track_point_in_utc_time(self.hass, self._start_fade, fade_at))
        elif self._fade_s and now < self._end:
            self._start_fade(now)
        self._unsub.append(async_track_point_in_utc_time(self.hass, self._on_end, self._end))
        if self._base:
            self._unsub.append(
                async_track_state_change_event(self.hass, [self._master()], self._master_changed)
            )
        self._publish()

    def _disarm(self) -> None:
        for u in self._unsub:
            u()
        self._unsub = []
        if self._fade_task:
            self._fade_task.cancel()
            self._fade_task = None

    @callback
    def _start_fade(self, _now: datetime) -> None:
        if self._fade_task is None:
            self._fade_task = self.hass.async_create_task(self._fade())

    # ---- fade -----------------------------------------------------------------------------
    @staticmethod
    def _level(kind: str, state) -> float | None:
        try:
            if kind == "light":
                return float(state.attributes["brightness"]) if state.state == "on" else None
            return float(state.state)
        except (KeyError, TypeError, ValueError):
            return None

    async def _set_level(self, kind: str, entity_id: str, level: float, fading: bool = False) -> None:
        if kind == "light":
            await self.hass.services.async_call(
                "light", "turn_on", {"entity_id": entity_id, "brightness": max(1, round(level))}, blocking=False
            )
        else:
            st = self.hass.states.get(entity_id)
            lo = float(st.attributes.get("min", 0)) if st else 0.0
            if fading and entity_id.endswith("_volume"):
                # volume 0 mutes the device and flips its "sound" state; stay at 1 (inaudible)
                lo = max(lo, 1.0)
            await self.hass.services.async_call(
                "number", "set_value", {"entity_id": entity_id, "value": max(lo, round(level))}, blocking=False
            )

    async def _fade(self) -> None:
        try:
            targets = self._targets()
            if not self._origs:
                for kind, eid in targets:
                    st = self.hass.states.get(eid)
                    lvl = self._level(kind, st) if st else None
                    if lvl is not None:
                        self._origs[eid] = lvl
                self._origs.update(self._remember())
                await self._persist()
            while self._end is not None:
                remaining = (self._end - dt_util.utcnow()).total_seconds()
                if remaining <= 0:
                    break
                frac = min(1.0, remaining / max(self._fade_s, 1))
                for kind, eid in targets:
                    if isinstance(self._origs.get(eid), (int, float)):
                        await self._set_level(kind, eid, self._origs[eid] * frac, fading=True)
                await asyncio.sleep(min(FADE_STEP_S, max(remaining, 0.5)))
        except asyncio.CancelledError:
            raise
        except Exception:  # keep the power-off alive even if the fade hiccups
            _LOGGER.exception("Sleep timer fade failed")

    # ---- power-off ------------------------------------------------------------------------
    async def _wait_state(self, entity_id: str, wanted: set[str], timeout: float) -> bool:
        loop_end = self.hass.loop.time() + timeout
        while self.hass.loop.time() < loop_end:
            st = self.hass.states.get(entity_id)
            if st is not None and st.state in wanted:
                return True
            await asyncio.sleep(2)
        return False

    async def _on_end(self, _now: datetime) -> None:
        self._finishing = True
        master = self._master()
        # right after a restart the entities are unavailable for a while
        await self._wait_state(master, {"on", "off"}, 120)
        attempts, ok = 0, False
        while attempts < OFF_ATTEMPTS and not ok:
            attempts += 1
            try:
                await self.hass.services.async_call("switch", "turn_off", {"entity_id": master}, blocking=True)
            except Exception:
                _LOGGER.exception("Sleep timer: turn_off call failed (attempt %s)", attempts)
            ok = await self._wait_state(master, {"off"}, OFF_WAIT_S)
        if not ok:
            _LOGGER.warning("Sleep timer: %s did not confirm power-off after %s attempts", master, attempts)
        await self._finish("off" if ok else "failed", restore=True, attempts=attempts)

    @callback
    def _master_changed(self, event: Event) -> None:
        new = event.data.get("new_state")
        if self._finishing or new is None or new.state != "off":
            return
        # switched off by hand before the timer ran out: nothing left to do
        self.hass.async_create_task(self._finish("switched_off_by_hand", restore=True))

    # ---- restore --------------------------------------------------------------------------
    async def _finish(self, result: str, restore: bool, attempts: int = 0) -> None:
        self._disarm()
        origs, base = dict(self._origs), self._base
        self._end, self._origs, self._finishing = None, {}, False
        self._last_run = {"result": result, "attempts": attempts, "at": dt_util.utcnow().isoformat()}
        if restore and origs and base and result in ("off", "failed", "switched_off_by_hand"):
            # A device that is off ignores writes, so apply now AND again at the next power-on.
            self._pending_restore = origs
            self._watch_poweron()
        await self._persist()
        self._publish()
        if restore and origs and base:
            await asyncio.sleep(2)
            await self._apply(origs)

    async def _apply(self, levels: dict[str, Any]) -> None:
        for eid, val in levels.items():
            dom = eid.split(".")[0]
            if dom == "switch":
                await self.hass.services.async_call(
                    "switch", "turn_on" if val == "on" else "turn_off", {"entity_id": eid}, blocking=False
                )
            elif dom == "select":
                await self.hass.services.async_call(
                    "select", "select_option", {"entity_id": eid, "option": val}, blocking=False
                )
            else:
                await self._set_level("light" if dom == "light" else "number", eid, float(val))

    def _matches(self, eid: str, want: Any) -> bool:
        st = self.hass.states.get(eid)
        if st is None:
            return False
        dom = eid.split(".")[0]
        try:
            if dom == "light":
                return st.state == "on" and abs(float(st.attributes.get("brightness", -99)) - float(want)) <= 6
            if dom == "number":
                return abs(float(st.state) - float(want)) <= 1
        except (TypeError, ValueError):
            return False
        return st.state == want

    def _watch_poweron(self) -> None:
        if self._unsub_poweron:
            self._unsub_poweron()
            self._unsub_poweron = None
        if not self._base:
            return
        self._unsub_poweron = async_track_state_change_event(
            self.hass, [self._master()], self._poweron_changed
        )

    @callback
    def _poweron_changed(self, event: Event) -> None:
        new, old = event.data.get("new_state"), event.data.get("old_state")
        if new is None or new.state != "on" or (old is not None and old.state == "on"):
            return
        if self._end is not None or not self._pending_restore:
            return
        levels = self._pending_restore
        self._pending_restore = {}
        if self._unsub_poweron:
            self._unsub_poweron()
            self._unsub_poweron = None
        self.hass.async_create_task(self._reapply(levels))

    async def _reapply(self, levels: dict[str, Any]) -> None:
        """Right after power-on the device drops writes, so wait, apply, and check it stuck."""
        await asyncio.sleep(REAPPLY_DELAY_S)
        for _attempt in range(3):
            todo = {e: v for e, v in levels.items() if not self._matches(e, v)}
            if not todo:
                break
            await self._apply(todo)
            await asyncio.sleep(8)
        await self._persist()

    # ---- state ----------------------------------------------------------------------------
    async def _persist(self) -> None:
        await self._store.async_save(
            {
                "end": self._end.isoformat() if self._end else None,
                "minutes": self._minutes,
                "fade_s": self._fade_s,
                "base": self._base,
                "origs": self._origs,
                "pending_restore": self._pending_restore,
                "last_run": self._last_run,
            }
        )

    def _publish(self) -> None:
        attrs: dict[str, Any] = {"friendly_name": "SK19 sleep timer", "icon": "mdi:timer-sand"}
        if self._last_run:
            attrs["last_run"] = self._last_run
        if self._end is None:
            self.hass.states.async_set(STATE_ID, "idle", attrs)
        else:
            attrs.update(end=self._end.isoformat(), minutes=self._minutes, fade_seconds=self._fade_s)
            self.hass.states.async_set(STATE_ID, "running", attrs)
