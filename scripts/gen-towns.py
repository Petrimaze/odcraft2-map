#!/usr/bin/env python3
"""Данные Towny -> нативные маркеры squaremap + список городов для навигации.

Тянет towns/ и townblocks/ у Towny одним ZIP через exaroton files API, связывает
чанки с городами и пишет ДВА файла (пути передаются аргументами):
  1) markers.json  — формат squaremap: каждый занятый чанк = прямоугольник
                     цвета города с тултипом. Вьювер сам проецирует координаты.
  2) towns-nav.json — список городов с центром (для панели навигации: клик -> перелёт).
"""
import io, json, os, re, sys, urllib.request, zipfile, colorsys, hashlib

API = "https://api.exaroton.com/v1/servers"
SERVER = os.environ.get("EXAROTON_SERVER", "bTx5yEMdtzk9sHv0")
TOKEN = os.environ["EXAROTON_TOKEN"]
WORLD = "world"  # клеймы только в оверворлде (ад/край выключены в Towny)

MARKERS_OUT = sys.argv[1] if len(sys.argv) > 1 else "markers.json"
NAV_OUT = sys.argv[2] if len(sys.argv) > 2 else "towns-nav.json"


def fetch_zip(path):
    req = urllib.request.Request(f"{API}/{SERVER}/files/data/{path}",
                                 headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": "odcraft2-map/1"})
    return zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(req, timeout=60).read()))


def town_color(name):
    h = int(hashlib.md5(name.encode()).hexdigest(), 16)
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360.0, 0.70, 0.90)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def parse_kv(text):
    d = {}
    for line in text.splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            d[k.strip()] = v.strip()
    return d


# --- города: ref(uuid|имя) -> запись --------------------------------------
towns = {}
try:
    zt = fetch_zip("plugins/Towny/data/towns")
    for n in zt.namelist():
        if not n.endswith(".txt"):
            continue
        kv = parse_kv(zt.read(n).decode("utf-8", "replace"))
        name = kv.get("name")
        if not name:
            continue
        rec = {"name": name, "mayor": kv.get("mayorName", ""), "color": town_color(name), "chunks": []}
        if kv.get("uuid"):
            towns[kv["uuid"].lower()] = rec
        towns[name.lower()] = rec
except Exception as e:
    print(f"warn: towns недоступны: {e}", file=sys.stderr)

# --- чанки -> города ------------------------------------------------------
by_town = {}  # name -> town rec (уникальные)
try:
    zb = fetch_zip("plugins/Towny/data/townblocks")
    for n in zb.namelist():
        m = re.search(rf"townblocks/{WORLD}/(-?\d+)_(-?\d+)_\d+\.data$", n)
        if not m:
            continue
        cx, cz = int(m.group(1)), int(m.group(2))
        kv = parse_kv(zb.read(n).decode("utf-8", "replace"))
        ref = (kv.get("town") or "").lower()
        town = towns.get(ref)
        if not town:
            town = {"name": ref or "?", "mayor": "", "color": "#888888", "chunks": []}
        town["chunks"].append((cx, cz))
        by_town[town["name"]] = town
except Exception as e:
    print(f"warn: townblocks недоступны: {e}", file=sys.stderr)

# --- markers.json (squaremap): прямоугольник на чанк ----------------------
markers = []
for town in by_town.values():
    for cx, cz in town["chunks"]:
        x0, z0 = cx * 16, cz * 16
        markers.append({
            "type": "rectangle",
            "points": [{"x": x0, "z": z0}, {"x": x0 + 16, "z": z0 + 16}],
            "color": town["color"], "weight": 1, "opacity": 0.9,
            "fillColor": town["color"], "fillOpacity": 0.28,
            "tooltip": {"content": f"<b>{town['name']}</b>" + (f"<br/>мэр: {town['mayor']}" if town['mayor'] else ""),
                        "sticky": True},
        })

layers = [{
    "id": "towny", "name": "Города", "control": True, "hide": False,
    "order": 10, "z_index": 999, "pane": "", "css": "",
    "markers": markers,
}]
with open(MARKERS_OUT, "w", encoding="utf-8") as f:
    json.dump(layers, f, ensure_ascii=False)

# --- towns-nav.json: список городов с центром (для навигации) -------------
nav = []
for town in sorted(by_town.values(), key=lambda t: -len(t["chunks"])):
    if not town["chunks"]:
        continue
    xs = [c[0] for c in town["chunks"]]
    zs = [c[1] for c in town["chunks"]]
    cx = (min(xs) + max(xs) + 1) / 2 * 16
    cz = (min(zs) + max(zs) + 1) / 2 * 16
    nav.append({"name": town["name"], "mayor": town["mayor"], "color": town["color"],
                "plots": len(town["chunks"]), "x": round(cx), "z": round(cz)})
with open(NAV_OUT, "w", encoding="utf-8") as f:
    json.dump({"towns": nav}, f, ensure_ascii=False)

print(f"городов: {len(nav)}, чанков: {len(markers)}", file=sys.stderr)
