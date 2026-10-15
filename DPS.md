# SK19 Pro ("Smart 3D Video Projector Light") — Tuya data points

- Device ID `<device-id>`, product `a5enoboa4fnkicus`, category `xktyd`, model id `e1oekjec`
- LAN: `<device-ip>`, TCP 6668, **protocol 3.5**. Local key lives in the gitignored `sk19.toml`.
- Source: cloud "Query Things Data Model" + live local `status()`.

## Live values observed (2026-10-14)

| DP | code | observed |
|---|---|---|
| 20 | switch_led | true |
| 24 | colour_data | "00d003e80258" (HHHHSSSSVVVV hex, H 0-360, S/V 0-1000) |
| 52 | colour_switch | true |
| 105 | projection | true |
| 106 | pr_projection (brightness, 0-100) | 75 |
| 107 | voice_play (pause/play) | true |
| 108 | auido (sound on/off) | false |
| 109 | voice (volume 0-100) | 40 |
| 111 | bluetooth_connected | true |
| 112 | playback_order | sequence |
| 120 | bluetooth_status | connect |
| 121 | colour_no (0-20) | 6 |
| 122 | projection_data | "36" |

## Full DP list

| DP | code | type | notes |
|---|---|---|---|
| 20 | switch_led | bool | master power |
| 24 | colour_data | string | HSV colour |
| 51 | star_work_mode | enum manual/scene/music | |
| 52 | colour_switch | bool | |
| 53 | laser_switch | bool | "ambient light" switch |
| 54 | laser_bright | int 10-1000 | |
| 57 | star_control_data | raw | write-only live HSV + laser brightness |
| 58 | star_scene_data | raw | scene: colour units, laser units, motor on/speed |
| 101 | mcu_info | string | |
| 102 | bool | bool | "custom" |
| 103 | device_status | string | |
| 104 | rtc_timer | raw | |
| 105 | projection | bool | projection on/off |
| 106 | pr_projection | int 0-100 | projection brightness |
| 107 | voice_play | bool | pause/play |
| 108 | auido | bool | sound on/off |
| 109 | voice | int 0-100 | volume |
| 110 | ambient_lighting | raw | |
| 111 | bluetooth_connected | bool | bluetooth switch |
| 112 | playback_order | enum random/sequence/single_cycle | |
| 113 | custom_save | bool | |
| 114 | power_off_memory | bool | |
| 115 | ota_update | bool | |
| 116-119 | custom_mode1..4 | raw | playlist: `LL OO (idx id)...` LL=count, OO=01 sequential/00 random, then pairs of (order, projection number). Example from vendor: `0202011e0223` |
| 120 | bluetooth_status | enum disconnect/connect | |
| 121 | colour_no | int 0-20 | colour preset |
| 122 | projection_data | string | "projection playback data, ordered 0-80" -> projection index |
| 123 | alarm_no | int 0-20 | |
| 124 | my_favorited | raw | |
| 125 | bluetooth_control | enum next/previous | write-only |
| 126 | bluetooth_play | bool | |
| 127 | scheduled_onoff | int 0-255 | byte1 on/off, byte2 projection index |
| 128 | custom_play | enum other/favorite/custom_mode1-4 | |
| 129 | ringtone_no | int 0-20 | |

## Firmware (cloud "Get Update Information")

| Module | Version | Firmware key |
|---|---|---|
| Main Module (Wi-Fi/BT, type 0, channel 0) | 1.0.15 | (firmware key omitted) |
| MCU Module (type 9, channel 9) | 1.0.0 | (empty) |

No pending upgrade is reported for either module (upgrade_status 0).

## Takeaways

- No DP carries video/media data. "Videos" are ~81 built-in projections addressed by index 0-80
  (DP 122, custom_mode playlists, scheduled_onoff). Custom video is not exposed over the Tuya API.
- Untested ideas: write DP 122 values 0-80 to step through every built-in; build playlists via DP 116-119.
