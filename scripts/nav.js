// Панель навигации odcraft2: переключатель миров + список городов.
// squaremap центрируется по query-параметрам при загрузке; клик меняет
// location.search (страница перезагружается, карта открывается где нужно).
(function () {
  "use strict";
  var ZOOM = 3;
  var WORLD_NAMES = {
    "minecraft_overworld": "Обычный мир",
    "minecraft_the_nether": "Ад",
    "minecraft_the_end": "Край",
  };

  function currentWorld() {
    var m = /[?&]world=([^&]+)/.exec(location.search);
    return m ? decodeURIComponent(m[1]) : "minecraft_overworld";
  }
  function goWorld(world) {
    location.search = "?world=" + world + "&zoom=" + ZOOM;
  }
  function flyTo(world, x, z) {
    location.search = "?world=" + world + "&zoom=" + ZOOM +
      "&x=" + Math.round(x) + "&z=" + Math.round(z);
  }

  function build(worlds, towns) {
    var world = currentWorld();
    var panel = document.createElement("div");
    panel.id = "town-nav";
    panel.innerHTML =
      '<div class="tn-head">Карта <button class="tn-toggle" title="Свернуть">–</button></div>' +
      '<div class="tn-body">' +
        '<div class="tn-worlds"></div>' +
        '<div class="tn-sub">Города <span class="tn-count"></span></div>' +
        '<div class="tn-list"></div>' +
      '</div>';
    document.body.appendChild(panel);

    // переключатель миров
    var wrap = panel.querySelector(".tn-worlds");
    worlds.forEach(function (w) {
      var b = document.createElement("button");
      b.className = "tn-world" + (w === world ? " tn-active" : "");
      b.textContent = WORLD_NAMES[w] || w;
      b.addEventListener("click", function () { if (w !== world) goWorld(w); });
      wrap.appendChild(b);
    });

    // список городов
    var list = panel.querySelector(".tn-list");
    panel.querySelector(".tn-count").textContent = "(" + towns.length + ")";
    if (!towns.length) list.innerHTML = '<div class="tn-empty">Городов пока нет</div>';
    towns.forEach(function (t) {
      var row = document.createElement("button");
      row.className = "tn-row";
      row.innerHTML =
        '<span class="tn-dot" style="background:' + t.color + '"></span>' +
        '<span class="tn-name"></span><span class="tn-plots">' + t.plots + "</span>";
      row.querySelector(".tn-name").textContent = t.name;
      row.title = (t.mayor ? "мэр: " + t.mayor + " · " : "") + t.plots + " участк.";
      // города только в оверворлде -> клик переносит и в оверворлд
      row.addEventListener("click", function () { flyTo("minecraft_overworld", t.x, t.z); });
      list.appendChild(row);
    });

    var collapsed = false;
    panel.querySelector(".tn-toggle").addEventListener("click", function () {
      collapsed = !collapsed;
      panel.classList.toggle("tn-collapsed", collapsed);
      this.textContent = collapsed ? "+" : "–";
    });
  }

  function load() {
    Promise.all([
      fetch("tiles/settings.json", { cache: "no-store" }).then(function (r) { return r.json(); })
        .then(function (s) { return (s.worlds || []).map(function (w) { return w.name; }); })
        .catch(function () { return ["minecraft_overworld"]; }),
      fetch("towns-nav.json", { cache: "no-store" }).then(function (r) { return r.json(); })
        .then(function (d) { return (d && d.towns) || []; }).catch(function () { return []; }),
    ]).then(function (res) { build(res[0], res[1]); });
  }

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", load);
  else load();
})();
