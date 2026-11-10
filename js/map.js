(function (root) {
  "use strict";

  var STATUS_CHAIR = "chair listed in Nov 7 roster";
  var STATUS_VACANT = "labeled vacant in Nov 7 roster";
  var STATUS_UNKNOWN = "unverified/unknown";
  var CHAIR_FILL = "#0d0572";
  var VACANT_FILL = "#9a3412";
  var UNKNOWN_FILL = "#5c5766";

  if (!root.document || !root.document.getElementById || !root.L) return;

  var doc = root.document;
  var mapEl = doc.getElementById("precinct-map");
  var frame = doc.getElementById("map-frame");
  var activateBtn = doc.getElementById("map-activate");
  var doneBtn = doc.getElementById("map-done");
  var searchForm = doc.getElementById("map-search");
  var searchInput = doc.getElementById("map-precinct");
  var searchStatus = doc.getElementById("map-search-status");
  if (!mapEl || !frame) return;

  var statusByPrecinct = {};
  Array.prototype.forEach.call(doc.querySelectorAll("#precinct-directory tbody tr[data-precinct]"), function (row) {
    statusByPrecinct[row.getAttribute("data-precinct")] = row.getAttribute("data-status");
  });

  var map = root.L.map(mapEl, {
    scrollWheelZoom: false,
    keyboard: true,
    zoomControl: true,
    zoomSnap: 0
  });
  mapEl.setAttribute("role", "region");
  mapEl.setAttribute("aria-label", "Map of the 67 voting precincts in Commissioner Precinct 4");
  if (doc.getElementById("map-caveat")) mapEl.setAttribute("aria-describedby", "map-caveat");

  root.L.tileLayer("https://tile.openstreetmap.de/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
  }).addTo(map);
  map.setView([33.15736, -97.23164], 10);

  var layersById = {};
  var selectedId = null;
  var loaded = false;
  var pendingShow = null;
  var mapActivated = false;
  var precinctGroup = null;
  var showingAll = true;
  var coarse = root.matchMedia("(pointer: coarse)");

  function setStatus(text) {
    if (searchStatus) searchStatus.textContent = text;
  }

  function fillFor(status) {
    if (status === STATUS_VACANT) return { color: VACANT_FILL, opacity: 0.62 };
    if (status === STATUS_CHAIR) return { color: CHAIR_FILL, opacity: 0.5 };
    return { color: UNKNOWN_FILL, opacity: 0.45 };
  }

  function styleFor(id, selected) {
    var fill = fillFor(statusByPrecinct[id] || STATUS_UNKNOWN);
    return {
      color: selected ? "#1a1720" : "#ffffff",
      weight: selected ? 3.5 : 1.25,
      fillColor: fill.color,
      fillOpacity: selected ? Math.min(fill.opacity + 0.18, 0.9) : fill.opacity,
      opacity: 1
    };
  }

  function eachElement(layer, fn) {
    var el = layer.getElement && layer.getElement();
    if (el) fn(el);
    if (!el && layer.eachLayer) {
      layer.eachLayer(function (child) { eachElement(child, fn); });
    }
  }

  function applyStyles() {
    Object.keys(layersById).forEach(function (id) {
      var layer = layersById[id];
      layer.setStyle(styleFor(id, id === selectedId));
      eachElement(layer, function (el) {
        el.setAttribute("aria-pressed", id === selectedId ? "true" : "false");
      });
    });
  }

  function prefersReducedMotion() {
    return root.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function highlightRow(id) {
    var row = doc.getElementById("precinct-" + id);
    if (!row) return;
    Array.prototype.forEach.call(doc.querySelectorAll("tr.is-map-target"), function (other) {
      other.classList.remove("is-map-target");
    });
    if (row.hidden) {
      var precinctInput = doc.getElementById("directory-precinct");
      var statusInput = doc.getElementById("directory-status");
      if (statusInput) statusInput.value = "";
      if (precinctInput) {
        precinctInput.value = id;
        precinctInput.dispatchEvent(new Event("input"));
      }
      row.hidden = false;
    }
    row.classList.add("is-map-target");
    row.scrollIntoView({ behavior: prefersReducedMotion() ? "auto" : "smooth", block: "center" });
  }

  function applyGestureMode() {
    if (!activateBtn || !doneBtn) return;
    if (!coarse.matches) {
      activateBtn.hidden = true;
      doneBtn.hidden = true;
      frame.classList.remove("is-inert");
      map.dragging.enable();
      if (map.touchZoom) map.touchZoom.enable();
      return;
    }
    if (mapActivated) {
      activateBtn.hidden = true;
      doneBtn.hidden = false;
      frame.classList.remove("is-inert");
      map.dragging.enable();
      if (map.touchZoom) map.touchZoom.enable();
      return;
    }
    activateBtn.hidden = false;
    doneBtn.hidden = true;
    frame.classList.add("is-inert");
    map.dragging.disable();
    map.scrollWheelZoom.disable();
    if (map.touchZoom) map.touchZoom.disable();
  }

  function activateMap() {
    mapActivated = true;
    applyGestureMode();
  }

  function deactivateMap() {
    mapActivated = false;
    applyGestureMode();
  }

  function fitAllPrecincts() {
    if (!precinctGroup) return;
    map.invalidateSize();
    map.fitBounds(precinctGroup.getBounds(), { padding: [24, 24], animate: false });
    showingAll = true;
  }

  function showOnMap(id, scrollMap) {
    if (!loaded) {
      pendingShow = { id: id, scrollMap: scrollMap };
      setStatus("The map is still loading.");
      return;
    }
    var layer = layersById[id];
    if (!layer) {
      setStatus("No precinct matches " + id + ".");
      return;
    }
    selectedId = id;
    showingAll = false;
    applyStyles();
    if (coarse.matches) activateMap();
    var status = statusByPrecinct[id] || STATUS_UNKNOWN;
    layer.openTooltip();
    map.fitBounds(layer.getBounds(), {
      padding: [32, 32],
      maxZoom: 16,
      animate: !prefersReducedMotion()
    });
    setStatus("Showing precinct " + id + " on the map. " + status + ".");
    if (scrollMap) {
      frame.scrollIntoView({ behavior: prefersReducedMotion() ? "auto" : "smooth", block: "center" });
    }
  }

  function findMatch(query) {
    if (layersById[query]) return { id: query };
    var hits = Object.keys(layersById).filter(function (id) { return id.indexOf(query) !== -1; });
    if (hits.length === 1) return { id: hits[0] };
    return { hits: hits };
  }

  function runSearch(allowPartial) {
    var query = String(searchInput && searchInput.value || "").replace(/\s+/g, "");
    if (!loaded) {
      pendingShow = { id: query, scrollMap: false, search: true };
      setStatus("The map is still loading.");
      return;
    }
    if (!query) {
      setStatus("Type a precinct number.");
      return;
    }
    var match = findMatch(query);
    if (match.id && (allowPartial || match.id === query)) {
      if (searchInput) searchInput.value = match.id;
      showOnMap(match.id, false);
      return;
    }
    if (!match.hits || !match.hits.length) {
      setStatus("No precinct matches " + query + ".");
      return;
    }
    if (!allowPartial) return;
    setStatus(match.hits.length + " precincts match " + query + ". Type more of the number.");
  }

  function wireElement(layer, id, status) {
    eachElement(layer, function (el) {
      if (el.getAttribute("data-wired") === "1") return;
      el.setAttribute("data-wired", "1");
      el.classList.add("precinct-path");
      el.setAttribute("data-precinct", id);
      el.setAttribute("tabindex", "0");
      el.setAttribute("role", "button");
      el.setAttribute("aria-pressed", "false");
      el.setAttribute("aria-label", "Precinct " + id + ", " + status + ". Highlight its directory row.");
      el.addEventListener("keydown", function (event) {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        event.stopPropagation();
        selectedId = id;
        applyStyles();
        layer.openTooltip();
        highlightRow(id);
      });
      el.addEventListener("focus", function () {
        selectedId = id;
        applyStyles();
        layer.openTooltip();
      });
    });
  }

  function onEachFeature(feature, layer) {
    var id = String(feature.properties.precinct);
    var status = statusByPrecinct[id] || STATUS_UNKNOWN;
    layersById[id] = layer;
    layer.bindTooltip("Precinct " + id + ". " + status, {
      sticky: true,
      opacity: 1,
      className: "precinct-tip"
    });
    layer.on("click", function () {
      selectedId = id;
      applyStyles();
      layer.openTooltip();
      highlightRow(id);
    });
    layer.on("add", function () { wireElement(layer, id, status); });
  }

  function bboxArea(feature) {
    var minX = Infinity;
    var minY = Infinity;
    var maxX = -Infinity;
    var maxY = -Infinity;
    function walk(coords) {
      if (typeof coords[0] === "number") {
        if (coords[0] < minX) minX = coords[0];
        if (coords[1] < minY) minY = coords[1];
        if (coords[0] > maxX) maxX = coords[0];
        if (coords[1] > maxY) maxY = coords[1];
        return;
      }
      for (var i = 0; i < coords.length; i += 1) walk(coords[i]);
    }
    walk(feature.geometry.coordinates);
    return (maxX - minX) * (maxY - minY);
  }

  if (activateBtn) {
    var tapStart = null;
    var activateArmed = false;
    activateBtn.addEventListener("pointerdown", function (event) {
      tapStart = { x: event.clientX, y: event.clientY };
    });
    activateBtn.addEventListener("pointerup", function (event) {
      if (!tapStart) return;
      var moved = Math.abs(event.clientX - tapStart.x) + Math.abs(event.clientY - tapStart.y);
      tapStart = null;
      if (moved >= 12) return;
      event.preventDefault();
      event.stopPropagation();
      activateArmed = true;
      // Hide only after the gesture's click, so it cannot fall through onto a precinct.
      root.setTimeout(function () {
        if (!activateArmed) return;
        activateArmed = false;
        activateMap();
      }, 400);
    });
    activateBtn.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      activateArmed = false;
      activateMap();
    });
  }
  if (doneBtn) doneBtn.addEventListener("click", deactivateMap);
  if (coarse.addEventListener) coarse.addEventListener("change", applyGestureMode);
  doc.addEventListener("keydown", function (event) {
    if (event.key === "Escape") deactivateMap();
  });
  doc.addEventListener("touchstart", function (event) {
    if (!coarse.matches || !mapActivated) return;
    if (frame.contains(event.target)) return;
    deactivateMap();
  }, { passive: true });
  map.on("focus", function () {
    if (!frame.classList.contains("is-inert")) map.scrollWheelZoom.enable();
  });
  map.getContainer().addEventListener("mouseleave", function () {
    map.scrollWheelZoom.disable();
  });
  if (searchForm) {
    searchForm.addEventListener("submit", function (event) {
      event.preventDefault();
      runSearch(true);
    });
  }
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      var query = String(searchInput.value || "").replace(/\s+/g, "");
      if (query && layersById[query]) showOnMap(query, false);
    });
  }
  Array.prototype.forEach.call(doc.querySelectorAll("a.show-on-map"), function (link) {
    link.addEventListener("click", function (event) {
      event.preventDefault();
      showOnMap(link.getAttribute("data-precinct"), true);
    });
  });

  applyGestureMode();

  root.fetch("/data/pct4-precincts.geojson").then(function (response) {
    if (!response.ok) throw new Error("map data");
    return response.json();
  }).then(function (data) {
    data.features.sort(function (a, b) { return bboxArea(b) - bboxArea(a); });
    precinctGroup = root.L.geoJSON(data, {
      style: function (feature) {
        return styleFor(String(feature.properties.precinct), false);
      },
      onEachFeature: onEachFeature
    }).addTo(map);
    precinctGroup.eachLayer(function (layer) {
      var id = String(layer.feature.properties.precinct);
      wireElement(layer, id, statusByPrecinct[id] || STATUS_UNKNOWN);
    });
    fitAllPrecincts();
    loaded = true;
    var count = Object.keys(layersById).length;
    if (!(searchStatus && searchStatus.textContent)) setStatus(count + " precincts on the map.");
    if (pendingShow && pendingShow.search) {
      if (searchInput) searchInput.value = pendingShow.id;
      runSearch(true);
    } else if (pendingShow && layersById[pendingShow.id]) {
      showOnMap(pendingShow.id, pendingShow.scrollMap);
    }
    pendingShow = null;
  }).catch(function () {
    setStatus("The precinct map did not load.");
  });

  root.addEventListener("resize", function () {
    if (showingAll) fitAllPrecincts();
    else map.invalidateSize();
  });
})(typeof window !== "undefined" ? window : globalThis);
