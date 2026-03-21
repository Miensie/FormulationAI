/**
 * FormulationAI — config.js
 * ==========================
 * ✏️  MODIFIER RENDER_API_URL avec l'URL EXACTE de votre backend Render.
 *
 * Pour trouver l'URL : Render Dashboard → votre service backend → Settings → URL
 * Exemple : https://formulationai-api-xxxx.onrender.com
 *
 * ⚠️  Erreur fréquente : vérifier qu'il n'y a pas de double "m" (.comm)
 *     et que l'URL commence bien par https://
 */

(function () {
  // ── ✏️ Mettre ici l'URL EXACTE de votre backend Render ──────────────────
  const RENDER_API_URL = "https://formulationai-api.onrender.com";
  //                      ↑ Vérifier cette URL dans votre tableau de bord Render
  // ─────────────────────────────────────────────────────────────────────────

  const hostname = window.location.hostname;
  const isLocal  = hostname === "localhost" || hostname === "127.0.0.1";

  window.FORMULATIONAI_CONFIG = {
    API_BASE_URL: isLocal ? "http://localhost:8000" : RENDER_API_URL,
    VERSION:      "1.0.0",
    ENV:          isLocal ? "development" : "production",
  };

  console.log(
    "%c[FormulationAI v" + window.FORMULATIONAI_CONFIG.VERSION + "]",
    "color:#00E5C8;font-weight:bold",
    window.FORMULATIONAI_CONFIG.ENV + " | API → " + window.FORMULATIONAI_CONFIG.API_BASE_URL
  );
})();
