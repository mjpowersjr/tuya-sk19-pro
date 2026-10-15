# Notice: what the MIT licence does and does not cover

The [MIT licence](LICENSE) applies to the **code and documentation written for this project**.
The items below are **not** covered by it.

## Third-party artwork (not licensed under MIT)

| Files | What it is | Status |
|---|---|---|
| `custom_components/sk19_pro/img/*` | Scene artwork and UI glyphs, downsized copies of the images shipped in the device's Smart Life / Tuya app panel | Property of the device's maker / app vendor. **No licence is granted by this repository.** Included only so the card can show the same scene images as the app, for use with the matching hardware. |
| `custom_components/sk19_pro/catalogue.json`, `projections.json`, `lighting_scenes.json` | Scene names and categories as shown in the app | Vendor strings; the file structure and tooling are MIT, the names are the vendor's. |
| `docs/img/product.jpg` | Product photo from a retail listing | Property of the seller. Shown only to help identify the device. |
| `docs/img/card-*.png` | Screenshots of this project's card | The screenshots are ours; the scene thumbnails inside them are the vendor artwork above. |

If you fork or redistribute this project, you are responsible for the third-party items above:
replace or remove them unless you have your own right to use them. The card works without
the images (it falls back to names), and `build_catalogue.py` / `build_integration.py` rebuild
them from your own copy of the app panel.

If you are a rights holder and want something removed, please open an issue and it will be
taken down promptly.

## Original assets (MIT)

`custom_components/sk19_pro/brand/*` (the integration icon and logo) and the card's CSS/JS were
created for this project and are covered by the MIT licence.

## Not bundled

[Tuya Local](https://github.com/make-all/tuya-local) (MIT, by @make-all) is a separate integration
that users install themselves; no code from it is vendored here. This project is not affiliated
with Tuya or the device's maker.
