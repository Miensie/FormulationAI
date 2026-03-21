/**
 * FormulationAI — config.js
 * ✏️ Modifier RENDER_API_URL apres deploiement Render
 */
(function () {
  const RENDER_API_URL = "https://formulationai-api.onrender.com";
  const isLocal = ["localhost","127.0.0.1"].includes(location.hostname);
  window.FORMULATIONAI_CONFIG = {
    API_BASE_URL: isLocal ? "http://localhost:8000" : RENDER_API_URL,
    VERSION:      "1.0.0",
    ENV:          isLocal ? "development" : "production",
  };
  console.log(`%c[FormulationAI v${window.FORMULATIONAI_CONFIG.VERSION}]`,
    "color:#00E5C8;font-weight:bold",
    `${window.FORMULATIONAI_CONFIG.ENV} | API → ${window.FORMULATIONAI_CONFIG.API_BASE_URL}`);
})();
