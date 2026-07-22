#!/usr/bin/env python3
"""Статус сервера odcraft2 -> online.json (для бейджа на карте).

exaroton API отдаёт статус, список ников онлайн и count — но НЕ позиции.
Поэтому на карте показываем только счётчик и ники, без точек игроков.
"""
import json, os, time, urllib.request

TOKEN = os.environ["EXAROTON_TOKEN"]
SERVER = os.environ.get("EXAROTON_SERVER", "bTx5yEMdtzk9sHv0")

req = urllib.request.Request(f"https://api.exaroton.com/v1/servers/{SERVER}/",
                             headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": "odcraft2-map/1"})
d = json.load(urllib.request.urlopen(req, timeout=30))["data"]

online = d.get("status") == 1  # 1 = ONLINE
players = d.get("players", {}) if online else {}
out = {
    "status": "online" if online else "offline",
    "count": players.get("count", 0),
    "max": players.get("max", 0),
    "players": players.get("list", []),
    "ts": int(time.time()),
}
print(json.dumps(out, ensure_ascii=False))
