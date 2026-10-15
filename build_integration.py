"""Build custom_components/sk19_pro assets from the catalogues (run after build_catalogue/build_lighting/gen_ha_config)."""
import json, pathlib, shutil
from PIL import Image

D = pathlib.Path("custom_components/sk19_pro")
img = D / "img"; img.mkdir(parents=True, exist_ok=True)

def shrink(src, dst, px=96):
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGB", im.size, (24, 28, 40)); bg.paste(im, mask=im.split()[3])
    bg.resize((px, px), Image.LANCZOS).save(dst, "JPEG", quality=70, optimize=True)

proj = json.load(open("projections.json"))
light = json.load(open("lighting_scenes.json"))
ui = json.load(open("ui_icons.json"))
cat = {"projections": [], "lighting": [], "ui": {}, "categories": []}
for c, key in [("Universe", "yuzhou"), ("Natural", "ziran"), ("Animal", "qingxu"), ("Festival", "jieri")]:
    cat["categories"].append({"name": c, "icon": f"img/ui_m_{key}.jpg", "icon_active": f"img/ui_my_{key}.jpg"})
for p in proj:
    n = pathlib.Path(p["image"]).stem + ".jpg"; shrink(p["image"], img / n)
    cat["projections"].append({"code": p["code"], "name": p["name"], "category": p["category"], "image": f"img/{n}"})
for l in light:
    n = pathlib.Path(l["image"]).stem + ".jpg"; shrink(l["image"], img / n)
    cat["lighting"].append({"code": l["code"], "name": l["name"], "image": f"img/{n}"})
for k, v in ui.items():
    n = f"ui_{k}.jpg"; shrink(v, img / n, 72); cat["ui"][k] = f"img/{n}"
json.dump(cat, open(D / "catalogue.json", "w"), indent=1)
shutil.copyfile("ha/sk19_pro_projector.yaml", D / "tuya_local_devices/sk19_pro_projector.yaml")
print(len(cat["projections"]), "projections,", len(cat["lighting"]), "lighting,", len(list(img.iterdir())), "images")
