# Research notes

What was learned about the device while building this, in case it saves you time.

## The device
| | |
|---|---|
| Product | A Tuya-based star/galaxy "Smart 3D (Video) Projector Light". Listings and boxes vary ("Smart 3D Projector Light", "Smart 3D Video Projector Light", "SK19 Pro"), so match on the product id below, not the name |
| Tuya cloud `product_name` / `model` | `Smart 3D Video Projector Light` / `Smart 3D Video Projetor Light` (sic - the typo is in Tuya's data) |
| Product ids | cloud `a5enoboa4fnkicus`; the device reports `fx1h9mjhadi9mytv` on the LAN (Tuya Local warns about it if only one is declared) |
| Category | `xktyd` (projector light) |
| Protocol | **3.5** (local TCP **6668**; nothing else is open) |
| Firmware | Wi-Fi module 1.0.15, separate MCU 1.0.0 |

Protocol 3.5 matters: older tinytuya releases and several tools default to 3.3/3.4 and just time
out. `dump_dps.py` tries all versions and prints the one that works.

## Can it be controlled without the app?
Yes, fully, over the LAN, using the device id + **local key**. You need:

1. A free Tuya IoT Platform project (iot.tuya.com) with the device linked through *Link App Account*.
2. The local key from *Cloud → API Explorer → Query Device Details* (field `local_key`).
3. The device's LAN IP (give it a DHCP reservation).

The key rotates if you re-pair the device in the app.

## Can I stream my own video to it?
Not through any interface that was found:
- No data point carries media; the "projection" DPs are just indices into built-ins.
- The spec lists index range 0-80 but the app and firmware expose 0-59.
- Tuya OTA exposes only the Wi-Fi module; the MCU has no firmware key.
- Replacing content would mean opening the unit (the content is presumably in flash/NAND on the
  MCU side) which was not attempted.

## Behaviours worth knowing
- **Power-on takes a while** to be reported (tens of seconds); power-off 5-10 s.
- A device that is **off ignores writes** to other data points; they may revert when it comes back.
- Changes made with the **hardware remote** *are* reported (≈1 s). Automatic scene advances are too.
- **One LAN connection at a time:** while Home Assistant holds it, `sk19.py` from another machine
  can time out (error 901). Disable the Tuya Local entry first if you need the CLI.
- **Out-of-range scene indices 60-80 are accepted** by the device but all show the same test image; nothing hidden there (see [DPS.md](DPS.md)).
- **After a power cycle the device reports defaults** (sound "off", play "off", no lighting scene) until something on it changes, even though it resumes playing music. It also drops the first writes for ~30 s after power-on and sometimes drops a turn-on sent shortly after power-off.

## Where the names and artwork came from
The scene names, categories and icons are taken from the panel the Smart Life app caches on the
phone. `build_catalogue.py` / `build_lighting.py` parse it; the panel itself is not committed.
