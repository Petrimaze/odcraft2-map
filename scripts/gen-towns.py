#!/usr/bin/env python3
"""Границы городов Towny -> GeoJSON (в игровых блок-координатах).

Тянет папки towns/ и townblocks/ у Towny одним ZIP через exaroton files API,
связывает чанки с городами и выдаёт FeatureCollection в stdout:
каждый занятый чанк = квадрат 16x16, свойства несут имя города, мэра и цвет.
Оверлей (inject-overlay.py) рисует это поверх карты squaremap.
"""
import io, json, os, re, sys, urllib.request, zipfile, colorsys, hashlib

API = "https://api.exaroton.com/v1/servers"
SERVER = os.environ.get("EXAROTON_SERVER", "bTx5yEMdtzk9sHv0")
TOKEN = os.environ["EXAROTON_TOKEN"]
WORLD = "world"  # Towny держит клеймы только в оверворлде (ад/край выключены)


def fetch_zip(path):
    req = urllib.request.Request(f"{API}/{SERVER}/files/data/{path}",
                                 headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": "odcraft2-map/1"})
    data = urllib.request.urlopen(req, timeout=60).read()
    return zipfile.ZipFile(io.BytesIO(data))


def town_color(name):
    h = int(hashlib.md5(name.encode()).hexdigest(), 16)
    hue = (h % 360) / 360.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.65, 0.9)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def parse_kv(text):
    d = {}
    for line in text.splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            d[k.strip()] = v.strip()
    return d


# --- 1. города: uuid -> (имя, мэр) --------------------------------------
towns = {}          # ключ: и uuid, и имя (townblock может ссылаться по любому)
try:
    zt = fetch_zip("plugins/Towny/data/towns")
    for n in zt.namelist():
        if not n.endswith(".txt"):
            continue
        kv = parse_kv(zt.read(n).decode("utf-8", "replace"))
        name = kv.get("name")
        if not name:
            continue
        rec = {"name": name, "mayor": kv.get("mayorName", ""), "color": town_color(name)}
        if kv.get("uuid"):
            towns[kv["uuid"].lower()] = rec
        towns[name.lower()] = rec
except Exception as e:
    print(f"warn: towns недоступны: {e}", file=sys.stderr)

# --- 2. чанки: townblocks/<world>/<x>_<z>_16.data -----------------------
features = []
try:
    zb = fetch_zip("plugins/Towny/data/townblocks")
    for n in zb.namelist():
        m = re.search(rf"townblocks/{WORLD}/(-?\d+)_(-?\d+)_\d+\.data$", n)
        if not m:
            continue
        cx, cz = int(m.group(1)), int(m.group(2))
        kv = parse_kv(zb.read(n).decode("utf-8", "replace"))
        ref = (kv.get("town") or "").lower()
        town = towns.get(ref, {"name": ref or "?", "mayor": "", "color": "#888888"})
        x0, z0 = cx * 16, cz * 16
        features.append({
            "type": "Feature",
            "properties": {"town": town["name"], "mayor": town["mayor"], "color": town["color"]},
            "geometry": {"type": "Polygon", "coordinates": [[
                [x0, z0], [x0 + 16, z0], [x0 + 16, z0 + 16], [x0, z0 + 16], [x0, z0]
            ]]},
        })
except Exception as e:
    print(f"warn: townblocks недоступны: {e}", file=sys.stderr)

print(json.dumps({"type": "FeatureCollection",
                  "town_count": len({f["properties"]["town"] for f in features}),
                  "features": features}, ensure_ascii=False))
