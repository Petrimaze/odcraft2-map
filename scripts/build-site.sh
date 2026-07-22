#!/usr/bin/env bash
# Собирает статический сайт карты в _site/:
#  1) выкачивает готовый веб-вьювер squaremap (тайлы + Leaflet) с игрового сервера через exaroton API
#  2) генерирует границы городов из данных Towny (towns.json — данные для будущего оверлея)
set -euo pipefail

API="https://api.exaroton.com/v1/servers"
SERVER="${EXAROTON_SERVER:-bTx5yEMdtzk9sHv0}"
AUTH="Authorization: Bearer ${EXAROTON_TOKEN:?нужен EXAROTON_TOKEN}"

rm -rf _site web.zip unz
mkdir -p _site unz

echo "::group::Выкачка вьювера squaremap"
# Директория через files API отдаётся одним ZIP
curl -sfS -H "$AUTH" "$API/$SERVER/files/data/plugins/squaremap/web" -o web.zip
unzip -q web.zip -d unz
# Найти каталог с index.html (в архиве путь может быть 'web/...' или сразу содержимое)
IDX="$(find unz -name index.html | head -1)"
[ -n "$IDX" ] || { echo "index.html не найден в архиве"; exit 1; }
cp -r "$(dirname "$IDX")"/. _site/
echo "  вьювер + тайлы из: $(dirname "$IDX")"
du -sh _site | awk '{print "  размер сайта:", $1}'
echo "::endgroup::"

echo "::group::Границы городов из Towny"
if python3 scripts/gen-towns.py > _site/towns.json; then
  python3 -c "import json;d=json.load(open('_site/towns.json'));print(f\"  городов: {d['town_count']}, чанков: {len(d['features'])}\")"
else
  echo "  towns.json пропущен (Towny недоступен) — карта соберётся без границ"
  echo '{"type":"FeatureCollection","town_count":0,"features":[]}' > _site/towns.json
fi
echo "::endgroup::"

# .nojekyll — чтобы GitHub Pages не прогонял сайт через Jekyll (иначе _-папки и служебки могут пропасть)
touch _site/.nojekyll
echo "Готово: _site/"
