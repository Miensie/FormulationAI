/**
 * FormulationAI — taskpane.js
 * ============================
 * Logique complète du frontend Excel Add-in.
 * Tous les appels API passent par apiPost() / apiGet().
 */

// ── Configuration API ────────────────────────────────────────────────────────
const API = (window.FORMULATIONAI_CONFIG?.API_BASE_URL || "http://localhost:8000") + "/api/v1";

// ── État global ──────────────────────────────────────────────────────────────
const state = {
  components:          [],      // [{id, min, max, fixed}]
  generatedFormulas:   [],      // dernières formulations générées
  trainedModelKey:     null,    // clé du modèle ML entraîné
  trainedComponentIds: [],      // ordre des features du modèle
  charts:              {},      // instances Chart.js
  officeReady:         false,
  trainData:           null,    // données lues depuis Excel
};

// ── Matériaux chargés depuis la BD ──────────────────────────────────────────
let MATERIALS_CACHE = {};
let CATEGORIES_CACHE = [];
let PROPERTIES_CACHE = {};

// ════════════════════════════════════════════════════════════════════════════
// INIT
// ════════════════════════════════════════════════════════════════════════════

Office.onReady((info) => {
  if (info.host === Office.HostType.Excel) state.officeReady = true;
  initApp();
});

async function initApp() {
  setupTabs();
  setupEventListeners();
  updateSimParams();
  await loadDatabaseCache();
  populatePropertiesChecks();
  checkAPIHealth();
  setInterval(checkAPIHealth, 30000);
}

// ── Health check ─────────────────────────────────────────────────────────────
async function checkAPIHealth() {
  const dot = document.getElementById("statusDot");
  try {
    const r = await fetch(API.replace("/api/v1","") + "/health",
                          {signal: AbortSignal.timeout(3000)});
    dot.className = r.ok ? "status-dot online" : "status-dot offline";
  } catch { dot.className = "status-dot offline"; }
}

// ── Tabs ─────────────────────────────────────────────────────────────────────
function setupTabs() {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
    });
  });
}

