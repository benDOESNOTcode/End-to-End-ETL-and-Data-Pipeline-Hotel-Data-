(async function () {
  const API_BASE = "http://127.0.0.1:5000";

  // helper for element lookup
  const $ = id => document.getElementById(id);
  const tableSelect = $("tableSelect");
  const colFilter = $("colFilter");
  const opFilter = $("opFilter");
  const valFilter = $("valFilter");
  const addFilterBtn = $("addFilter");
  const fetchBtn = $("fetch");
  const loadColsBtn = $("loadCols");
  const limitInput = $("limit");
  const appliedDiv = $("appliedFilters");
  const resultTable = $("resultTable");

  let currentTable = null;
  let cols = [];
  let applied = [];

  // api helper
  async function api(path, opts) {
    const url = API_BASE + path;
    const r = await fetch(url, opts);
    if (!r.ok) {
      const text = await r.text().catch(() => "");
      throw new Error(`Request to ${url} failed: ${r.status} ${text}`);
    }
    return r.json();
  }

  // load tables into drop down
  async function loadTables() {
    try {
      const data = await api("/api/tables");
      console.log("tables:", data);
      tableSelect.innerHTML = data.tables
        .map(t => `<option value="${t}">${t}</option>`)
        .join("");
      currentTable = tableSelect.value;
      await loadColumns();
    } catch (err) {
      console.error(err);
      alert("Failed to load tables. Check that the backend is running.");
    }
  }

  // load col names for table
  async function loadColumns() {
    currentTable = tableSelect.value;
    if (!currentTable) return;
    try {
      const data = await api(
        `/api/columns?table=${encodeURIComponent(currentTable)}`
      );
      console.log("columns:", data);
      cols = data.columns.map(c => c.name);
      colFilter.innerHTML = cols
        .map(c => `<option value="${c}">${c}</option>`)
        .join("");
    } catch (err) {
      console.error(err);
      alert("Failed to load columns for this table.");
    }
  }

  // active filters > badges + add removal
  function renderApplied() {
    appliedDiv.innerHTML = applied
      .map(
        (f, i) =>
          `<span class="badge bg-info text-dark me-1">${f.column} ${f.op} ${f.value} <a href="#" data-i="${i}">&times;</a></span>`
      )
      .join("");
    appliedDiv.querySelectorAll("a").forEach(a => {
      a.addEventListener("click", e => {
        const i = Number(e.target.dataset.i);
        applied.splice(i, 1);
        renderApplied();
      });
    });
  }

  // add new filter from ui
  addFilterBtn.addEventListener("click", () => {
    const f = {
      column: colFilter.value,
      op: opFilter.value,
      value: valFilter.value
    };
    if (!f.value) return alert("Enter a filter value.");
    applied.push(f);
    renderApplied();
  });

  // fetch data for selection
  fetchBtn.addEventListener("click", async () => {
    const table = tableSelect.value;
    const limit = Number(limitInput.value) || 100;
    const body = { table, filters: applied, limit };

    try {
      const data = await api("/api/data", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body)
      });
      console.log("rows:", data);
      if (data.error) {
        alert(data.error);
      } else {
        renderTable(data.rows);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to fetch data for this table.");
    }
  });

  // manual reload
  loadColsBtn.addEventListener("click", loadColumns);
  // reload on table change
  tableSelect.addEventListener("change", loadColumns);

  // render
  function renderTable(rows) {
    const thead = resultTable.querySelector("thead");
    const tbody = resultTable.querySelector("tbody");
    thead.innerHTML = "";
    tbody.innerHTML = "";
    if (!rows || rows.length === 0) return;

    const keys = Object.keys(rows[0]);
    thead.innerHTML =
      "<tr>" + keys.map(k => `<th>${k}</th>`).join("") + "</tr>";
    tbody.innerHTML = rows
      .map(
        r =>
          "<tr>" +
          keys
            .map(
              k =>
                `<td>${escapeHTML(String(r[k] == null ? "" : r[k]))}</td>`
            )
            .join("") +
          "</tr>"
      )
      .join("");
  }

  function escapeHTML(s) {
    return s
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }

  // init load
  await loadTables();
})();
