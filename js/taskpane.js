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
  setupSimParams();
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
