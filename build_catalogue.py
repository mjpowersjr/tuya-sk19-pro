import json, re, shutil, pathlib
R = pathlib.Path("panel/C14A828CC956773B7094719D53B2F2D1/Resources/1.0.1_4srF3mfXjetJpYAH")
s = (R / "main.js").read_text(encoding="utf8")
names = json.loads("[" + re.search(r'ens=\["(.*?)"\],enf=', s).group(1).join(['"', '"']) + "]") if False else \
        json.loads(re.search(r'ens=(\[.*?\]),enf=', s).group(1))
assets = {}
for p in (R / "_assets").iterdir():
    m = re.match(r"(\d+)\s+(.*)-[A-Z0-9]{8}\.png$", p.name)
    if m: assets[int(m.group(1))] = p
cats = [("Universe", 0, 30), ("Natural", 30, 14), ("Animal", 44, 12), ("Festival", 56, 4)]
out = pathlib.Path("projections"); out.mkdir(exist_ok=True)
rows = []
for cat, start, n in cats:
    for code in range(start, start + n):
        slug = re.sub(r"[^a-z0-9]+", "_", names[code].lower()).strip("_")
        img = f"{code:02d}_{slug}.png"
        shutil.copyfile(assets[code + 1], out / img)   # asset numbers are 1-based
        rows.append({"code": code, "dp122": str(code), "name": names[code],
                     "category": cat, "image": f"projections/{img}",
                     "app_asset": assets[code + 1].name})
json.dump(rows, open("projections.json", "w"), indent=2)
assert len(rows) == 60 == len(names)
print(len(rows), "projections;", len(list(out.iterdir())), "images")
for r in rows[:3] + rows[28:32] + rows[-3:]: print(r["code"], r["category"], r["name"], "<-", r["app_asset"])
