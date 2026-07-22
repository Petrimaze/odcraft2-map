#!/usr/bin/env python3
"""Впечатывает панель навигации в вьювер squaremap и правит настройки.

  1) копирует nav.js / nav.css в собранный сайт;
  2) подключает их в index.html (link в head, script перед </body>);
  3) выключает player_tracker в per-world settings.json — на статичной карте
     он показывал бы ЗАМОРОЖЕННЫХ игроков (снимок на момент выкачки), это врёт;
  4) проставляет осмысленный <title>.
"""
import json, os, pathlib, shutil, sys

site = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
here = pathlib.Path(__file__).parent

# 1) файлы панели и бейджа
for f in ("nav.js", "nav.css", "online.js"):
    shutil.copy(here / f, site / f)

# 2) index.html
idx = site / "index.html"
html = idx.read_text(encoding="utf-8")
if "nav.css" not in html:
    html = html.replace("</head>", '  <link rel="stylesheet" href="./nav.css">\n</head>', 1)
if "nav.js" not in html:
    html = html.replace("</body>", '  <script src="./nav.js"></script>\n</body>', 1)
if "online.js" not in html:
    html = html.replace("</body>", '  <script src="./online.js"></script>\n</body>', 1)
html = html.replace("<title></title>", "<title>Карта odcraft2</title>", 1)
idx.write_text(html, encoding="utf-8")

# 3) выключить замороженный player_tracker
for st in site.glob("tiles/*/settings.json"):
    try:
        d = json.loads(st.read_text(encoding="utf-8"))
    except Exception:
        continue
    if isinstance(d, dict) and isinstance(d.get("player_tracker"), dict):
        d["player_tracker"]["enabled"] = False
        st.write_text(json.dumps(d), encoding="utf-8")

print("overlay: панель навигации подключена, player_tracker выключен")