// ── Event listeners ──────────────────────────────────────────────────────────
function setupEventListeners() {
  document.getElementById("btnAddComponent")  .addEventListener("click", addComponent);
  document.getElementById("btnGenerate")      .addEventListener("click", generateFormulations);
  document.getElementById("btnOptimize")      .addEventListener("click", runOptimization);
  document.getElementById("btnRecommend")     .addEventListener("click", runRecommend);
  document.getElementById("btnAnalyze")       .addEventListener("click", runAnalyze);
  document.getElementById("btnSimulate")      .addEventListener("click", runSimulation);
  document.getElementById("btnReadTrain")     .addEventListener("click", readTrainData);
  document.getElementById("btnTrain")         .addEventListener("click", trainModel);
  document.getElementById("btnPredictGenerated").addEventListener("click", predictGenerated);
  document.getElementById("btnDbSearch")      .addEventListener("click", searchDatabase);

  // Objectif optimisation
  document.getElementById("optimizeObjective").addEventListener("change", () => {
    const obj = document.getElementById("optimizeObjective").value;
    document.getElementById("targetPropertyPanel").style.display =
      obj === "property" ? "block" : "none";
  });

  // Budget buttons
  document.querySelectorAll(".budget-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".budget-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// CHARGEMENT BASE DE DONNÉES
// ════════════════════════════════════════════════════════════════════════════

async function loadDatabaseCache() {
  try {
    // Matériaux
    const matRes = await apiGet("/db/materials");
    MATERIALS_CACHE = matRes.materials || {};

    // Catégories
    const catRes = await apiGet("/db/categories");
    CATEGORIES_CACHE = catRes.categories || [];

    // Propriétés
    const propRes = await apiGet("/db/properties");
    PROPERTIES_CACHE = propRes.properties || {};

    // Remplir le select des composants
    populateComponentSelect();

    // Remplir le select des catégories DB
    const catSelect = document.getElementById("dbCategory");
    catSelect.innerHTML = '<option value="">Toutes categories</option>';
    CATEGORIES_CACHE.forEach(cat => {
      catSelect.insertAdjacentHTML("beforeend",
        `<option value="${cat}">${cat.charAt(0).toUpperCase()+cat.slice(1)}</option>`);
    });

    showToast(`BD chargee : ${Object.keys(MATERIALS_CACHE).length} materiaux`, "success");
  } catch(e) {
    showToast("BD non disponible — mode offline", "info");
    loadFallbackMaterials();
  }
}

function loadFallbackMaterials() {
  // Matériaux minimaux pour mode offline
  MATERIALS_CACHE = {
    "Water":          {name:"Purified Water",      category:"solvent",    min_pct:0,   max_pct:99,  cost_rel:1},
    "Ethanol_96":     {name:"Ethanol 96%",          category:"solvent",    min_pct:1,   max_pct:80,  cost_rel:12},
    "Glycerol":       {name:"Glycerol",             category:"solvent",    min_pct:1,   max_pct:50,  cost_rel:8},
    "HPMC_E5":        {name:"HPMC E5",              category:"polymer",    min_pct:0.5, max_pct:5,   cost_rel:25},
    "Carbopol_971P":  {name:"Carbopol 971P",        category:"polymer",    min_pct:0.1, max_pct:2,   cost_rel:40},
    "Tween_80":       {name:"Polysorbate 80",        category:"surfactant", min_pct:0.1, max_pct:5,   cost_rel:20},
    "SDS":            {name:"SDS/SLS",              category:"surfactant", min_pct:0.1, max_pct:3,   cost_rel:8},
    "Vaseline":       {name:"White Petrolatum",     category:"oil",        min_pct:1,   max_pct:80,  cost_rel:5},
    "Phenoxyethanol": {name:"Phenoxyethanol",       category:"preservative",min_pct:0.5,max_pct:1,   cost_rel:20},
    "Ibuprofen":      {name:"Ibuprofen",            category:"api",        min_pct:1,   max_pct:20,  cost_rel:40},
  };
  populateComponentSelect();
}

function populateComponentSelect() {
  const select = document.getElementById("componentToAdd");
  select.innerHTML = "";
  const grouped = {};
  Object.entries(MATERIALS_CACHE).forEach(([id, mat]) => {
    const cat = mat.category || "other";
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push({id, name: mat.name || id});
  });
  Object.entries(grouped).sort().forEach(([cat, items]) => {
    const grp = document.createElement("optgroup");
    grp.label = cat.charAt(0).toUpperCase() + cat.slice(1);
    items.sort((a,b) => a.name.localeCompare(b.name)).forEach(({id, name}) => {
      const opt = document.createElement("option");
      opt.value = id; opt.textContent = name;
      grp.appendChild(opt);
    });
    select.appendChild(grp);
  });
}

function populatePropertiesChecks() {
  const container = document.getElementById("targetPropsChecks");
  const propIds = Object.keys(PROPERTIES_CACHE).length > 0
    ? Object.keys(PROPERTIES_CACHE)
    : ["viscosity","pH","stability_index","spreadability","cost_index","HLB_required","release_rate_2h","zeta_potential"];
  container.innerHTML = propIds.map(id => {
    const name = PROPERTIES_CACHE[id]?.name || id;
    return `<label class="prop-check">
      <input type="checkbox" class="prop-cb" value="${id}"/>
      ${name.length > 22 ? name.substring(0,22)+"…" : name}
    </label>`;
  }).join("");
}

// ════════════════════════════════════════════════════════════════════════════
// ONGLET COMPOSER
// ════════════════════════════════════════════════════════════════════════════

function addComponent() {
  const id    = document.getElementById("componentToAdd").value;
  const min   = parseFloat(document.getElementById("compMin").value) || 0;
  const max   = parseFloat(document.getElementById("compMax").value) || 100;

  if (!id) { showToast("Choisissez un composant", "error"); return; }
  if (state.components.find(c => c.id === id)) {
    showToast("Composant deja ajoute", "error"); return;
  }
  if (min > max) { showToast("Min > Max", "error"); return; }

  state.components.push({id, min, max, fixed: false});
  renderComponentsList();
  showToast(`${MATERIALS_CACHE[id]?.name || id} ajoute`, "success");
}

function removeComponent(id) {
  state.components = state.components.filter(c => c.id !== id);
  renderComponentsList();
}

function renderComponentsList() {
  const container = document.getElementById("componentsList");
  if (!state.components.length) {
    container.innerHTML = `<div class="hint" style="padding:8px">Aucun composant — ajoutez-en ci-dessous</div>`;
    return;
  }
  container.innerHTML = state.components.map(c => {
    const mat = MATERIALS_CACHE[c.id] || {};
    const name = (mat.name || c.id).substring(0, 22);
    const cat  = mat.category || "?";
    return `<div class="component-item">
      <span class="comp-cat">${cat}</span>
      <span class="comp-name">${name}</span>
      <span class="comp-range">${c.min}–${c.max}%</span>
      <button class="btn-remove" onclick="removeComponent('${c.id}')">✕</button>
    </div>`;
  }).join("");
}

async function generateFormulations() {
  if (state.components.length < 2) {
    showToast("Ajoutez au moins 2 composants", "error"); return;
  }
  showLoader("Generation des formulations...");
  try {
    const res = await apiPost("/generate_formulation", {
      components:     state.components,
      n_formulations: parseInt(document.getElementById("nFormulations").value) || 5,
      method:         document.getElementById("genMethod").value,
      seed:           42,
    });

    state.generatedFormulas = res.formulations || [];
    renderFormulations(res);
    showToast(`${res.n_generated} formulations generees`, "success");
  } catch(e) {
    showToast("Erreur generation : " + e.message, "error");
  } finally { hideLoader(); }
}

function renderFormulations(res) {
  const panel = document.getElementById("formulations-result");
  panel.style.display = "block";

  // Stats globales
  const s = res.statistics || {};
  let html = `<div class="result-block">
    <h4>Statistiques (${res.n_generated} formulations)</h4>
    <div class="metric-row"><span class="metric-label">Cout min</span>
      <span class="metric-value good">${s.cost_min?.toFixed(2)||"—"}</span></div>
    <div class="metric-row"><span class="metric-label">Cout max</span>
      <span class="metric-value warn">${s.cost_max?.toFixed(2)||"—"}</span></div>
    <div class="metric-row"><span class="metric-label">Cout moyen</span>
      <span class="metric-value">${s.cost_mean?.toFixed(2)||"—"}</span></div>
    <div class="metric-row"><span class="metric-label">Densite moy.</span>
      <span class="metric-value">${s.density_mean?.toFixed(4)||"—"}</span></div>
  </div>`;

  // Cartes formulations
  res.formulations.slice(0, 5).forEach((f, i) => {
    const comp = f.composition || {};
    const entries = Object.entries(comp).sort((a,b) => b[1]-a[1]);
    const bars = entries.map(([id, pct]) => {
      const name = (MATERIALS_CACHE[id]?.name || id).substring(0, 18);
      const width = Math.max(2, pct);
      return `<div class="comp-bar-row">
        <div class="comp-bar-label">${name}</div>
        <div class="comp-bar-track"><div class="comp-bar-fill" style="width:${width}%"></div></div>
        <div class="comp-bar-val">${pct.toFixed(1)}%</div>
      </div>`;
    }).join("");

    html += `<div class="form-card">
      <div class="form-card-header">
        <span class="form-card-title">Formulation #${i+1}</span>
        <div class="form-card-badges">
          <span class="badge badge-amber">Cout ${f.cost_index?.toFixed(1)}</span>
          <span class="badge badge-cyan">d=${f.density_est?.toFixed(3)}</span>
          ${f.HLB_avg != null ? `<span class="badge badge-green">HLB ${f.HLB_avg}</span>` : ""}
        </div>
      </div>
      ${bars}
    </div>`;
  });

  panel.innerHTML = html;

  // Graphique radar (premières 3 formulations)
  renderComposeChart(res.formulations.slice(0, 3));
}

function renderComposeChart(formulas) {
  const card = document.getElementById("composeChartCard");
  card.style.display = "block";
  destroyChart("composeChart");

  const allIds = [...new Set(formulas.flatMap(f => Object.keys(f.composition || {})))];
  const colors = ["rgba(0,229,200,.7)","rgba(245,158,11,.7)","rgba(59,130,246,.7)"];

  const ctx = document.getElementById("composeChart").getContext("2d");
  state.charts["composeChart"] = new Chart(ctx, {
    type: "radar",
    data: {
      labels: allIds.map(id => (MATERIALS_CACHE[id]?.name || id).substring(0,12)),
      datasets: formulas.map((f, i) => ({
        label:           `#${i+1}`,
        data:            allIds.map(id => f.composition?.[id] || 0),
        borderColor:     colors[i],
        backgroundColor: colors[i].replace("0.7","0.1"),
        borderWidth:     2,
        pointRadius:     3,
      })),
    },
    options: {
      ...chartOptions("Comparaison compositions"),
      scales: {
        r: {
          grid:        { color: "rgba(255,255,255,.06)" },
          ticks:       { color: "#3a3f55", font: {size:8}, backdropColor:"transparent" },
          pointLabels: { color: "#7a8098", font: {size:9} },
        },
      },
    },
  });
}

// ════════════════════════════════════════════════════════════════════════════
// ONGLET OPTIMISER
// ════════════════════════════════════════════════════════════════════════════

async function runOptimization() {
  if (state.components.length < 2) {
    showToast("Ajoutez des composants dans l'onglet Composer", "error"); return;
  }
  const obj = document.getElementById("optimizeObjective").value;
  showLoader("Optimisation en cours...");
  try {
    let res;
    if (obj === "cost") {
      res = await apiPost("/optimize/cost", { components: state.components });
    } else if (obj === "pareto") {
      res = await apiPost("/optimize/pareto", { components: state.components, n_solutions: 20 });
    } else {
      const w = { cost: parseFloat(document.getElementById("weightCost").value) || 0.5 };
      const hlb = parseFloat(document.getElementById("targetHLB").value);
      const den = parseFloat(document.getElementById("targetDensity").value);
      if (!isNaN(hlb)) { w.target_HLB = hlb; w.w_HLB = 1.0; }
      if (!isNaN(den)) { w.target_density = den; w.w_density = 0.5; }
      res = await apiPost("/optimize", {
        components:      state.components,
        target_property: "composite",
        weights:         w,
      });
    }

    renderOptResult(res, obj);
    showToast("Optimisation terminee", "success");
  } catch(e) {
    showToast("Erreur optimisation : " + e.message, "error");
  } finally { hideLoader(); }
}

function renderOptResult(res, obj) {
  const el = document.getElementById("optResult");
  el.style.display = "block";

  if (obj === "pareto" && res.solutions) {
    // Graphique Pareto
    const card = document.getElementById("optChartCard");
    card.style.display = "block";
    destroyChart("optChart");
    const ctx = document.getElementById("optChart").getContext("2d");
    state.charts["optChart"] = new Chart(ctx, {
      type: "scatter",
      data: { datasets: [{
        label:           "Front de Pareto",
        data:            res.solutions.map(s => ({x: s.cost, y: s.density})),
        backgroundColor: "rgba(0,229,200,.7)",
        pointRadius:     5,
      }]},
      options: chartOptions("Pareto : Cout vs Densite"),
    });

    el.innerHTML = `<h4>Front de Pareto (${res.n_solutions} solutions)</h4>
      <div class="metric-row"><span class="metric-label">Cout min</span>
        <span class="metric-value good">${Math.min(...res.solutions.map(s=>s.cost)).toFixed(2)}</span></div>
      <div class="metric-row"><span class="metric-label">Cout max</span>
        <span class="metric-value">${Math.max(...res.solutions.map(s=>s.cost)).toFixed(2)}</span></div>
      <div class="hint" style="margin-top:6px">Chaque point = un compromis cout/densite. Choisissez selon votre priorite.</div>`;
    return;
  }

  const comp  = res.composition || {};
  const entries = Object.entries(comp).sort((a,b)=>b[1]-a[1]);
  const bars = entries.map(([id, pct]) => {
    const name = (MATERIALS_CACHE[id]?.name || id).substring(0, 20);
    return `<div class="comp-bar-row">
      <div class="comp-bar-label">${name}</div>
      <div class="comp-bar-track"><div class="comp-bar-fill" style="width:${Math.max(2,pct)}%"></div></div>
      <div class="comp-bar-val">${pct.toFixed(2)}%</div>
    </div>`;
  }).join("");

  el.innerHTML = `
    <h4>${obj === "cost" ? "Formulation a cout minimal" : "Formulation optimisee"}</h4>
    <div class="metric-row"><span class="metric-label">Cout</span>
      <span class="metric-value good">${res.cost_index?.toFixed(2)||"—"}</span></div>
    <div class="metric-row"><span class="metric-label">Densite</span>
      <span class="metric-value">${res.density_est?.toFixed(4)||"—"}</span></div>
    ${res.HLB_avg != null ? `<div class="metric-row"><span class="metric-label">HLB moyen</span>
      <span class="metric-value">${res.HLB_avg}</span></div>` : ""}
    <div class="metric-row"><span class="metric-label">Converge</span>
      <span class="metric-value ${res.converged?'good':'warn'}">${res.converged?"oui":"non"}</span></div>
    <div style="margin-top:8px">${bars}</div>`;
}

// ════════════════════════════════════════════════════════════════════════════
// ONGLET PREDIRE
// ════════════════════════════════════════════════════════════════════════════

async function readTrainData() {
  const range = document.getElementById("trainRange").value.trim();
  if (!state.officeReady) {
    // Mode démo
    generateDemoTrainData();
    showToast("Mode demo : donnees simulees", "info"); return;
  }
  showLoader("Lecture Excel...");
  try {
    await Excel.run(async (ctx) => {
      const sheet = ctx.workbook.worksheets.getActiveWorksheet();
      const r = sheet.getRange(range);
      r.load("values");
      await ctx.sync();
      const vals = r.values;
      if (!vals || vals.length < 3) throw new Error("Trop peu de lignes (min 3)");
      state.trainData = vals;
      const headers = vals[0];
      const n = vals.length - 1;
      document.getElementById("trainPreview").textContent =
        `${n} lignes, ${headers.length} colonnes : ${headers.join(", ")}`;
      showToast(`${n} echantillons charges`, "success");
    });
  } catch(e) {
    showToast("Erreur lecture : " + e.message, "error");
  } finally { hideLoader(); }
}

function generateDemoTrainData() {
  // Démo : 12 formulations eau/glycerol/HPMC + viscosité mesurée
  const headers = ["Water", "Glycerol", "HPMC_E5", "Tween_80", "viscosity"];
  const rows = [headers];
  const rng = (a,b) => a + Math.random()*(b-a);
  for (let i = 0; i < 15; i++) {
    const w  = rng(50, 80);
    const g  = rng(5, 25);
    const h  = rng(0.5, 4);
    const t  = rng(0.5, 3);
    const sum = w+g+h+t;
    // Viscosité modèle simple : fonction du HPMC
    const visc = 50 + 800 * (h/sum*100) + rng(-30, 30);
    rows.push([
      Math.round(w/sum*100*10)/10,
      Math.round(g/sum*100*10)/10,
      Math.round(h/sum*100*10)/10,
      Math.round(t/sum*100*10)/10,
      Math.round(visc),
    ]);
  }
  state.trainData = rows;
  document.getElementById("trainPreview").textContent =
    `Demo: 15 formulations | Colonnes: ${headers.join(", ")}`;
}

async function trainModel() {
  if (!state.trainData) {
    showToast("Lisez d'abord les donnees d'entrainement", "error"); return;
  }
  const headers = state.trainData[0];
  const propName = document.getElementById("predictPropName").value.trim() ||
                   headers[headers.length - 1];
  const compIds  = headers.slice(0, -1);
  const rows     = state.trainData.slice(1).filter(r => r.every(v => v !== "" && !isNaN(v)));

  showLoader("Entrainement du modele ML...");
  try {
    const formulations   = rows.map(r => Object.fromEntries(compIds.map((id,j) => [id, parseFloat(r[j])])));
    const target_values  = rows.map(r => parseFloat(r[r.length-1]));

    const res = await apiPost("/predict/train", {
      formulations, target_values, component_ids: compIds,
      target_property: propName,
      model_type: document.getElementById("predictModel").value,
      n_estimators: 100,
    });

    state.trainedModelKey     = res.model_cache_key;
    state.trainedComponentIds = compIds;

    const el = document.getElementById("trainResult");
    el.style.display = "block";
    el.innerHTML = `
      <h4>Modele entraine — ${res.target_property}</h4>
      <div class="metric-row"><span class="metric-label">R2 train</span>
        <span class="metric-value ${res.r2_train>0.9?'good':'warn'}">${res.r2_train?.toFixed(6)}</span></div>
      <div class="metric-row"><span class="metric-label">RMSE train</span>
        <span class="metric-value">${res.rmse_train?.toFixed(4)}</span></div>
      <div class="metric-row"><span class="metric-label">CV R2</span>
        <span class="metric-value">${res.cv_r2 ?? "—"}</span></div>
      <div class="metric-row"><span class="metric-label">Cle cache</span>
        <span class="metric-value" style="font-size:9px">${res.model_cache_key}</span></div>`;

    showToast(`Modele entraine — R2=${res.r2_train?.toFixed(3)}`, "success");
  } catch(e) {
    showToast("Erreur entrainement : " + e.message, "error");
  } finally { hideLoader(); }
}

async function predictGenerated() {
  if (!state.trainedModelKey) {
    showToast("Entrainer d'abord le modele (onglet Predire)", "error"); return;
  }
  const forms = state.generatedFormulas.length > 0
    ? state.generatedFormulas.map(f => f.composition)
    : null;

  if (!forms) {
    showToast("Generez d'abord des formulations (onglet Composer)", "error"); return;
  }

  showLoader("Prediction en cours...");
  try {
    const res = await apiPost("/predict", {
      formulations:    forms,
      component_ids:   state.trainedComponentIds,
      model_cache_key: state.trainedModelKey,
    });

    const el = document.getElementById("predictResult");
    el.style.display = "block";
    const ps = res.pred_stats || {};
    const rows = (res.predictions || []).map((v, i) =>
      `<div class="metric-row"><span class="metric-label">Formulation #${i+1}</span>
       <span class="metric-value">${v.toFixed(4)}</span></div>`
    ).join("");

    el.innerHTML = `
      <h4>Predictions — ${res.target_property}</h4>
      <div class="metric-row"><span class="metric-label">Moy.</span>
        <span class="metric-value">${ps.mean?.toFixed(4)||"—"}</span></div>
      <div class="metric-row"><span class="metric-label">Min/Max</span>
        <span class="metric-value">[${ps.min?.toFixed(3)||"—"}, ${ps.max?.toFixed(3)||"—"}]</span></div>
      ${rows}`;

    showToast(`${res.predictions.length} predictions calculees`, "success");
  } catch(e) {
    showToast("Erreur prediction : " + e.message, "error");
  } finally { hideLoader(); }
}

// ════════════════════════════════════════════════════════════════════════════
// ONGLET IA ADVISOR
// ════════════════════════════════════════════════════════════════════════════

async function runRecommend() {
  const props = [...document.querySelectorAll(".prop-cb:checked")].map(c => c.value);
  if (!props.length) { showToast("Cochez au moins une propriete cible", "error"); return; }

  const app    = document.getElementById("applicationSelect").value;
  const budget = document.querySelector(".budget-btn.active")?.dataset.budget || "medium";
  const current = state.components.map(c => c.id);

  showLoader("Analyse IA en cours...");
  try {
    const res = await apiPost("/recommend", {
      target_properties:  props,
      application:        app,
      current_components: current,
      budget_level:       budget,
    });
    renderAIReport(res);
    showToast("Recommandations IA generees", "success");
  } catch(e) {
    showToast("Erreur IA : " + e.message, "error");
  } finally { hideLoader(); }
}

function renderAIReport(res) {
  const el = document.getElementById("aiAdvisorReport");
  el.style.display = "block";

  const sugg = res.suggested_components || [];
  const alerts = res.general_alerts || [];

  const suggHtml = sugg.map(s => `
    <div style="background:var(--input);border:1px solid var(--border);border-radius:4px;padding:7px 9px;margin-bottom:5px">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="font-size:11px;font-weight:600;color:var(--text)">${s.name}</span>
        <div>
          <span class="badge badge-cyan">${s.category}</span>
          <span class="badge badge-amber" style="margin-left:3px">cout ${s.cost_rel}</span>
        </div>
      </div>
      <div style="font-size:9px;color:var(--dim);margin-top:2px">${s.reason}</div>
      <div style="font-size:9px;color:var(--cyan);margin-top:1px">
        Plage recommandee : ${s.min_pct}–${s.max_pct}%
      </div>
    </div>`).join("");

  const alertHtml = alerts.map(a =>
    `<div style="font-size:10px;color:var(--amber);padding:3px 0;border-bottom:1px solid var(--border)">⚠ ${a}</div>`
  ).join("");

  el.innerHTML = `
    <div class="ai-section">
      <div class="ai-section-title">Composants recommandes</div>
      ${suggHtml || '<span class="hint">Aucune suggestion disponible</span>'}
    </div>
    <div class="ai-section">
      <div class="ai-section-title">Methode d'optimisation</div>
      <div style="font-size:11px;color:var(--text)">${res.recommended_method || "—"}</div>
      <div class="hint" style="margin-top:3px">${res.method_reason || ""}</div>
    </div>
    ${alerts.length ? `<div class="ai-section">
      <div class="ai-section-title">Points de vigilance</div>
      ${alertHtml}
    </div>` : ""}
    <div style="background:var(--cyan-dim);border:1px solid rgba(0,229,200,.2);border-radius:5px;padding:8px;margin-top:6px;font-size:11px;color:var(--cyan)">
      🎯 ${res.priority_action || ""}
    </div>`;
}

async function runAnalyze() {
  if (!state.components.length) {
    showToast("Ajoutez des composants dans l'onglet Composer", "error"); return;
  }
  // Construire une formulation representative (moyenne des bornes)
  const total = state.components.reduce((s,c) => s + (c.min+c.max)/2, 0);
  const formulation = Object.fromEntries(
    state.components.map(c => [c.id, ((c.min+c.max)/2) * 100 / total])
  );

  showLoader("Analyse de la formulation...");
  try {
    const res = await apiPost("/recommend/analyze", {
      formulation,
      application: document.getElementById("applicationSelect").value,
    });
    renderAnalyzeReport(res);
    showToast("Analyse terminee", "success");
  } catch(e) {
    showToast("Erreur analyse : " + e.message, "error");
  } finally { hideLoader(); }
}

function renderAnalyzeReport(res) {
  const el = document.getElementById("analyzeReport");
  el.style.display = "block";

  const compat = res.compatibility || {};
  const est    = res.estimated_properties || {};
  const recs   = res.recommendations || [];

  const recoHtml = recs.map(r => {
    const color = r.type==="error" ? "var(--red)" : r.type==="warning" ? "var(--amber)" : "var(--blue)";
    const icon  = r.type==="error" ? "✗" : r.type==="warning" ? "⚠" : "ℹ";
    return `<div style="border-left:3px solid ${color};padding:5px 8px;margin-bottom:5px;background:var(--input);border-radius:0 4px 4px 0">
      <div style="font-size:10px;color:${color}">${icon} ${r.message}</div>
      <div class="hint" style="margin-top:2px">${r.suggestion}</div>
    </div>`;
  }).join("");

  el.innerHTML = `
    <div class="ai-section">
      <div class="ai-section-title">Compatibilite</div>
      <span style="font-size:11px;color:${compat.compatible?'var(--green)':'var(--red)'}">
        ${compat.compatible ? "✓ Compatible" : "✗ Problemes detectes"}
      </span>
      ${(compat.alerts||[]).map(a=>`<div class="hint" style="color:var(--red);margin-top:2px">${a}</div>`).join("")}
      ${(compat.warnings||[]).map(w=>`<div class="hint" style="color:var(--amber);margin-top:2px">${w}</div>`).join("")}
    </div>
    <div class="ai-section">
      <div class="ai-section-title">Proprietes estimees</div>
      ${est.HLB_avg != null ? `<div class="metric-row"><span class="metric-label">HLB moyen</span><span class="metric-value">${est.HLB_avg} — ${est.emulsion_type||""}</span></div>` : ""}
      ${est.viscosity_qualitative ? `<div class="metric-row"><span class="metric-label">Viscosite</span><span class="metric-value">${est.viscosity_qualitative}</span></div>` : ""}
      ${est.polymer_fraction_pct != null ? `<div class="metric-row"><span class="metric-label">Fraction polymere</span><span class="metric-value">${est.polymer_fraction_pct}%</span></div>` : ""}
    </div>
    ${recs.length ? `<div class="ai-section"><div class="ai-section-title">Recommandations (${recs.length})</div>${recoHtml}</div>` : ""}`;
}

// ════════════════════════════════════════════════════════════════════════════
// ONGLET SIMULER
// ════════════════════════════════════════════════════════════════════════════

const SIM_PARAMS = {
  viscosity: `
    <div class="row-2">
      <div><label class="field-label small">T min (°C)</label>
        <input class="field-input" id="simTMin" type="number" value="5"/></div>
      <div><label class="field-label small">T max (°C)</label>
        <input class="field-input" id="simTMax" type="number" value="60"/></div>
    </div>
    <div class="mt-8"><label class="field-label small">Viscosite de reference (mPa.s)</label>
      <input class="field-input" id="simViscRef" type="number" value="1000"/></div>`,

  release: `
    <div class="row-2">
      <div><label class="field-label small">Duree (h)</label>
        <input class="field-input" id="simTimeMax" type="number" value="24"/></div>
      <div><label class="field-label small">Actif (ID)</label>
        <input class="field-input" id="simApiId" value="Ibuprofen"/></div>
    </div>`,

  stability: `
    <div class="row-2">
      <div><label class="field-label small">Duree (mois)</label>
        <input class="field-input" id="simMonths" type="number" value="24"/></div>
      <div><label class="field-label small">Temperature (°C)</label>
        <input class="field-input" id="simTempStab" type="number" value="25"/></div>
    </div>
    <div class="mt-4"><label class="field-label small">Humidite (%)</label>
      <input class="field-input" id="simHumidity" type="number" value="60"/></div>`,

  compare: `<p class="hint">Compare les formulations generees sur : cout, densite, HLB, n_composants.</p>`,
};

function updateSimParams() {
  const type = document.getElementById("simType").value;
  document.getElementById("simParamsPanel").innerHTML =
    `<label class="field-label">Parametres</label>${SIM_PARAMS[type] || ""}`;
}

async function runSimulation() {
  const type = document.getElementById("simType").value;

  // Obtenir la formulation de reference (premiere generee ou moyenne des contraintes)
  let formulation = {};
  if (state.generatedFormulas.length > 0) {
    formulation = state.generatedFormulas[0].composition;
  } else if (state.components.length > 0) {
    const total = state.components.reduce((s,c) => s+(c.min+c.max)/2, 0);
    state.components.forEach(c => { formulation[c.id] = ((c.min+c.max)/2)*100/total; });
  } else {
    // Formulation démo
    formulation = { Water: 70, Glycerol: 15, HPMC_E5: 2, Tween_80: 1, Phenoxyethanol: 0.8 };
    const total = Object.values(formulation).reduce((a,b)=>a+b,0);
    Object.keys(formulation).forEach(k => formulation[k] = formulation[k]*100/total);
  }

  showLoader("Simulation en cours...");
  try {
    let res;

    if (type === "viscosity") {
      const tMin = parseFloat(document.getElementById("simTMin")?.value)||5;
      const tMax = parseFloat(document.getElementById("simTMax")?.value)||60;
      const vRef = parseFloat(document.getElementById("simViscRef")?.value)||1000;
      const T_range = Array.from({length:20}, (_,i) => tMin + i*(tMax-tMin)/19);
      res = await apiPost("/simulate/viscosity", {formulation, T_range, ref_viscosity: vRef});
      renderSimChart(res.temperature, res.viscosity, "Temperature (°C)", "Viscosite (mPa.s)", "line", "Viscosite vs T");

    } else if (type === "release") {
      const tMax  = parseFloat(document.getElementById("simTimeMax")?.value)||24;
      const apiId = document.getElementById("simApiId")?.value||"Ibuprofen";
      const t = Array.from({length:25}, (_,i) => i*tMax/24);
      res = await apiPost("/simulate/release", {formulation, time_hours:t, api_id:apiId});
      renderSimChart(res.time_hours, res.release_pct, "Temps (h)", "Liberation (%)", "line", "Profil de liberation");

    } else if (type === "stability") {
      const months = parseFloat(document.getElementById("simMonths")?.value)||24;
      const temp   = parseFloat(document.getElementById("simTempStab")?.value)||25;
      const hum    = parseFloat(document.getElementById("simHumidity")?.value)||60;
      const t = Array.from({length:25}, (_,i) => i*months/24);
      res = await apiPost("/simulate/stability", {formulation, time_months:t, temperature_C:temp, humidity_pct:hum});
      renderSimChart(res.time_months, res.stability_pct, "Temps (mois)", "Stabilite (%)", "line", "Stabilite");

    } else if (type === "compare") {
      const forms = state.generatedFormulas.slice(0,4).map(f => f.composition);
      const labels = forms.map((_,i) => `F#${i+1}`);
      if (forms.length < 2) {
        showToast("Generez au moins 2 formulations dans l'onglet Composer", "error");
        hideLoader(); return;
      }
      res = await apiPost("/simulate/compare", {
        formulations: forms, labels,
        properties_to_compare: ["cost","density","HLB","n_components"],
      });
      renderCompareResult(res);
    }

    if (res) {
      renderSimResult(res, type);
      showToast("Simulation terminee", "success");
    }
  } catch(e) {
    showToast("Erreur simulation : " + e.message, "error");
  } finally { hideLoader(); }
}

function renderSimChart(x, y, xLabel, yLabel, type, title) {
  const card = document.getElementById("simChartCard");
  card.style.display = "block";
  destroyChart("simChart");
  const ctx = document.getElementById("simChart").getContext("2d");
  const isDecreasing = y[y.length-1] < y[0];
  const color = isDecreasing ? "#f59e0b" : "#00e5c8";

  state.charts["simChart"] = new Chart(ctx, {
    type: "line",
    data: { labels: x.map(v => typeof v==="number" ? v.toFixed(1) : v),
      datasets:[{
        label: yLabel, data: y,
        borderColor: color, backgroundColor: color.replace(")",",0.1)").replace("#","rgba("),
        borderWidth: 2.5, pointRadius: 0, tension: 0.4, fill: true,
      }]},
    options: {
      ...chartOptions(title),
      scales: {
        x: { title:{display:true,text:xLabel,color:"#7a8098",font:{size:9}},
             grid:{color:"rgba(255,255,255,.04)"}, ticks:{color:"#3a3f55",font:{size:8}} },
        y: { title:{display:true,text:yLabel,color:"#7a8098",font:{size:9}},
             grid:{color:"rgba(255,255,255,.04)"}, ticks:{color:"#3a3f55",font:{size:8}} },
      },
    },
  });
}

function renderSimResult(res, type) {
  const el = document.getElementById("simResult");
  el.style.display = "block";
  let html = "<h4>Resultats de simulation</h4>";

  if (type === "viscosity") {
    const v = res.viscosity || [];
    html += `<div class="metric-row"><span class="metric-label">Viscosite max</span>
      <span class="metric-value">${Math.max(...v).toFixed(0)} mPa.s</span></div>
      <div class="metric-row"><span class="metric-label">Viscosite min</span>
      <span class="metric-value">${Math.min(...v).toFixed(0)} mPa.s</span></div>`;
  } else if (type === "release") {
    html += `<div class="metric-row"><span class="metric-label">Modele</span>
      <span class="metric-value">${res.release_type}</span></div>
      <div class="metric-row"><span class="metric-label">t80%</span>
      <span class="metric-value">${res.t80_hours?.toFixed(1)} h</span></div>
      <div class="metric-row"><span class="metric-label">k liberation</span>
      <span class="metric-value">${res.k_release?.toFixed(4)}</span></div>
      <div class="metric-row"><span class="metric-label">Exposant n</span>
      <span class="metric-value">${res.n_exponent?.toFixed(4)}</span></div>`;
  } else if (type === "stability") {
    const q = res.stability_pct?.[res.stability_pct.length-1] || 0;
    html += `<div class="metric-row"><span class="metric-label">Stabilite finale</span>
      <span class="metric-value ${q>90?'good':q>75?'warn':'bad'}">${q.toFixed(1)}%</span></div>
      <div class="metric-row"><span class="metric-label">t90% (durabilite)</span>
      <span class="metric-value">${res.t90_months?.toFixed(1)} mois</span></div>
      <div class="metric-row"><span class="metric-label">t95% (shelf life)</span>
      <span class="metric-value good">${res.t_shelf_life?.toFixed(1)} mois</span></div>
      <div class="metric-row"><span class="metric-label">k degradation</span>
      <span class="metric-value">${res.k_degradation?.toFixed(6)}</span></div>`;
  }
  el.innerHTML = html;
}

function renderCompareResult(res) {
  const el = document.getElementById("simResult");
  el.style.display = "block";
  const results = res.results || [];
  const best    = res.best_per_property || {};

  let html = `<h4>Comparaison de ${res.n_compared} formulations</h4>`;
  results.forEach(r => {
    html += `<div style="margin-bottom:6px;padding:6px 8px;background:var(--hover);border-radius:4px">
      <div style="font-size:10px;font-weight:700;color:var(--cyan)">${r.label}</div>
      ${r.cost_index!=null?`<div class="metric-row"><span class="metric-label">Cout</span>
        <span class="metric-value ${best.cost_index===r.label?'good':''}">${r.cost_index?.toFixed(2)}</span></div>`:""}
      ${r.density!=null?`<div class="metric-row"><span class="metric-label">Densite</span>
        <span class="metric-value">${r.density?.toFixed(4)}</span></div>`:""}
      ${r.HLB!=null?`<div class="metric-row"><span class="metric-label">HLB</span>
        <span class="metric-value">${r.HLB?.toFixed(2)}</span></div>`:""}
    </div>`;
  });
  el.innerHTML = html;

  // Graphique bar chart comparaison coûts
  const card = document.getElementById("simChartCard");
  card.style.display = "block";
  destroyChart("simChart");
  const ctx = document.getElementById("simChart").getContext("2d");
  const costs = results.map(r => r.cost_index || 0);
  const colors = results.map(r =>
    best.cost_index === r.label ? "rgba(34,197,94,.8)" : "rgba(0,229,200,.5)");
  state.charts["simChart"] = new Chart(ctx, {
    type: "bar",
    data: { labels: results.map(r=>r.label),
      datasets:[{label:"Cout",data:costs,backgroundColor:colors,borderWidth:0}]},
    options: chartOptions("Comparaison des couts"),
  });
}

// ════════════════════════════════════════════════════════════════════════════
// ONGLET BASE DE DONNÉES
// ════════════════════════════════════════════════════════════════════════════

async function searchDatabase() {
  const cat  = document.getElementById("dbCategory").value;
  const text = document.getElementById("dbSearchText").value.toLowerCase();

  let data = MATERIALS_CACHE;
  if (cat) {
    data = Object.fromEntries(Object.entries(data).filter(([,v]) => v.category === cat));
  }
  if (text) {
    data = Object.fromEntries(Object.entries(data).filter(([id, v]) =>
      (v.name||id).toLowerCase().includes(text) ||
      (v.function||[]).some(f => f.toLowerCase().includes(text))
    ));
  }

  const el = document.getElementById("dbResults");
  const items = Object.entries(data);
  if (!items.length) {
    el.innerHTML = `<div class="hint" style="padding:8px">Aucun resultat</div>`;
    return;
  }
  el.innerHTML = items.map(([id, mat]) => `
    <div class="db-item" onclick="showMaterialDetail('${id}')">
      <div class="db-item-name">${mat.name || id}</div>
      <div class="db-item-meta">${mat.category} | cout: ${mat.cost_rel||"?"} | ${(mat.function||[]).slice(0,3).join(", ")}</div>
    </div>`).join("");
}

function showMaterialDetail(id) {
  const mat = MATERIALS_CACHE[id];
  if (!mat) return;
  const panel = document.getElementById("dbDetailPanel");
  const det   = document.getElementById("dbDetail");
  panel.style.display = "block";

  const fields = [
    ["Nom complet",    mat.name],
    ["Categorie",      mat.category],
    ["CAS",            mat.cas],
    ["Masse mol.",     mat.molar_mass ? mat.molar_mass + " g/mol" : "—"],
    ["Densite",        mat.density ? mat.density + " g/cm3" : "—"],
    ["Cout relatif",   mat.cost_rel],
    ["Plage typ.",     `${mat.min_pct}–${mat.max_pct}%`],
    ["Fonctions",      (mat.function||[]).join(", ")],
    ["Compatible avec",(mat.compatible_with||[]).join(", ")],
  ];

  det.innerHTML = fields.filter(([,v]) => v).map(([k,v]) =>
    `<div class="db-detail-prop"><span style="color:var(--muted)">${k}</span><span>${v}</span></div>`
  ).join("") + `
    <button class="btn btn-accent full-width" style="margin-top:8px"
      onclick="addMaterialFromDB('${id}')">
      + Ajouter a la formulation
    </button>`;
}

function addMaterialFromDB(id) {
  const mat = MATERIALS_CACHE[id] || {};
  if (state.components.find(c => c.id === id)) {
    showToast("Deja present dans la formulation", "error"); return;
  }
  state.components.push({id, min: mat.min_pct||0, max: mat.max_pct||100, fixed:false});
  renderComponentsList();
  // Aller à l'onglet Composer
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
  document.querySelector('[data-tab="compose"]').classList.add("active");
  document.getElementById("tab-compose").classList.add("active");
  showToast(`${mat.name || id} ajoute a la formulation`, "success");
}

// ════════════════════════════════════════════════════════════════════════════
// HELPERS — API
// ════════════════════════════════════════════════════════════════════════════

async function apiPost(endpoint, payload) {
  const res = await fetch(API + endpoint, {
    method:  "POST",
    headers: {"Content-Type": "application/json"},
    body:    JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({detail: res.statusText}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

async function apiGet(endpoint) {
  const res = await fetch(API + endpoint);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ── Chart.js helpers ─────────────────────────────────────────────────────────
function chartOptions(title) {
  return {
    responsive: true,
    animation:  {duration: 500},
    plugins: {
      legend: {labels:{color:"#7a8098",font:{size:9},boxWidth:10}},
      title:  {display:true,text:title,color:"#00e5c8",font:{family:"DM Mono",size:9}},
    },
  };
}

function destroyChart(id) {
  if (state.charts[id]) { state.charts[id].destroy(); delete state.charts[id]; }
}

// ── UI helpers ────────────────────────────────────────────────────────────────
function showLoader(text="Calcul...") {
  document.getElementById("loaderText").textContent = text;
  document.getElementById("loaderOverlay").style.display = "flex";
}
function hideLoader() {
  document.getElementById("loaderOverlay").style.display = "none";
}

let _toastTimer;
function showToast(msg, type="info") {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className = `toast ${type} show`;
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => el.classList.remove("show"), 3500);
}

// Init simulation params on load
document.addEventListener("DOMContentLoaded", updateSimParams);


// ════════════════════════════════════════════════════════════════════════════
// ONGLET GÉRER LA BD — CRUD matériaux & propriétés personnalisés
// ════════════════════════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("btnRefreshStats") ?.addEventListener("click", loadDbStats);
  document.getElementById("btnValidateMat")  ?.addEventListener("click", validateNewMaterial);
  document.getElementById("btnAddMat")       ?.addEventListener("click", addNewMaterial);
  document.getElementById("btnAddProp")      ?.addEventListener("click", addNewProperty);
  document.getElementById("btnDeleteItem")   ?.addEventListener("click", deleteItem);
  document.getElementById("btnExportDb")     ?.addEventListener("click", exportDb);
  document.getElementById("btnImportDb")     ?.addEventListener("click", () =>
    document.getElementById("importFileInput").click());
  document.getElementById("importFileInput") ?.addEventListener("change", importDb);

  // Charger les stats au premier affichage de l'onglet
  document.querySelector('[data-tab="manage"]')?.addEventListener("click", () => {
    if (!document.getElementById("dbStats").children.length ||
        document.getElementById("dbStats").querySelector(".hint"))
      loadDbStats();
  });
});

// ── Stats BD ─────────────────────────────────────────────────────────────────

async function loadDbStats() {
  try {
    const res = await apiGet("/db/stats");
    const cats = res.by_category || {};
    const customIds = res.custom_material_ids || [];

    document.getElementById("dbStats").innerHTML = `
      <div class="metric-row"><span class="metric-label">Total materiaux</span>
        <span class="metric-value">${res.total_materials}</span></div>
      <div class="metric-row"><span class="metric-label">BD integree</span>
        <span class="metric-value good">${res.builtin_materials}</span></div>
      <div class="metric-row"><span class="metric-label">Personnalises</span>
        <span class="metric-value cyan">${res.custom_materials}</span></div>
      <div class="metric-row"><span class="metric-label">Proprietes</span>
        <span class="metric-value">${res.total_properties} (${res.custom_properties} custom)</span></div>
      <div style="margin-top:8px;font-size:9px;color:var(--dim)">
        Categories : ${Object.entries(cats).map(([k,n])=>`${k}(${n})`).join(", ")}
      </div>
      ${customIds.length ? `<div style="margin-top:5px;font-size:9px;color:var(--cyan)">
        Custom IDs : ${customIds.join(", ")}
      </div>` : ""}`;
  } catch(e) {
    document.getElementById("dbStats").innerHTML =
      `<span class="hint">Erreur : ${e.message}</span>`;
  }
}

// ── Collecte des données du formulaire ────────────────────────────────────────

function collectMaterialData() {
  const fnRaw   = document.getElementById("newMatFunctions").value;
  const compRaw = document.getElementById("newMatCompat").value;
  const hlbVal  = parseFloat(document.getElementById("newMatHLB").value);
  return {
    name:            document.getElementById("newMatName").value.trim(),
    category:        document.getElementById("newMatCat").value,
    cas:             document.getElementById("newMatCAS").value.trim() || undefined,
    density:         parseFloat(document.getElementById("newMatDensity").value) || 1.0,
    cost_rel:        parseFloat(document.getElementById("newMatCost").value) || 10,
    HLB:             isNaN(hlbVal) ? undefined : hlbVal,
    min_pct:         parseFloat(document.getElementById("newMatMin").value) || 0,
    max_pct:         parseFloat(document.getElementById("newMatMax").value) || 100,
    function:        fnRaw.split(",").map(s=>s.trim()).filter(Boolean),
    compatible_with: compRaw.split(",").map(s=>s.trim()).filter(Boolean),
    source:          document.getElementById("newMatSource").value.trim() || "user",
  };
}

// ── Validation avant ajout ────────────────────────────────────────────────────

async function validateNewMaterial() {
  const data = collectMaterialData();
  if (!data.name) { showToast("Le nom est obligatoire", "error"); return; }
  showLoader("Validation...");
  try {
    const res = await apiPost("/db/materials/validate", data);
    const el  = document.getElementById("addMatResult");
    el.style.display = "block";

    const errHtml  = (res.errors||[]).map(e => `<div style="color:var(--red)">✗ ${e}</div>`).join("");
    const warnHtml = (res.warnings||[]).map(w => `<div style="color:var(--amber)">⚠ ${w}</div>`).join("");
    const suggHtml = (res.suggestions||[]).map(s => `<div style="color:var(--dim)">💡 ${s}</div>`).join("");

    el.innerHTML = `<h4>${res.valid ? "✓ Valide" : "✗ Erreurs"}</h4>
      ${errHtml}${warnHtml}${suggHtml}
      ${res.valid ? '<div class="hint" style="margin-top:4px">Pret a ajouter !</div>' : ""}`;

    showToast(res.valid ? "Validation reussie" : "Corriger les erreurs", res.valid?"success":"error");
  } catch(e) {
    showToast("Erreur validation : " + e.message, "error");
  } finally { hideLoader(); }
}

// ── Ajout d'un matériau ───────────────────────────────────────────────────────

async function addNewMaterial() {
  const id   = document.getElementById("newMatId").value.trim();
  const data = collectMaterialData();

  if (!id)        { showToast("L'identifiant est obligatoire", "error"); return; }
  if (!data.name) { showToast("Le nom est obligatoire", "error"); return; }

  showLoader("Ajout en cours...");
  try {
    const res = await fetch(`${API}/db/materials/custom?material_id=${encodeURIComponent(id)}`, {
      method:  "POST",
      headers: {"Content-Type": "application/json"},
      body:    JSON.stringify(data),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(JSON.stringify(json.detail || json.error));

    const el = document.getElementById("addMatResult");
    el.style.display = "block";
    el.innerHTML = `<h4>✓ Materiau ajoute</h4>
      <div class="metric-row"><span class="metric-label">ID</span>
        <span class="metric-value good">${json.id}</span></div>
      <div class="metric-row"><span class="metric-label">Nom</span>
        <span class="metric-value">${json.data?.name}</span></div>
      <div class="metric-row"><span class="metric-label">Categorie</span>
        <span class="metric-value">${json.data?.category}</span></div>`;

    // Mettre à jour le cache local
    MATERIALS_CACHE[id] = json.data;
    populateComponentSelect();
    loadDbStats();
    showToast(`${data.name} ajoute a la BD !`, "success");

    // Reset formulaire
    ["newMatId","newMatName","newMatCAS","newMatFunctions","newMatCompat","newMatSource"]
      .forEach(field => { document.getElementById(field).value = ""; });

  } catch(e) {
    showToast("Erreur ajout : " + e.message, "error");
  } finally { hideLoader(); }
}

// ── Ajout d'une propriété ─────────────────────────────────────────────────────

async function addNewProperty() {
  const id      = document.getElementById("newPropId").value.trim();
  const name    = document.getElementById("newPropName").value.trim();
  const unit    = document.getElementById("newPropUnit").value.trim();
  const method  = document.getElementById("newPropMethod").value.trim();
  const factors = document.getElementById("newPropFactors").value.split(",").map(s=>s.trim()).filter(Boolean);
  const pMin    = parseFloat(document.getElementById("newPropMin").value) || 0;
  const pMax    = parseFloat(document.getElementById("newPropMax").value) || 100;

  if (!id || !name || !unit) {
    showToast("ID, nom et unite sont obligatoires", "error"); return;
  }

  showLoader("Ajout propriete...");
  try {
    const res = await fetch(`${API}/db/properties/custom?prop_id=${encodeURIComponent(id)}`, {
      method:  "POST",
      headers: {"Content-Type": "application/json"},
      body:    JSON.stringify({ name, unit, range:[pMin,pMax], method, key_factors:factors }),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(JSON.stringify(json.detail || json.error));

    const el = document.getElementById("addPropResult");
    el.style.display = "block";
    el.innerHTML = `<h4>✓ Propriete ajoutee</h4>
      <div class="metric-row"><span class="metric-label">ID</span>
        <span class="metric-value good">${json.id}</span></div>
      <div class="metric-row"><span class="metric-label">Nom</span>
        <span class="metric-value">${json.data?.name}</span></div>
      <div class="metric-row"><span class="metric-label">Unite</span>
        <span class="metric-value">${json.data?.unit}</span></div>`;

    // Mettre à jour les checkboxes de propriétés
    PROPERTIES_CACHE[id] = json.data;
    populatePropertiesChecks();
    loadDbStats();
    showToast(`${name} ajoutee a la BD !`, "success");

    ["newPropId","newPropName","newPropUnit","newPropMethod","newPropFactors"]
      .forEach(f => { document.getElementById(f).value = ""; });

  } catch(e) {
    showToast("Erreur ajout propriete : " + e.message, "error");
  } finally { hideLoader(); }
}

// ── Suppression ───────────────────────────────────────────────────────────────

async function deleteItem() {
  const id   = document.getElementById("deleteId").value.trim();
  const type = document.getElementById("deleteType").value;
  if (!id) { showToast("Entrez un ID a supprimer", "error"); return; }

  const endpoint = type === "material"
    ? `/db/materials/custom/${encodeURIComponent(id)}`
    : `/db/properties/custom/${encodeURIComponent(id)}`;

  if (!confirm(`Supprimer le ${type} '${id}' ? Cette action est irreversible.`)) return;

  showLoader("Suppression...");
  try {
    const res = await fetch(API + endpoint, {method: "DELETE"});
    const json = await res.json();
    if (!res.ok) throw new Error(JSON.stringify(json.detail || json.error));

    if (type === "material") {
      delete MATERIALS_CACHE[id];
      populateComponentSelect();
    } else {
      delete PROPERTIES_CACHE[id];
      populatePropertiesChecks();
    }
    loadDbStats();
    document.getElementById("deleteId").value = "";
    showToast(`${type} '${id}' supprime`, "success");
  } catch(e) {
    showToast("Erreur suppression : " + e.message, "error");
  } finally { hideLoader(); }
}

// ── Export JSON ───────────────────────────────────────────────────────────────

async function exportDb() {
  showLoader("Export...");
  try {
    const data = await apiGet("/db/custom/export");
    const blob = new Blob([JSON.stringify(data, null, 2)], {type: "application/json"});
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `FormulationAI_BD_${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("BD personnalisee exportee", "success");
  } catch(e) {
    showToast("Erreur export : " + e.message, "error");
  } finally { hideLoader(); }
}

// ── Import JSON ───────────────────────────────────────────────────────────────

async function importDb(event) {
  const file = event.target.files[0];
  if (!file) return;
  showLoader("Import...");
  try {
    const text = await file.text();
    const data = JSON.parse(text);
    const res  = await apiPost("/db/custom/import", {...data, mode: "merge"});

    // Recharger le cache
    await loadDatabaseCache();
    loadDbStats();
    showToast(`Import reussi : ${res.n_materials} materiaux, ${res.n_properties} proprietes`, "success");
  } catch(e) {
    showToast("Erreur import : " + e.message, "error");
  } finally {
    hideLoader();
    event.target.value = "";
  }
}


// ════════════════════════════════════════════════════════════════════════════
// ONGLET CI LOCAL — Matières premières, FCFA, Rapport PDF
// ════════════════════════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("btnCalcFcfa")      ?.addEventListener("click", calcFcfa);
  document.getElementById("btnGeneratePDF")   ?.addEventListener("click", generatePDFReport);
  document.getElementById("btnLoadCiMats")    ?.addEventListener("click", loadCiMaterials);
  document.getElementById("btnLoadSuppliers") ?.addEventListener("click", loadSuppliers);

  // Charger les stats CI au premier clic sur l'onglet
  document.querySelector('[data-tab="ci"]')?.addEventListener("click", () => {
    loadCiStats();
    // Pré-remplir le nom de formulation depuis l'onglet Composer
    const fn = document.getElementById("pdfFormName");
    if (fn && !fn.value) fn.value = "Ma Formulation CI";
  });
});

// ── Stats CI ─────────────────────────────────────────────────────────────────
async function loadCiStats() {
  const el = document.getElementById("ciStats");
  if (!el || el.textContent !== "Chargement...") return;
  try {
    const res = await apiGet("/db/ci/materials");
    const mats = res.materials || {};
    const local = Object.values(mats).filter(m => m.origin_ci).length;
    el.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-top:4px">
        <div style="text-align:center;padding:6px;background:rgba(0,154,61,.1);border-radius:4px">
          <div style="font-size:18px;font-weight:800;color:#009a3d">${res.n}</div>
          <div style="font-size:9px;color:var(--muted)">Total ingredients</div>
        </div>
        <div style="text-align:center;padding:6px;background:rgba(240,135,0,.1);border-radius:4px">
          <div style="font-size:18px;font-weight:800;color:#f08700">${local}</div>
          <div style="font-size:9px;color:var(--muted)">Produits en CI</div>
        </div>
        <div style="text-align:center;padding:6px;background:rgba(0,229,200,.1);border-radius:4px">
          <div style="font-size:18px;font-weight:800;color:var(--cyan)">${res.n - local}</div>
          <div style="font-size:9px;color:var(--muted)">Importes</div>
        </div>
      </div>`;
  } catch(e) {
    el.textContent = "Erreur chargement stats CI";
  }
}

// ── Calcul FCFA ───────────────────────────────────────────────────────────────
async function calcFcfa() {
  const batchKg = parseFloat(document.getElementById("fcfaBatchKg").value) || 10;

  // Obtenir la formulation (générée ou contraintes moyennées)
  let formulation = {};
  if (state.generatedFormulas.length > 0) {
    formulation = state.generatedFormulas[0].composition;
  } else if (state.components.length > 0) {
    const total = state.components.reduce((s,c) => s+(c.min+c.max)/2, 0);
    state.components.forEach(c => {
      formulation[c.id] = ((c.min+c.max)/2) * 100 / total;
    });
  } else {
    showToast("Ajoutez des composants dans l'onglet Composer", "error"); return;
  }

  showLoader("Calcul en FCFA...");
  try {
    const res = await apiPost("/db/ci/cost_fcfa", {formulation, batch_kg: batchKg});
    renderFcfaResult(res);
    showToast(`Cout calcule : ${res.cost_per_kg_fmt}`, "success");
  } catch(e) {
    showToast("Erreur FCFA : " + e.message, "error");
  } finally { hideLoader(); }
}

function renderFcfaResult(res) {
  const el = document.getElementById("fcfaResult");
  el.style.display = "block";

  const detail  = res.detail || {};
  const estIds  = res.estimated_ids || [];
  const sorted  = Object.entries(detail).sort((a,b) => b[1].cost_fcfa - a[1].cost_fcfa);

  const rows = sorted.map(([id, d]) => {
    const isEst  = estIds.includes(id);
    const mat    = MATERIALS_CACHE[id] || {};
    const name   = (mat.name || id).substring(0, 22);
    const srcBadge = isEst
      ? '<span style="font-size:8px;color:var(--amber);font-style:italic">estimé</span>'
      : '<span style="font-size:8px;color:var(--green)">prix CI</span>';
    return `<div style="display:flex;gap:4px;align-items:center;padding:3px 0;border-bottom:1px solid var(--border);font-size:9px;font-family:var(--mono)">
      <span style="flex:1;color:var(--text)">${name}</span>
      <span style="color:var(--muted);width:30px;text-align:right">${d.pct.toFixed(1)}%</span>
      <span style="color:var(--muted);width:38px;text-align:right">${d.price_fcfa_kg.toLocaleString('fr-FR')} F</span>
      <span style="color:var(--cyan);width:55px;text-align:right;font-weight:700">${d.cost_fcfa.toLocaleString('fr-FR')} F</span>
      ${srcBadge}
    </div>`;
  }).join("");

  el.innerHTML = `
    <div style="background:rgba(0,154,61,.12);border:1px solid rgba(0,154,61,.3);border-radius:6px;padding:10px">
      <div style="font-size:13px;font-weight:800;color:#009a3d;margin-bottom:4px">
        ${res.cost_per_kg_fmt} <span style="font-size:10px;font-weight:400;color:var(--muted)">= coût/kg</span>
      </div>
      <div style="font-size:11px;color:var(--text)">
        Batch ${res.batch_kg} kg → <strong>${res.total_fcfa_fmt}</strong>
      </div>
      <div style="font-size:9px;color:var(--muted);margin-top:3px">${res.currency}</div>
    </div>
    <div style="margin-top:8px;background:var(--input);border-radius:4px;padding:8px">
      <div style="display:flex;gap:4px;font-size:9px;font-family:var(--mono);color:var(--dim);margin-bottom:4px;border-bottom:1px solid var(--border);padding-bottom:3px">
        <span style="flex:1">Ingredient</span>
        <span style="width:30px;text-align:right">%</span>
        <span style="width:38px;text-align:right">FCFA/kg</span>
        <span style="width:55px;text-align:right">Coût</span>
        <span style="width:40px"></span>
      </div>
      ${rows}
    </div>
    ${estIds.length ? `<div class="hint" style="margin-top:6px;color:var(--amber)">
      ⚠ Prix estimés pour : ${estIds.join(", ")}. Consulter les fournisseurs CI pour tarifs réels.
    </div>` : ""}`;
}

// ── Rapport PDF ───────────────────────────────────────────────────────────────
async function generatePDFReport() {
  // Obtenir la formulation
  let formulation = {};
  if (state.generatedFormulas.length > 0) {
    formulation = state.generatedFormulas[0].composition;
  } else if (state.components.length > 0) {
    const total = state.components.reduce((s,c) => s+(c.min+c.max)/2, 0);
    state.components.forEach(c => {
      formulation[c.id] = ((c.min+c.max)/2) * 100 / total;
    });
  } else {
    showToast("Ajoutez des composants dans l'onglet Composer", "error"); return;
  }

  const formName = document.getElementById("pdfFormName").value  || "Ma Formulation";
  const company  = document.getElementById("pdfCompany").value   || "Mon Entreprise";
  const prepBy   = document.getElementById("pdfPreparedBy").value|| "";
  const batchKg  = parseFloat(document.getElementById("pdfBatchKg").value) || 10;
  const inclAI   = document.getElementById("pdfIncludeAI").checked;
  const app      = document.getElementById("applicationSelect").value || "cosmetique";

  const pdfStatus = document.getElementById("pdfStatus");
  pdfStatus.style.display = "none";

  showLoader("Génération du rapport PDF en cours...");
  try {
    const response = await fetch(`${API}/report/pdf`, {
      method:  "POST",
      headers: {"Content-Type": "application/json"},
      body:    JSON.stringify({
        formulation,
        batch_kg:         batchKg,
        formulation_name: formName,
        company_name:     company,
        prepared_by:      prepBy,
        application:      app,
        include_analysis: inclAI,
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({detail: response.statusText}));
      throw new Error(err.detail || `HTTP ${response.status}`);
    }

    // Télécharger le PDF
    const blob     = await response.blob();
    const url      = URL.createObjectURL(blob);
    const a        = document.createElement("a");
    const filename = formName.replace(/\s+/g,"_").substring(0,40) + "_rapport.pdf";
    a.href         = url;
    a.download     = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    pdfStatus.style.display = "block";
    pdfStatus.innerHTML = `
      <h4 style="color:#009a3d">✓ Rapport PDF genere</h4>
      <div class="metric-row"><span class="metric-label">Fichier</span>
        <span class="metric-value good">${filename}</span></div>
      <div class="metric-row"><span class="metric-label">Batch</span>
        <span class="metric-value">${batchKg} kg</span></div>`;

    showToast("Rapport PDF téléchargé !", "success");
  } catch(e) {
    showToast("Erreur PDF : " + e.message, "error");
    console.error(e);
  } finally { hideLoader(); }
}

// ── Liste matériaux CI ────────────────────────────────────────────────────────
async function loadCiMaterials() {
  const localOnly = document.getElementById("ciFilterOrigin").value === "local";
  showLoader("Chargement ingredients CI...");
  try {
    const res  = await apiGet("/db/ci/materials" + (localOnly ? "?local_only=true" : ""));
    const mats = res.materials || {};
    const el   = document.getElementById("ciMatsList");

    el.innerHTML = Object.entries(mats).map(([id, mat]) => {
      const priceLine = mat.price_fcfa_kg
        ? `<span style="color:#009a3d;font-weight:700">${mat.price_fcfa_kg.toLocaleString('fr-FR')} FCFA/kg</span>`
        + (mat.price_min_fcfa ? ` <span style="font-size:8px;color:var(--dim)">[${mat.price_min_fcfa.toLocaleString('fr-FR')}–${mat.price_max_fcfa.toLocaleString('fr-FR')}]</span>` : "")
        : '<span style="color:var(--muted)">Prix non renseigne</span>';

      const localBadge = mat.origin_ci
        ? '<span style="background:rgba(0,154,61,.15);color:#009a3d;padding:1px 5px;border-radius:10px;font-size:8px">🇨🇮 CI</span>'
        : '<span style="background:var(--hover);color:var(--dim);padding:1px 5px;border-radius:10px;font-size:8px">Import</span>';

      const availColor = mat.local_availability === "facile" ? "#009a3d"
                       : mat.local_availability === "moderee" ? "#f08700" : "#cc4444";

      return `<div class="db-item" onclick="showCiDetail('${id}')">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div class="db-item-name">${mat.name || id}</div>
          <div style="display:flex;gap:4px;align-items:center">${localBadge}</div>
        </div>
        <div class="db-item-meta">
          ${mat.category} | ${priceLine}
          | Dispo : <span style="color:${availColor}">${mat.local_availability || "?"}</span>
        </div>
        ${mat.name_local ? `<div style="font-size:9px;font-style:italic;color:var(--dim)">Nom local : ${mat.name_local}</div>` : ""}
      </div>`;
    }).join("") || '<div class="hint" style="padding:8px">Aucun ingredient trouve</div>';

    showToast(`${Object.keys(mats).length} ingredients charges`, "success");
  } catch(e) {
    showToast("Erreur chargement CI : " + e.message, "error");
  } finally { hideLoader(); }
}

function showCiDetail(id) {
  // Récupérer depuis le cache local (CI materials) et afficher une modale simple
  apiGet(`/db/materials/${id}`).then(mat => {
    const suppliers = (mat.suppliers_ci || []).map(s =>
      `<div style="padding:4px 0;border-bottom:1px solid var(--border)">
        <div style="font-size:10px;font-weight:600;color:var(--text)">${s.name}</div>
        <div style="font-size:9px;color:var(--muted)">${s.city} | ${s.contact || ""}</div>
        ${s.notes ? `<div style="font-size:9px;font-style:italic;color:var(--dim)">${s.notes}</div>` : ""}
      </div>`).join("");

    const priceLine = mat.price_fcfa_kg
      ? `<strong style="color:#009a3d">${mat.price_fcfa_kg.toLocaleString('fr-FR')} FCFA/kg</strong>`
      + (mat.price_min_fcfa ? ` (fourchette : ${mat.price_min_fcfa.toLocaleString('fr-FR')}–${mat.price_max_fcfa.toLocaleString('fr-FR')} FCFA/kg)` : "")
      : "N/A";

    alert(`${mat.name}\n\nCategorie : ${mat.category}\nPrix CI : ${mat.price_fcfa_kg ? mat.price_fcfa_kg + " FCFA/kg" : "N/A"}\nPlage : ${mat.min_pct}–${mat.max_pct}%\nFonctions : ${(mat.function||[]).join(", ")}\n${mat.notes_technique || ""}`);

    // Proposer d'ajouter à la formulation
    if (confirm(`Ajouter "${mat.name}" à la formulation ?`)) {
      if (!state.components.find(c => c.id === id)) {
        state.components.push({id, min: mat.min_pct||0, max: mat.max_pct||100, fixed:false});
        MATERIALS_CACHE[id] = mat;
        populateComponentSelect();
        renderComponentsList();
        showToast(`${mat.name} ajouté à la formulation`, "success");
      } else {
        showToast("Déjà dans la formulation", "info");
      }
    }
  }).catch(e => showToast("Erreur detail : " + e.message, "error"));
}

// ── Fournisseurs ──────────────────────────────────────────────────────────────
async function loadSuppliers() {
  showLoader("Chargement fournisseurs...");
  try {
    const res       = await apiGet("/db/ci/suppliers");
    const suppliers = res.suppliers || [];
    const el        = document.getElementById("suppliersList");

    el.innerHTML = suppliers.map(s => `
      <div style="background:var(--input);border:1px solid var(--border);border-left:3px solid #009a3d;border-radius:4px;padding:8px 10px;margin-bottom:6px">
        <div style="font-size:11px;font-weight:700;color:var(--text)">${s.name}</div>
        <div style="font-size:9px;color:#009a3d;margin-top:1px">${s.city}</div>
        <div style="font-size:9px;color:var(--muted);margin-top:2px">${s.specialty || ""}</div>
        ${s.phone ? `<div style="font-size:9px;color:var(--cyan);margin-top:2px">📞 ${s.phone}</div>` : ""}
        ${s.min_order ? `<div style="font-size:8px;color:var(--dim)">Commande min : ${s.min_order}</div>` : ""}
        ${s.notes ? `<div style="font-size:8px;font-style:italic;color:var(--dim);margin-top:2px">${s.notes}</div>` : ""}
      </div>`).join("");

    showToast(`${suppliers.length} fournisseurs charges`, "success");
  } catch(e) {
    showToast("Erreur fournisseurs : " + e.message, "error");
  } finally { hideLoader(); }
}


// ════════════════════════════════════════════════════════════════════════════
// DEVISE — sélecteur global
// ════════════════════════════════════════════════════════════════════════════

let currentCurrency = "FCFA";
const RATES = { FCFA: 1, EUR: 655.957, USD: 600 };
const SYMS  = { FCFA: "FCFA", EUR: "€", USD: "$" };

function setCurrency(currency) {
  currentCurrency = currency;
  // Mettre à jour l'affichage des coûts partout
  refreshCostDisplays();
}

function formatPrice(amount_fcfa, currency) {
  currency = currency || currentCurrency;
  const rate = RATES[currency] || 1;
  const sym  = SYMS[currency]  || currency;
  const converted = amount_fcfa / rate;
  if (currency === "FCFA") return `${Math.round(converted).toLocaleString("fr-FR")} ${sym}`;
  return `${converted.toFixed(2)} ${sym}`;
}

function refreshCostDisplays() {
  // Re-rendre les formulations si déjà générées
  if (state.lastGenerateResult) renderFormulations(state.lastGenerateResult);
}

// Récupérer les taux depuis l'API
async function loadExchangeRates() {
  try {
    const res = await apiGet("/currency/rates");
    Object.assign(RATES, res.rates || {});
  } catch { /* offline — utiliser taux locaux */ }
}

// ════════════════════════════════════════════════════════════════════════════
// ONGLET RAPPORT PDF
// ════════════════════════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("btnRptPreview") ?.addEventListener("click", previewReport);
  document.getElementById("btnRptGenerate")?.addEventListener("click", generateReport);

  // Boutons devise rapport
  document.querySelectorAll(".rpt-currency").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".rpt-currency").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });

  // Sync sélecteur de devise header avec sélecteur rapport
  document.getElementById("currencySelect")?.addEventListener("change", e => {
    setCurrency(e.target.value);
    document.querySelectorAll(".rpt-currency").forEach(b => {
      b.classList.toggle("active", b.dataset.cur === e.target.value);
    });
  });

  loadExchangeRates();
});

// ── Aperçu ────────────────────────────────────────────────────────────────────
function previewReport() {
  const panel = document.getElementById("rptPreviewPanel");
  const prev  = document.getElementById("rptPreview");
  panel.style.display = "block";

  const nForms = state.generatedFormulas.length;
  const hasOpt = !!state.lastOptResult;
  const rptCur = document.querySelector(".rpt-currency.active")?.dataset.cur || "FCFA";

  const sections = [...document.querySelectorAll(".rpt-section:checked")]
    .map(c => c.nextSibling?.textContent?.trim() || c.id);

  prev.innerHTML = `
    <div style="color:var(--cyan);font-weight:700;margin-bottom:6px">
      ${document.getElementById("rptCompany").value || "Entreprise"}
    </div>
    Auteur : ${document.getElementById("rptAuthor").value || "—"}<br>
    Projet : ${document.getElementById("rptProject").value || "—"}<br>
    Devise : ${rptCur} | Orientation : ${document.getElementById("rptOrientation").value}<br>
    <br>
    Formulations disponibles : ${nForms} generees${hasOpt?" + 1 optimisee":""}<br>
    Sections : ${sections.join(", ")}<br>
    <br>
    <span style="color:${nForms>0?'var(--green)':'var(--amber)'}">
      ${nForms>0?"✓ Pret a generer":"⚠ Generez des formulations dans l'onglet Composer"}
    </span>`;
}

// ── Génération PDF ────────────────────────────────────────────────────────────
async function generateReport() {
  if (!state.generatedFormulas.length && !state.lastOptResult) {
    showToast("Generez d'abord des formulations dans l'onglet Composer", "error"); return;
  }

  showLoader("Chargement jsPDF...");
  try {
    if (!window.jspdf) {
      await loadScript("https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js");
      await loadScript("https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js");
    }
    if (!window.jspdf?.jsPDF) {
      showToast("Impossible de charger jsPDF", "error"); hideLoader(); return;
    }

    showLoader("Generation du rapport PDF...");

    const { jsPDF } = window.jspdf;
    const isLandscape = document.getElementById("rptOrientation").value === "landscape";
    const doc = new jsPDF({ orientation: isLandscape?"l":"p", unit:"mm", format:"a4" });

    const PW  = doc.internal.pageSize.getWidth();
    const PH  = doc.internal.pageSize.getHeight();
    const ML  = 15, MR = 15;
    const CW  = PW - ML - MR;
    let Y     = 15;

    // Infos rapport
    const company  = sanitize(document.getElementById("rptCompany").value  || "Entreprise");
    const author   = sanitize(document.getElementById("rptAuthor").value   || "");
    const project  = sanitize(document.getElementById("rptProject").value  || "Formulation");
    const city     = sanitize(document.getElementById("rptCity").value     || "Abidjan");
    const desc     = sanitize(document.getElementById("rptDescription").value || "");
    const rptCur   = document.querySelector(".rpt-currency.active")?.dataset.cur || "FCFA";
    const today    = new Date().toLocaleDateString("fr-FR", {day:"2-digit",month:"long",year:"numeric"});

    // Quelle formulation afficher
    const fIdx     = document.getElementById("rptFormulationIdx").value;
    let   mainForm = null;
    if (fIdx === "opt" && state.lastOptResult) {
      mainForm = { composition: state.lastOptResult.composition,
                   cost_index: state.lastOptResult.cost_index,
                   density_est: state.lastOptResult.density_est,
                   HLB_avg: state.lastOptResult.HLB_avg,
                   label: "Formulation optimisee" };
    } else {
      const idx = parseInt(fIdx) || 0;
      mainForm = state.generatedFormulas[idx] || state.generatedFormulas[0];
      if (mainForm) mainForm.label = `Formulation #${idx+1}`;
    }

    // Palette
    const C = {
      cyan:  [0,229,200], dark: [7,9,15], card: [14,17,32],
      white: [255,255,255], light:[245,247,252],
      muted: [100,110,140], green:[34,197,94],
      amber: [245,158,11],  red:  [239,68,68],
    };

    function newPage() {
      footerPage();
      doc.addPage();
      Y = 15;
      headerPage();
    }
    function chk(n) { if (Y + n > PH - 18) newPage(); }

    function headerPage() {
      doc.setFillColor(...C.dark);
      doc.rect(0, 0, PW, 9, "F");
      doc.setFontSize(7); doc.setFont("helvetica","bold");
      doc.setTextColor(...C.cyan);
      doc.text("FormulationAI", ML, 6.5);
      doc.setFont("helvetica","normal"); doc.setTextColor(...C.muted);
      doc.text(company + " — " + project, PW - MR, 6.5, {align:"right"});
      Y = 16;
    }

    function footerPage() {
      const pg = doc.internal.getNumberOfPages();
      doc.setPage(pg);
      doc.setDrawColor(...C.muted); doc.setLineWidth(0.2);
      doc.line(ML, PH - 10, PW - MR, PH - 10);
      doc.setFontSize(7); doc.setFont("helvetica","normal");
      doc.setTextColor(...C.muted);
      doc.text(`FormulationAI — ${company} — Confidentiel`, ML, PH - 6);
      doc.text(`Page ${pg}`, PW - MR, PH - 6, {align:"right"});
    }

    function secTitle(txt) {
      chk(12); Y += 2;
      doc.setFillColor(...C.cyan);
      doc.rect(ML, Y, CW, 7.5, "F");
      doc.setFontSize(9.5); doc.setFont("helvetica","bold");
      doc.setTextColor(...C.dark);
      doc.text(sanitize(txt), ML + 3, Y + 5.5);
      Y += 11;
    }

    function kv(label, value, valColor) {
      chk(7);
      doc.setFontSize(8.5); doc.setFont("helvetica","normal");
      doc.setTextColor(...C.muted);
      doc.text(sanitize(String(label)), ML + 2, Y);
      doc.setFont("helvetica","bold");
      doc.setTextColor(...(valColor || C.dark));
      doc.text(sanitize(String(value ?? "—")), ML + CW * 0.5, Y);
      doc.setDrawColor(...C.light); doc.setLineWidth(0.15);
      doc.line(ML, Y+1.5, ML+CW, Y+1.5);
      Y += 7;
    }

    function para(txt, sz, color) {
      if (!txt) return;
      const clean = sanitize(txt);
      chk(7);
      doc.setFontSize(sz||8.5); doc.setFont("helvetica","normal");
      doc.setTextColor(...(color||C.dark));
      const lines = doc.splitTextToSize(clean, CW - 4);
      chk(lines.length * 5);
      doc.text(lines, ML + 2, Y);
      Y += lines.length * ((sz||8.5) * 0.45) + 3;
    }

    // ══════════════════════════════════════════════════════════════════════
    // PAGE DE GARDE
    // ══════════════════════════════════════════════════════════════════════

    doc.setFillColor(...C.dark); doc.rect(0,0,PW,PH,"F");
    doc.setFillColor(...C.cyan); doc.rect(0,0,PW,3,"F");
    doc.setFillColor(...C.cyan); doc.rect(0,PH-3,PW,3,"F");

    // Logo
    doc.setFontSize(34); doc.setFont("helvetica","bold");
    doc.setTextColor(...C.cyan);
    doc.text("Formulation", PW/2 - 18, PH*0.22, {align:"center"});
    doc.setTextColor(...C.white);
    doc.text("AI", PW/2 + 33, PH*0.22, {align:"center"});
    doc.setFontSize(9); doc.setFont("helvetica","normal");
    doc.setTextColor(...C.muted);
    doc.text("Moteur de formulation chimique assiste par IA", PW/2, PH*0.22+8, {align:"center"});

    // Boite titre
    doc.setFillColor(14,17,32); doc.setDrawColor(...C.cyan); doc.setLineWidth(0.4);
    doc.roundedRect(ML+8, PH*0.30, CW-16, 28, 2, 2, "FD");
    doc.setFontSize(14); doc.setFont("helvetica","bold"); doc.setTextColor(...C.white);
    const titleLines = doc.splitTextToSize(sanitize(project), CW-24);
    doc.text(titleLines, PW/2, PH*0.30+10, {align:"center"});

    // Métadonnées
    const meta = [
      ["Entreprise", company], ["Formulateur", author||"—"],
      ["Reference",  project], ["Date",        today],
      ["Ville",      city],    ["Devise",       rptCur],
    ];
    let yM = PH*0.66;
    meta.forEach(([k,v]) => {
      doc.setFontSize(8.5); doc.setFont("helvetica","bold");
      doc.setTextColor(...C.muted);
      doc.text(k+" :", PW/2-8, yM, {align:"right"});
      doc.setFont("helvetica","normal"); doc.setTextColor(...C.white);
      doc.text(sanitize(v), PW/2-4, yM);
      yM += 8.5;
    });

    if (desc) {
      doc.setFontSize(8); doc.setFont("helvetica","italic");
      doc.setTextColor(...C.muted);
      const dl = doc.splitTextToSize(sanitize(desc), CW-20);
      doc.text(dl, PW/2, yM+4, {align:"center"});
    }

    // ══════════════════════════════════════════════════════════════════════
    // PAGES CONTENU
    // ══════════════════════════════════════════════════════════════════════
    doc.addPage();
    headerPage();

    const sectionChecked = id => document.getElementById(id)?.checked;

    // ── Section 1 : Composition ────────────────────────────────────────────
    if (mainForm && sectionChecked("rpt_composition")) {
      secTitle("1. Composition de la formulation");
      kv("Reference", mainForm.label || "Formulation");
      kv("N composants", Object.keys(mainForm.composition||{}).length);

      // Tableau composition
      chk(20);
      const compEntries = Object.entries(mainForm.composition||{})
        .sort((a,b) => b[1]-a[1]);
      const tableData = compEntries.map(([id, pct]) => {
        const mat = MATERIALS_CACHE[id] || {};
        const isCI = mat.origin?.includes("Cote d'Ivoire") ||
                     mat.origin?.includes("CI") ||
                     mat._source?.includes("CI") ? "✓" : "";
        return [
          sanitize(mat.name || id),
          sanitize(mat.category || "?"),
          pct.toFixed(2) + " %",
          isCI,
        ];
      });

      doc.autoTable({
        startY: Y,
        head:   [["Matiere premiere", "Categorie", "Pourcentage", "Local CI"]],
        body:   tableData,
        theme:  "grid",
        headStyles: {fillColor: C.dark, textColor: C.cyan, fontSize: 8, fontStyle:"bold"},
        bodyStyles: {fontSize: 8, textColor: C.dark},
        alternateRowStyles: {fillColor: [245,247,252]},
        columnStyles: {
          0:{cellWidth:CW*0.45},
          1:{cellWidth:CW*0.20},
          2:{cellWidth:CW*0.18, halign:"center"},
          3:{cellWidth:CW*0.12, halign:"center", textColor:C.green},
        },
        margin: {left:ML, right:MR},
      });
      Y = doc.lastAutoTable.finalY + 6;
    }

    // ── Section 2 : Analyse des coûts ────────────────────────────────────
    if (mainForm && sectionChecked("rpt_costs")) {
      chk(40); secTitle("2. Analyse des couts");
      try {
        const priceRes = await apiPost("/currency/price", {
          formulation: mainForm.composition, currency: rptCur
        });
        kv("Cout total (" + rptCur + "/kg)",
           formatPrice(priceRes.total_FCFA_per_kg, rptCur),
           C.cyan);
        kv("Cout index relatif", mainForm.cost_index?.toFixed(2));
        kv("Densite estimee", (mainForm.density_est?.toFixed(4)||"—") + " g/cm3");

        // Tableau coûts détaillés
        chk(20);
        const costData = (priceRes.detail||[]).slice(0,15).map(d => [
          sanitize(d.name),
          d.pct?.toFixed(2) + "%",
          formatPrice(d.price_kg, rptCur) + "/kg",
          formatPrice(d.cost_contribution_FCFA, rptCur),
        ]);
        doc.autoTable({
          startY: Y,
          head:   [["Ingredient","Quantite","Prix unitaire","Contribution"]],
          body:   costData,
          theme:  "striped",
          headStyles: {fillColor:C.card, textColor:C.amber, fontSize:7.5, fontStyle:"bold"},
          bodyStyles: {fontSize:7.5, textColor:C.dark},
          alternateRowStyles: {fillColor:[245,247,252]},
          margin: {left:ML, right:MR},
        });
        Y = doc.lastAutoTable.finalY + 6;
      } catch(e) {
        para("Calcul des couts non disponible : " + e.message, 8, C.muted);
      }
    }

    // ── Section 3 : Propriétés estimées ──────────────────────────────────
    if (mainForm && sectionChecked("rpt_properties")) {
      chk(40); secTitle("3. Proprietes estimees");
      if (mainForm.HLB_avg != null) kv("HLB moyen", mainForm.HLB_avg?.toFixed(2));
      kv("Type emulsion probable", mainForm.HLB_avg < 6 ? "W/O" : mainForm.HLB_avg > 10 ? "O/W" : "intermediaire");
      kv("Densite", (mainForm.density_est?.toFixed(4)||"—") + " g/cm3");

      // Fractions par categorie
      const comp = mainForm.composition || {};
      const catFrac = {};
      Object.entries(comp).forEach(([id,pct]) => {
        const cat = MATERIALS_CACHE[id]?.category || "?";
        catFrac[cat] = (catFrac[cat]||0) + pct;
      });
      Object.entries(catFrac).sort((a,b)=>b[1]-a[1]).forEach(([cat,pct]) => {
        kv("Fraction " + cat, pct.toFixed(1) + "%");
      });
    }

    // ── Section 4 : Compatibilité ──────────────────────────────────────────
    if (mainForm && sectionChecked("rpt_compatibility")) {
      chk(40); secTitle("4. Compatibilite et alertes");
      try {
        const compatRes = await apiPost("/recommend/compatibility", {
          formulation: mainForm.composition
        });
        kv("Statut compatibilite",
           compatRes.compatible ? "Compatible" : "Problemes detectes",
           compatRes.compatible ? C.green : C.red);
        kv("Composants verifies", compatRes.n_checked);
        (compatRes.alerts||[]).forEach(a => para("ALERTE : " + a, 8, C.red));
        (compatRes.warnings||[]).forEach(w => para("Attention : " + w, 8, C.amber));
        if (!compatRes.alerts?.length && !compatRes.warnings?.length)
          para("Aucune incompatibilite detectee.", 8, C.green);
      } catch(e) {
        para("Analyse non disponible.", 8, C.muted);
      }
    }

    // ── Section 5 : Fiches matières ────────────────────────────────────────
    if (mainForm && sectionChecked("rpt_matfiche")) {
      secTitle("5. Fiches matieres premieres");
      const entries = Object.entries(mainForm.composition||{}).sort((a,b)=>b[1]-a[1]);
      entries.slice(0,8).forEach(([id, pct]) => {
        const mat = MATERIALS_CACHE[id] || {};
        chk(28);
        doc.setFillColor(245,247,252);
        doc.rect(ML, Y-2, CW, 26, "F");
        doc.setFontSize(9); doc.setFont("helvetica","bold"); doc.setTextColor(...C.dark);
        doc.text(sanitize(mat.name || id), ML+3, Y+4);
        doc.setFontSize(7.5); doc.setFont("helvetica","normal");
        doc.setTextColor(...C.muted);
        const fields = [
          ["Categorie", mat.category], ["Proportion", pct.toFixed(2)+"%"],
          ["CAS", mat.cas||"—"],       ["Origine", mat.origin||"—"],
          ["Fonctions", (mat.function||[]).slice(0,4).join(", ")],
        ];
        let xf = ML+3, yf = Y+9;
        fields.forEach(([k,v]) => {
          doc.setTextColor(...C.muted); doc.text(k+":", xf, yf);
          doc.setTextColor(...C.dark); doc.text(sanitize(String(v||"—")), xf+22, yf);
          yf += 4.5;
        });
        if (mat.properties?.note) {
          doc.setTextColor(...C.muted);
          doc.text("Note: "+sanitize(mat.properties.note).substring(0,70), ML+3, yf);
        }
        Y += 30;
      });
    }

    // ── Section 6 : Matières premières CI ─────────────────────────────────
    if (sectionChecked("rpt_local")) {
      secTitle("6. Valorisation matieres premieres locales CI");
      const ciMats = Object.entries(mainForm?.composition||{}).filter(([id]) => {
        const mat = MATERIALS_CACHE[id] || {};
        return mat.origin?.includes("CI") || mat.origin?.includes("Cote") ||
               mat._source?.includes("CI");
      });

      if (ciMats.length) {
        kv("Ingredients locaux CI", ciMats.length + "/" + Object.keys(mainForm.composition||{}).length);
        const localPct = ciMats.reduce((s,[,p])=>s+p, 0);
        kv("Part locale totale", localPct.toFixed(1) + "%");
        doc.setFillColor(0,229,200,10);
        chk(20);
        doc.setFillColor(0,40,35); doc.rect(ML, Y, CW, ciMats.length*6+10, "F");
        doc.setFontSize(8.5); doc.setFont("helvetica","bold");
        doc.setTextColor(...C.cyan);
        doc.text("Ingredients 100% locaux Cote d'Ivoire :", ML+4, Y+6);
        Y += 9;
        ciMats.forEach(([id,pct]) => {
          const mat = MATERIALS_CACHE[id]||{};
          doc.setFont("helvetica","normal"); doc.setTextColor(...C.white);
          doc.text(`- ${sanitize(mat.name||id)} (${pct.toFixed(1)}%) — ${sanitize(mat.origin||"")}`, ML+6, Y);
          Y += 5.5;
        });
        Y += 4;
        para("Valorisation des filieres locales : palmier, karite, cacao, coco, moringa...", 8, C.muted);
        para("Reduction des importations — impact economique positif pour la CI.", 8, C.muted);
      } else {
        para("Aucune matiere premiere locale CI identifiee dans cette formulation.", 8, C.muted);
        para("Considerez d'ajouter : Huile_Palme_RBD, Beurre_Cacao, Beurre_Karite,", 8, C.amber);
        para("Aloe_Vera_Gel_CI, Gomme_Arabique_CI, Argile_Kaolin_CI...", 8, C.amber);
      }
    }

    // ── Toutes les formulations générées (résumé) ──────────────────────────
    if (state.generatedFormulas.length > 1) {
      secTitle(`7. Comparatif des ${Math.min(state.generatedFormulas.length,5)} formulations`);
      const allIds = [...new Set(state.generatedFormulas.flatMap(f => Object.keys(f.composition||{})))];
      const tableHead = ["Ingredient", ...state.generatedFormulas.slice(0,5).map((_,i)=>`F#${i+1}`)];
      const tableBody = allIds.slice(0,12).map(id => {
        const mat = MATERIALS_CACHE[id]||{};
        return [
          sanitize((mat.name||id).substring(0,22)),
          ...state.generatedFormulas.slice(0,5).map(f => {
            const v = f.composition?.[id];
            return v != null ? v.toFixed(1)+"%" : "—";
          }),
        ];
      });
      tableBody.push([
        "Cout (" + rptCur + "/kg)",
        ...state.generatedFormulas.slice(0,5).map(f =>
          formatPrice((f.cost_index||0) * 150, rptCur))
      ]);
      doc.autoTable({
        startY:    Y,
        head:      [tableHead],
        body:      tableBody,
        theme:     "grid",
        headStyles:{fillColor:C.dark, textColor:C.cyan, fontSize:7},
        bodyStyles:{fontSize:7, textColor:C.dark},
        alternateRowStyles:{fillColor:[245,247,252]},
        margin:    {left:ML, right:MR},
      });
      Y = doc.lastAutoTable.finalY + 6;
    }

    // Pied de page dernière page
    footerPage();

    // ── Sauvegarde ────────────────────────────────────────────────────────
    const slug = (company + "_" + project).replace(/[^a-zA-Z0-9]/g,"_").substring(0,30);
    const filename = `FormulationAI_${slug}_${new Date().toISOString().slice(0,10)}.pdf`;
    doc.save(filename);

    const pg = doc.internal.getNumberOfPages();
    const el  = document.getElementById("rptStatus");
    el.style.display = "block";
    el.innerHTML = `
      <h4>Rapport PDF genere</h4>
      <div class="metric-row"><span class="metric-label">Fichier</span>
        <span class="metric-value good">${filename}</span></div>
      <div class="metric-row"><span class="metric-label">Pages</span>
        <span class="metric-value">${pg}</span></div>
      <div class="metric-row"><span class="metric-label">Devise</span>
        <span class="metric-value">${rptCur}</span></div>`;
    showToast("Rapport PDF genere !", "success");

  } catch(e) {
    console.error(e);
    showToast("Erreur PDF : " + e.message, "error");
  } finally { hideLoader(); }
}

// ── sanitize (PDF safe) ───────────────────────────────────────────────────────
function sanitize(str) {
  if (!str) return "";
  return String(str)
    .replace(/&amp;/g,"&").replace(/&lt;/g,"<").replace(/&gt;/g,">")
    .replace(/[éèêë]/g,"e").replace(/[àâä]/g,"a").replace(/[îï]/g,"i")
    .replace(/[ôö]/g,"o").replace(/[ùûü]/g,"u").replace(/[ç]/g,"c")
    .replace(/[ÉÈÊË]/g,"E").replace(/[ÀÂÄÃ]/g,"A").replace(/[ÔÖ]/g,"O")
    .replace(/[°]/g,"deg").replace(/[±]/g,"+/-").replace(/[²³]/g,n=>n==="²"?"2":"3")
    .replace(/[–—]/g,"-").replace(/[•·▸→]/g,"-")
    .replace(/[^\x00-\xFF]/g,"?");
}

// ── loadScript helper ─────────────────────────────────────────────────────────
function loadScript(src) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) { resolve(); return; }
    const s = document.createElement("script");
    s.src = src; s.onload = resolve; s.onerror = reject;
    document.head.appendChild(s);
  });
}

// Stocker le dernier résultat de génération pour la devise
const _origGenerate = generateFormulations;
window.generateFormulations = async function() {
  await _origGenerate.call(this);
  state.lastGenerateResult = null; // sera mis à jour dans renderFormulations
};

// Stocker dernier résultat optimisation
state.lastOptResult = null;
const _origOptResult = renderOptResult;
window.renderOptResult = function(res, obj) {
  _origOptResult.call(this, res, obj);
  if (obj !== "pareto") state.lastOptResult = res;
};
