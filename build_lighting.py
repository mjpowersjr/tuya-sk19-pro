"""Extract lighting scenes (DP 121 colour_no) and UI icons from the cached panel."""
import json, re, shutil, pathlib
R = pathlib.Path("panel/C14A828CC956773B7094719D53B2F2D1/Resources/1.0.1_4srF3mfXjetJpYAH")
s = (R / "main.js").read_text(encoding="utf8")
var = dict(re.findall(r'\b([A-Za-z_$][\w$]{1,4})="/_assets/([^"]+\.png)"', s))
lang = dict(re.findall(r'(\w+):"([^"]*)"', s[s.find('icelandBlue:"'):s.find('icelandBlue:"') + 700]))
scenes = re.search(r"T=\[(\{id:0,nameKey:.*?\})\],k=function", s).group(1)
out = pathlib.Path("projections"); out.mkdir(exist_ok=True)
rows = []
for sid, key, icon in re.findall(r'\{id:(\d+),nameKey:"(\w+)",icon:([\w$]+)\}', scenes):
    src = R / "_assets" / var[icon]
    dst = f"light_{int(sid):02d}_{key}.png"
    shutil.copyfile(src, out / dst)
    rows.append({"code": int(sid), "dp121": int(sid), "key": key, "name": lang[key], "image": f"projections/{dst}"})
json.dump(rows, open("lighting_scenes.json", "w"), indent=2)
ui = {}
for name in ["m_yuzhou", "my_yuzhou", "m_ziran", "my_ziran", "m_qingxu", "my_qingxu", "m_jieri", "my_jieri",
             "pause", "single_cycle", "shuffleImg", "sequentialPlaybackImg", "singleTuneCirculationImg", "lanya"]:
    f = next(R.joinpath("_assets").glob(f"{name}-*.png"), None)
    if f: shutil.copyfile(f, out / f"ui_{name}.png"); ui[name] = f"projections/ui_{name}.png"
json.dump(ui, open("ui_icons.json", "w"), indent=2)
print(json.dumps(rows, indent=1)); print(sorted(ui))
