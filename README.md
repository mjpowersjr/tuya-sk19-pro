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
   (see Credentials below) → choose *Projector light*.

The panel finds the entities by name; no dashboard editing needed.

**Optional dashboard** (needed only if you want the projector as a *Default dashboard*, e.g. on a Fire
tablet): Settings → Dashboards → Add dashboard → *New from scratch*, title `Projector`, URL
`sk19-dashboard`, then in its raw editor use:
`views: [{title: Projector, path: projector, panel: true, cards: [{type: "custom:sk19-projector-card"}]}]`.
When that dashboard exists the integration hides its own sidebar entry so you don't see two. The card is
also available as `type: custom:sk19-projector-card`.

## Repo contents

- `custom_components/sk19_pro/` – the HACS integration (panel, icons, catalogue, device YAML)
- `DPS.md` – data point map and firmware notes
- `projections.json`, `lighting_scenes.json` – scene catalogues (DP 122 / DP 121)
- `sk19.py` – local control CLI (protocol 3.5): `status`, `set <dp> <value>`
- `build_catalogue.py`, `build_lighting.py`, `gen_ha_config.py`, `build_integration.py` –
  regenerate everything from the app's cached panel (`panel/`, not committed)

## Credentials

The local tools read `sk19.toml` (gitignored; copy `sk19.example.toml`, `chmod 600`) or the
env vars `SK19_DEVICE_ID`, `SK19_HOST`, `SK19_LOCAL_KEY`. The local key is never committed.
Get it from the Tuya IoT Platform (Cloud → API Explorer → Query Device Details).
In Home Assistant you enter the same three values once in the Tuya Local setup form.

## Notes

Icons in `custom_components/sk19_pro/img/` are downsized copies of the artwork shipped in
the device's Smart Life/Tuya app panel, included for personal use with the matching hardware.
