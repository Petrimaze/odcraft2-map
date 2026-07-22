// Бейдж "онлайн: N" — кто сейчас на сервере (ники, без позиций на карте).
// Данные пишет лёгкий workflow update-online.yml в ветку live каждые ~10 мин;
// здесь опрашиваем raw-файл. Живых ПОЗИЦИЙ игроков на статике быть не может —
// exaroton API отдаёт только список ников и count.
(function () {
  "use strict";
  var URL = "https://raw.githubusercontent.com/Petrimaze/odcraft2-map/live/online.json";
  var POLL = 60000; // опрос раз в минуту (сам файл обновляется реже, ~10 мин)

  var badge = document.createElement("div");
  badge.id = "online-badge";
  badge.innerHTML = '<span class="ob-dot"></span><span class="ob-text">…</span>';
  document.body.appendChild(badge);
  var text = badge.querySelector(".ob-text");

  function render(d) {
    if (!d || d.status !== "online") {
      badge.classList.remove("ob-live");
      text.textContent = "сервер спит";
      return;
    }
    badge.classList.add("ob-live");
    var n = d.count || 0;
    var names = (d.players || []).join(", ");
    text.innerHTML = "онлайн: <b>" + n + "</b>" +
      (names ? ' <span class="ob-names">' + names.replace(/</g, "&lt;") + "</span>" : "");
  }

  function poll() {
    fetch(URL + "?t=" + Date.now(), { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(render)
      .catch(function () { badge.classList.remove("ob-live"); text.textContent = "нет данных"; });
  }

  poll();
  setInterval(poll, POLL);
})();
