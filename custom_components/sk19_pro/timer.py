"""Sleep timer: counts down, fades the volume over the last seconds, then powers the projector off.

State is published as `sk19_pro.sleep_timer` ("idle" / "running") and persisted, so a restart
mid-countdown picks the timer back up instead of dropping it.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.event import async_track_point_in_utc_time, async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

STATE_ID = "sk19_pro.sleep_timer"
FADE_STEP_S = 4
_STALE = timedelta(minutes=2)  # a timer that expired this long ago (while HA was down) is dropped


class SleepTimer:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store: Store = Store(hass, 1, "sk19_pro.sleep_timer")
        self._end: datetime | None = None
        self._minutes = 0
        self._fade_s = 60
        self._base: str | None = None
        self._orig_volume: float | None = None
        self._unsub: list[CALLBACK_TYPE] = []
        self._fade_task: asyncio.Task | None = None
        self._finishing = False

    # ---- entities -------------------------------------------------------------------------
    def _find_base(self) -> str | None:
        for eid in self.hass.states.async_entity_ids("select"):
            if eid.endswith("_projection_scene"):
                return eid[len("select.") : -len("_projection_scene")]
        return None

    def _master(self) -> str:
        return f"switch.{self._base}_master"

    def _volume(self) -> str:
        return f"number.{self._base}_volume"

    # ---- public ---------------------------------------------------------------------------
    async def async_setup(self) -> None:
        data = await self._store.async_load()
        self._publish()
        if not data:
            return
        end = dt_util.parse_datetime(data.get("end", ""))
        if end is None or dt_util.utcnow() - end > _STALE:
            await self._store.async_save({})
            return
        self._end, self._minutes = end, int(data.get("minutes", 0))
        self._fade_s, self._base = int(data.get("fade_s", 60)), data.get("base")
        self._orig_volume = data.get("orig_volume")
        self._arm()

    async def async_start(self, minutes: int, fade_s: int = 60, base: str | None = None) -> None:
        await self.async_cancel()
        self._base = base or self._find_base()
        if not self._base:
            raise ServiceValidationError("No SK19 projector found; add it in the Tuya Local integration first")
        self._minutes = minutes
        self._fade_s = max(0, min(fade_s, minutes * 60))
        self._end = dt_util.utcnow() + timedelta(minutes=minutes)
        self._orig_volume = None
        await self._persist()
        self._arm()

    async def async_cancel(self) -> None:
        """Stop the timer; if a fade is in progress, put the volume back."""
        if self._end is None:
            return
        await self._stop(restore=True)

    # ---- internals ------------------------------------------------------------------------
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

    async def _fade(self) -> None:
        try:
            if self._orig_volume is None:
                st = self.hass.states.get(self._volume())
                try:
                    self._orig_volume = float(st.state) if st else None
                except (TypeError, ValueError):
                    self._orig_volume = None
                await self._persist()
            if self._orig_volume is None:
                return
            while self._end is not None:
                remaining = (self._end - dt_util.utcnow()).total_seconds()
                if remaining <= 0:
                    break
                level = round(self._orig_volume * min(1.0, remaining / max(self._fade_s, 1)))
                await self.hass.services.async_call(
                    "number", "set_value", {"entity_id": self._volume(), "value": level}, blocking=False
                )
                await asyncio.sleep(min(FADE_STEP_S, max(remaining, 0.5)))
        except asyncio.CancelledError:
            raise
        except Exception:  # keep the power-off alive even if the fade hiccups
            _LOGGER.exception("Sleep timer fade failed")

    async def _on_end(self, _now: datetime) -> None:
        self._finishing = True
        try:
            await self.hass.services.async_call("switch", "turn_off", {"entity_id": self._master()}, blocking=True)
        except Exception:
            _LOGGER.exception("Sleep timer could not turn the projector off")
        await self._stop(restore=True)

    @callback
    def _master_changed(self, event: Event) -> None:
        new = event.data.get("new_state")
        if self._finishing or new is None or new.state != "off":
            return
        # switched off by hand before the timer ran out: nothing left to do
        self.hass.async_create_task(self._stop(restore=True))

    async def _stop(self, restore: bool) -> None:
        self._disarm()
        orig, base = self._orig_volume, self._base
        self._end, self._orig_volume, self._finishing = None, None, False
        await self._store.async_save({})
        self._publish()
        if restore and orig is not None and base:
            await asyncio.sleep(1.5)  # let the off command land before touching the volume
            await self.hass.services.async_call(
                "number", "set_value", {"entity_id": f"number.{base}_volume", "value": orig}, blocking=False
            )

    async def _persist(self) -> None:
        await self._store.async_save(
            {
                "end": self._end.isoformat() if self._end else None,
                "minutes": self._minutes,
                "fade_s": self._fade_s,
                "base": self._base,
                "orig_volume": self._orig_volume,
            }
        )

    def _publish(self) -> None:
        if self._end is None:
            self.hass.states.async_set(STATE_ID, "idle", {"friendly_name": "SK19 sleep timer", "icon": "mdi:timer-sand"})
        else:
            self.hass.states.async_set(
                STATE_ID,
                "running",
                {
                    "friendly_name": "SK19 sleep timer",
                    "icon": "mdi:timer-sand",
                    "end": self._end.isoformat(),
                    "minutes": self._minutes,
                    "fade_seconds": self._fade_s,
                },
            )
