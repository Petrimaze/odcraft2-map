// Панель навигации по городам odcraft2.
// Читает towns-nav.json и строит список: клик по городу -> перелёт карты
// через hash-навигацию squaremap (#world;renderer;x,z;zoom).
(function () {
  "use strict";
  var WORLD = "minecraft_overworld";
  var ZOOM = 3;

  function flyTo(x, z) {
    // squaremap центрируется по query-параметрам при загрузке;
    // смена location.search перезагружает страницу — карта откроется на городе.
    location.search =
      "?world=" + WORLD + "&zoom=" + ZOOM + "&x=" + Math.round(x) + "&z=" + Math.round(z);
  }

  function build(towns) {
    var panel = document.createElement("div");
    panel.id = "town-nav";
    panel.innerHTML =
      '<div class="tn-head">Города <span class="tn-count"></span>' +
      '<button class="tn-toggle" title="Свернуть">–</button></div>' +
      '<div class="tn-list"></div>';
    document.body.appendChild(panel);

    var list = panel.querySelector(".tn-list");
    panel.querySelector(".tn-count").textContent = "(" + towns.length + ")";

    if (!towns.length) {
      list.innerHTML = '<div class="tn-empty">Городов пока нет</div>';
    }
    towns.forEach(function (t) {
      var row = document.createElement("button");
      row.className = "tn-row";
      row.innerHTML =
        '<span class="tn-dot" style="background:' + t.color + '"></span>' +
        '<span class="tn-name"></span>' +
        '<span class="tn-plots">' + t.plots + "</span>";
      row.querySelector(".tn-name").textContent = t.name;
      row.title = (t.mayor ? "мэр: " + t.mayor + " · " : "") + t.plots + " участк.";
      row.addEventListener("click", function () { flyTo(t.x, t.z); });
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
    fetch("towns-nav.json", { cache: "no-store" })
      .then(function (r) { return r.json(); })
      .then(function (d) { build((d && d.towns) || []); })
      .catch(function () { build([]); });
  }

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", load);
  else load();
})();
