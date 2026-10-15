# Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| "SK19 entities not found" in the card | The device isn't added in **Tuya Local** yet, or its entities have a different prefix. Add it, choose the *Projector light* config. |
| Tuya Local doesn't offer *Projector light* | The device config wasn't installed or Home Assistant hasn't restarted since. Restart HA (or reload the Tuya Local entry). |
| Entities "unavailable" | Wrong host/key, the device changed IP (give it a DHCP reservation), or another client holds its single LAN connection. Tuya Local → **Reconfigure**. |
| Key stopped working | Re-pairing the device in the app rotates the local key. Fetch the new one and reconfigure. |
| Dashboard shows "Configuration error" / "Custom element doesn't exist" on a cold start | Fixed in 0.2.2+ (re-registration of the element). Make sure the integration is up to date and HA was restarted. |
| Card didn't update after a HACS update | The script's cache-bust version is computed at startup. **Restart Home Assistant** after updating. |
| Two "Projector" sidebar entries | Hide one under your profile; the integration hides its own when a dashboard with URL `sk19-dashboard` exists. |
| Timer reaches zero but the projector stays on | Check `sk19_pro.sleep_timer` → `last_run` (`result`, `attempts`). `failed` means the device never confirmed power-off; the log has a warning. |
| Brightness/volume low after a timer | Levels are re-applied at the next power-on; if the device was off for a long time press the slider once. |
| Phone shows the card but the colour wheel is small | By design: on short screens the wheel shrinks (min 140 px) so all lighting scenes fit. |

Logs: *Settings → System → Logs*. Useful filters: `sk19_pro`, `tuya_local`.
