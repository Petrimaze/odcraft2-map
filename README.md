# odcraft2-map

Онлайн-карта Minecraft-сервера **odcraft2** (Towny). Обновляется автоматически.

## Как устроено

Свой сервер не нужен — весь конвейер на GitHub:

1. **Плагин [squaremap](https://modrinth.com/plugin/squaremap)** на игровом сервере рендерит карту в тайлы (инкрементально, TPS не ест).
2. **GitHub Actions** ([`update-map.yml`](.github/workflows/update-map.yml)) по расписанию (каждые 6 часов) и по кнопке:
   - выкачивает тайлы + вьювер с сервера через [exaroton files API](https://developers.exaroton.com/) ([`build-site.sh`](scripts/build-site.sh));
   - генерирует границы городов из данных Towny ([`gen-towns.py`](scripts/gen-towns.py) → `towns.json`);
   - публикует на GitHub Pages.
3. **GitHub Pages** раздаёт готовую карту.

Тайлы **не** хранятся в репозитории — каждый прогон берёт свежие с сервера и публикует как артефакт Pages. История git остаётся чистой.

## Запустить вручную

Вкладка **Actions → Обновить карту → Run workflow**.

## Секрет

`EXAROTON_TOKEN` — токен exaroton (Settings → Secrets and variables → Actions). В коде токена нет.
