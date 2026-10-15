# How it works

```
 ┌────────────────────┐   LAN, Tuya protocol 3.5    ┌─────────────────────┐
 │ SK19 Pro projector │◄───────────────────────────►│ Tuya Local          │
 │ (TCP 6668)         │  one persistent connection  │ (make-all/tuya-local)│
 └────────────────────┘                             └──────────┬──────────┘
                                                               │ entities
                          ┌────────────────────────────────────┴───────────┐
                          │ SK19 Pro Projector (this repo, custom_components/sk19_pro)
                          │  • device config  → tuya_local_devices/*.yaml   │
                          │  • card + panel   → frontend/sk19-card.js       │
                          │  • sleep timer    → timer.py + services         │
                          │  • assets         → img/, catalogue.json        │
                          └─────────────────────────────────────────────────┘
```

The projector never talks to the cloud for control. Everything is local, through the standard
**Tuya Local** integration; this repo adds the device definition, a UI, and a sleep timer on top.

## Pieces

### Device config (`tuya_local_devices/sk19_pro_projector.yaml`)
A Tuya Local device definition mapping data points (DPs) to Home Assistant entities: master power,
colour light, projection on/off and brightness, play/pause, sound, volume, Bluetooth, playback
order, next/previous, and the two scene selects (projection 0-59, lighting 0-7). The file is
**generated** by `gen_ha_config.py` from `projections.json` and `lighting_scenes.json`; the DP
meanings are in [DPS.md](DPS.md). The integration copies it into
`custom_components/tuya_local/devices/` at startup.

> Tuya Local reads device configs when its config entry loads, so after the file changes Home
> Assistant needs a restart (or a reload of the Tuya Local entry) to pick it up.

### The card (`frontend/sk19-card.js`)
One dependency-free custom element, `sk19-projector-card`, plus a thin `sk19-panel` wrapper for the
sidebar panel. It discovers the device by looking for `select.*_projection_scene` and deriving the
sibling entities from that prefix, so there's nothing to configure. Layout is driven by CSS
container queries (phone: one column; wide: two columns), and a small `_fit()` makes the card fill
the viewport height so only the scene list scrolls.

Things that look odd but are deliberate:
- **Re-registration of the custom elements.** HA swaps in a scoped-custom-element-registry polyfill
  shortly after startup; elements defined on the native registry before that are invisible to
  Lovelace ("Custom element doesn't exist"). The script re-registers whenever the registry object is
  replaced. See `register()` at the bottom of the file.
- **Scroll preservation.** The card rebuilds its DOM on every state change, so scroll positions are
  saved and restored around each render.
- **Tap protection.** The device takes seconds to act on power and drops writes around it, so rapid
  taps only make it flap. The power button locks for 4 s after a tap; powering off while a sleep
  timer runs needs a second tap; scene taps are last-wins with a 350 ms window and re-tapping the
  active scene is ignored; other toggles ignore repeats within 600 ms. This lives in the card only,
  so entity controls elsewhere in HA, automations and the hardware remote bypass it.
- **Last known value.** While the device is unavailable (reload, Wi-Fi blip) numeric labels keep the
  last real value instead of showing `NaN`.

### Serving and caching (`__init__.py`)
- The script URL carries `?v=<mtime>` and is served `immutable` so cold starts hit the disk cache.
  The version is computed when HA starts, so **a JS change needs an HA restart to be picked up.**
- It is registered both as an `extra_js_url` and as a Lovelace resource, and as a custom panel
  (`/sk19-projector`). If a dashboard with URL `sk19-dashboard` exists, the panel's sidebar entry is
  hidden so there's only one.
- `/sk19_pro/now` returns the server clock so the countdown is right on devices with a wrong clock.

### Sleep timer (`timer.py`)
`sk19_pro.start_timer` / `cancel_timer` services and a `sk19_pro.sleep_timer` state
(`running` / `idle`, plus `end`, `minutes`, `fade_seconds`, `last_run`).

- Fades projection brightness, colour-light brightness and (if sound is on) volume over the last
  *fade_seconds*, then turns the master switch off.
- The power-off is **confirmed** against the entity state and retried up to 3 times.
- Original levels are saved (also to `.storage`), re-applied right after power-off and again at the
  next power-on, because a device that is off ignores writes.
- State survives restarts; a timer that expired more than 2 minutes before startup is dropped.
- `last_run` records `{result, attempts, at}` of the previous run, so a failure leaves evidence.

### Catalogues and assets
`catalogue.json` maps scene indices to names, categories and image files; `img/` holds the
downsized artwork. Both are built from the Smart Life app's cached panel by the scripts in the repo
root (see [HACKING.md](HACKING.md)).

## Why not stream video / change the videos?
The projector's "videos" are 60 built-ins selected by index; there is no media data point and the
only open network port is the control port. See [RESEARCH.md](RESEARCH.md).
