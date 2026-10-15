# Hacking on it

Everything you need to change, rebuild and test this project. Forks and PRs welcome.

## Layout

```
custom_components/sk19_pro/   the HACS integration (what users install)
  __init__.py                 serving, caching, panel registration, services
  timer.py                    sleep timer engine
  frontend/sk19-card.js       the card + panel (single file, no build step)
  tuya_local_devices/*.yaml   Tuya Local device config (GENERATED, see below)
  catalogue.json, img/        scene names/categories and artwork (GENERATED)
docs/                         architecture, research, data points, troubleshooting
sk19.py, sk19conf.py          local-control CLI + config loading
dump_dps.py                   find the protocol version / dump data points
build_*.py, gen_ha_config.py  regenerate catalogues, images and device YAML
.github/workflows/release.yml checks + automatic GitHub releases
```

## Quick local loop (card)

The card is plain ES modules; there is no bundler.

1. Edit `custom_components/sk19_pro/frontend/sk19-card.js`.
2. `node --check custom_components/sk19_pro/frontend/sk19-card.js`
3. Try it against your real Home Assistant without deploying: serve the file with CORS and load a
   renamed copy in a page that is logged in to HA (browser console on your HA tab):

   ```js
   // python3 -m http.server needs CORS; a 6-line handler that adds Access-Control-Allow-Origin: * works
   let src = await (await fetch("http://localhost:8765/sk19-card.js")).text();
   src = src.replaceAll("sk19-projector-card", "sk19-card-test");
   await import(URL.createObjectURL(new Blob([src], {type: "text/javascript"})));
   const c = document.createElement("sk19-card-test"); c.setConfig({});
   document.body.append(c); c.hass = document.querySelector("home-assistant").hass;
   ```
   (Renaming avoids clashing with the card that is already registered.) Feed it a modified
   `hass` object to exercise states like *unavailable*, a running timer, or another category.

## Deploying a change to your own HA

- HACS → the integration → **Update information** → **Redownload**, then **restart HA**.
  The script URL is cache-busted with a version computed at startup, so even a JS-only change needs
  a restart. (HACS' download comes from `raw.githubusercontent.com`, which caches for a few minutes;
  if the file looks stale, wait and redownload.)
- Check what is really on the box: `/sk19_pro/manifest.json` and `/sk19_pro/frontend/sk19-card.js`
  are served statically, so you can fetch them and grep for your change.

## Releasing

Bump `version` in `custom_components/sk19_pro/manifest.json` and push to `main`. The *Release*
workflow runs the checks and creates the `v<version>` GitHub release, which is what HACS shows.

## Regenerating assets and the device config

Only needed if you want to rebuild from the app's artwork or add scenes. You need the Smart Life
app's cached mini-app panel (pulled from an Android phone with adb:
`/sdcard/Android/data/com.tuya.smartlife/files/Godzilla/MiniApp/<id>/`) placed in `./panel/`.

```bash
python build_catalogue.py     # projections.json + images (DP 122 scenes)
python build_lighting.py      # lighting_scenes.json + UI icons (DP 121)
python gen_ha_config.py       # custom_components/.../tuya_local_devices/*.yaml
python build_integration.py   # downsized images + catalogue.json for the integration
```

`panel/` and `projections/` are gitignored. Don't hand-edit the generated YAML for anything
permanent; add it to `gen_ha_config.py` instead (temporary probes in the YAML are fine, but they
disappear on the next regenerate).

## Exploring data points

```bash
cp sk19.example.toml sk19.toml && chmod 600 sk19.toml   # device id, host, local key
python sk19.py status                  # all DPs the device reports
python sk19.py set 106 40              # projection brightness
python dump_dps.py                     # tries protocol 3.1-3.5
```

Tips: Home Assistant (Tuya Local) holds the device's one LAN connection, so the CLI can time out
(901/905) while it's running. Disable the Tuya Local entry for a minute, or probe through Home
Assistant by adding a temporary select/number entity for the DP in the device YAML.

## Debugging the card on a tablet or phone

The HA Companion app's WebView is inspectable:

1. Enable *Companion app → Troubleshooting → WebView remote debugging* and Android *Wireless
   debugging* (pair with `adb pair`, then `adb connect`).
2. `adb forward tcp:9333 localabstract:webview_devtools_remote_<pid>` (find the socket in
   `/proc/net/unix`), then talk CDP at `localhost:9333/json` or open it in Chrome DevTools.
3. Useful: cold-start the app with `adb shell am force-stop` + `monkey -p <package> 1`, evaluate in
   the page (is `customElements.get("sk19-projector-card")` defined? what does `hui-error-card`
   say?), and intercept the script with the CDP `Fetch` domain to test a fix before deploying.

## Gotchas learned the hard way

- `customElements` may be a polyfill by the time Lovelace looks things up (see ARCHITECTURE).
- A Lovelace *panel view* with a failing card shows a full-screen "Configuration error" with no text.
- `hass` objects are immutable snapshots; re-read `document.querySelector("home-assistant").hass`
  inside polling loops.
- A powered-off projector ignores writes; restore levels at the next power-on.
- Entities created by Tuya Local show up as `<domain>.<device-name>_<entity-name>`; the card and the
  timer discover the prefix from `select.*_projection_scene`, so don't rename that entity's suffix.

## Ideas / not done

- Time/schedule and custom playlists (DPs 116-119, 124, 127/104) - formats partly known, see DPS.md.
- One-shot alarms using the timer engine.
- Upstreaming the device config to `make-all/tuya-local`.
