// Auto-select API: localhost in dev, relative paths in production (proxied via netlify.toml)
// Check if running from file:// protocol or localhost (including Live Server ports like 5500-5599)
const isLocal = location.protocol === "file:" || 
                location.hostname === "localhost" || 
                location.hostname === "127.0.0.1" || 
                location.hostname === "" ||
                (location.hostname === "127.0.0.1" && location.port >= "5500" && location.port <= "5599");
// In production (Netlify), use relative paths (proxied via netlify.toml)
// In local dev, point to local backend
const API_BASE_URL = window.API_BASE_URL || (isLocal ? "http://127.0.0.1:5001" : "");

console.log('[Fertilizer] Page URL:', location.href);
console.log('[Fertilizer] Detected as local:', isLocal);
console.log('[Fertilizer] API Base URL:', API_BASE_URL);

const soilSelect = document.getElementById("soil_type");
const cropSelect = document.getElementById("crop_type");
const resultEl = document.getElementById("result");
const errorsEl = document.getElementById("errors");

async function fetchClasses() {
  try {
    console.log('[Fertilizer] Fetching classes from:', `${API_BASE_URL}/api/classes`);
    const res = await fetch(`${API_BASE_URL}/api/classes`);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    const data = await res.json();
    console.log('[Fertilizer] Received classes:', data);
    soilSelect.innerHTML = data.soil_types.map(v => `<option>${v}</option>`).join("");
    cropSelect.innerHTML = data.crop_types.map(v => `<option>${v}</option>`).join("");
    console.log('[Fertilizer] Dropdowns populated successfully');
  } catch (e) {
    console.error('[Fertilizer] Failed to load classes:', e);
    errorsEl.classList.remove("hidden");
    errorsEl.textContent = `Failed to load classes: ${e.message}. Make sure backend is running on port 5001.`;
  }
}

function payloadFromForm() {
  return {
    temperature: Number(document.getElementById("temperature").value),
    humidity: Number(document.getElementById("humidity").value),
    moisture: Number(document.getElementById("moisture").value),
    soil_type: soilSelect.value,
    crop_type: cropSelect.value,
    nitrogen: Number(document.getElementById("nitrogen").value),
    potassium: Number(document.getElementById("potassium").value),
    phosphorous: Number(document.getElementById("phosphorous").value)
  };
}

async function submit(e) {
  e.preventDefault();
  errorsEl.classList.add("hidden");
  resultEl.classList.add("hidden");

  try {
    const res = await fetch(`${API_BASE_URL}/api/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payloadFromForm())
    });
    const data = await res.json();
    if (!res.ok) {
      const msg = data?.errors?.join("; ") || data?.error || "Request failed";
      errorsEl.classList.remove("hidden");
      errorsEl.textContent = msg;
      return;
    }

    const conf = data.confidence != null ? ` (${(data.confidence * 100).toFixed(1)}%)` : "";
    const d = data.details || {};
    resultEl.innerHTML = `
      <h3>Recommended: ${data.fertilizer}${conf}</h3>
      <p>${d.description || ""}</p>
      ${Array.isArray(d.benefits) ? `<p><strong>Benefits:</strong> ${d.benefits.join(", ")}</p>` : ""}
      ${Array.isArray(d.best_for) ? `<p><strong>Best for:</strong> ${d.best_for.join(", ")}</p>` : ""}
      ${d.application_rate ? `<p><strong>Rate:</strong> ${d.application_rate}</p>` : ""}
      ${d.timing ? `<p><strong>Timing:</strong> ${d.timing}</p>` : ""}
    `;
    resultEl.classList.remove("hidden");
  } catch (e) {
    errorsEl.classList.remove("hidden");
    errorsEl.textContent = "Prediction failed. Check API URL or network.";
  }
}

window.addEventListener("DOMContentLoaded", () => {
  fetchClasses();
  document.getElementById("predict-form").addEventListener("submit", submit);
});
