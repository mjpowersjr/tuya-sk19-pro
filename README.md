# SK19 Pro projector (Tuya "Smart 3D Video Projector Light")

Home Assistant package: local control via **tuya-local**, plus an app-style
**Projector** panel (Projection / Lighting / Music tabs) using the mobile app's
names and icons.

## Install (HACS)

1. HACS → ⋮ → Custom repositories → `mjpowersjr/tuya-sk19-pro`, type **Integration**.
2. Download **SK19 Pro Projector** and **Tuya Local** (custom repo `make-all/tuya-local`,
   or from the HACS default list if present). Restart Home Assistant.
3. Settings → Devices & services → Add integration → **SK19 Pro Projector** (one click).
   This restores the tuya-local device config and adds the **Projector** sidebar entry.
   Restart once more if it says it installed the device config.
4. Add integration → **Tuya Local** → enter device ID, host and local key
   (`device.json`, see below) → choose *Projector light*.

The panel finds the entities by name; no dashboard editing needed. The card is
also available as `type: custom:sk19-projector-card`.

## Repo contents

- `custom_components/sk19_pro/` – the HACS integration (panel, icons, catalogue, device YAML)
- `DPS.md` – data point map and firmware notes
- `projections.json`, `lighting_scenes.json` – scene catalogues (DP 122 / DP 121)
- `sk19.py` – local control CLI (protocol 3.5): `status`, `set <dp> <value>`
- `build_catalogue.py`, `build_lighting.py`, `gen_ha_config.py`, `build_integration.py` –
  regenerate everything from the app's cached panel (`panel/`, not committed)

## Credentials

`device.json` (device id + local key) is never committed. Keep it locally; get the key
from the Tuya IoT Platform (Cloud → API Explorer → Query Device Details).

## Notes

Icons in `custom_components/sk19_pro/img/` are downsized copies of the artwork shipped in
the device's Smart Life/Tuya app panel, included for personal use with the matching hardware.
