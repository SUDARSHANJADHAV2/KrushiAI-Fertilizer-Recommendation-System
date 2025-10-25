// Set this to your deployed Render URL, e.g. "https://fertilizer-api.onrender.com"
const API_BASE_URL = window.API_BASE_URL || "http://localhost:5000";

const soilSelect = document.getElementById("soil_type");
const cropSelect = document.getElementById("crop_type");
const resultEl = document.getElementById("result");
const errorsEl = document.getElementById("errors");

async function fetchClasses() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/classes`);
    const data = await res.json();
    soilSelect.innerHTML = data.soil_types.map(v => `<option>${v}</option>`).join("");
    cropSelect.innerHTML = data.crop_types.map(v => `<option>${v}</option>`).join("");
  } catch (e) {
    errorsEl.classList.remove("hidden");
    errorsEl.textContent = "Failed to load classes from backend.";
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
