#!/usr/bin/env bash
# Собирает статический сайт карты в _site/:
#  1) выкачивает готовый веб-вьювер squaremap (тайлы + Leaflet) с игрового сервера через exaroton API
#  2) генерирует границы городов (нативные маркеры squaremap) + список городов для навигации
#  3) впечатывает панель навигации, выключает замороженный player_tracker
set -euo pipefail

API="https://api.exaroton.com/v1/servers"
SERVER="${EXAROTON_SERVER:-bTx5yEMdtzk9sHv0}"
AUTH="Authorization: Bearer ${EXAROTON_TOKEN:?нужен EXAROTON_TOKEN}"

rm -rf _site web.zip unz
mkdir -p _site unz

echo "::group::Выкачка вьювера squaremap"
curl -sfS -H "$AUTH" "$API/$SERVER/files/data/plugins/squaremap/web" -o web.zip
unzip -q web.zip -d unz
IDX="$(find unz -name index.html | head -1)"
[ -n "$IDX" ] || { echo "index.html не найден в архиве"; exit 1; }
cp -r "$(dirname "$IDX")"/. _site/
du -sh _site | awk '{print "  размер сайта:", $1}'
echo "::endgroup::"

echo "::group::Границы городов + навигация из Towny"
mkdir -p _site/tiles/minecraft_overworld
if python3 scripts/gen-towns.py \
      _site/tiles/minecraft_overworld/markers.json \
      _site/towns-nav.json; then
  :
else
  echo "  Towny недоступен — карта соберётся без городов"
  echo '[]' > _site/tiles/minecraft_overworld/markers.json
  echo '{"towns":[]}' > _site/towns-nav.json
fi
echo "::endgroup::"

echo "::group::Панель навигации + настройки"
python3 scripts/inject-overlay.py _site
echo "::endgroup::"

touch _site/.nojekyll
echo "Готово: _site/"
