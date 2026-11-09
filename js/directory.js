(function (root) {
  "use strict";

  function filterRows(rows, query, status) {
    var needle = String(query || "").replace(/\s+/g, "");
    var wanted = String(status || "");
    var matched = [];
    for (var i = 0; i < rows.length; i += 1) {
      var row = rows[i];
      if (needle && String(row.precinct).indexOf(needle) === -1) continue;
      if (wanted && String(row.status) !== wanted) continue;
      matched.push(row);
    }
    return matched;
  }

  root.DirectoryFilter = { filterRows: filterRows };
  if (!root.document || !root.document.getElementById) return;

  var table = root.document.getElementById("precinct-directory");
  var precinctInput = root.document.getElementById("directory-precinct");
  var statusInput = root.document.getElementById("directory-status");
  if (!table || !precinctInput || !statusInput) return;

  var rows = Array.prototype.map.call(table.tBodies[0].rows, function (row) {
    return {
      precinct: row.getAttribute("data-precinct"),
      status: row.getAttribute("data-status"),
      node: row
    };
  });
  var note = root.document.getElementById("directory-filter-status");

  function apply() {
    var visible = filterRows(rows, precinctInput.value, statusInput.value);
    var keep = {};
    visible.forEach(function (row) { keep[row.precinct] = true; });
    rows.forEach(function (row) { row.node.hidden = !keep[row.precinct]; });
    if (note) note.textContent = visible.length + " of " + rows.length + " precincts shown.";
  }

  precinctInput.addEventListener("input", apply);
  statusInput.addEventListener("change", apply);
})(typeof window !== "undefined" ? window : globalThis);
