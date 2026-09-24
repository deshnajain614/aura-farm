// AURA-Farm OS Web Dashboard Client Application

const LIFECYCLE_STEPS = [
  { id: "PRODUCTION_PLANNING", label: "Plan" },
  { id: "SEED_INVENTORY_CHECK", label: "Seed Inventory" },
  { id: "AUTOMATED_SEEDING", label: "Seeding Robot" },
  { id: "GERMINATING", label: "Germination" },
  { id: "ROBOTIC_TRANSPLANTING", label: "Transplant" },
  { id: "VEGETATIVE_GROWTH", label: "Grow" },
  { id: "ROBOTIC_INSPECTION", label: "Inspect" },
  { id: "ROBOTIC_PRUNING", label: "Prune" },
  { id: "ROBOTIC_POLLINATION", label: "Pollinate" },
  { id: "DISEASE_RESPONSE", label: "Disease Response" },
  { id: "HARVEST_PREDICTION", label: "Predict Yield" },
  { id: "AUTONOMOUS_HARVESTING", label: "Harvest" },
  { id: "SORTING_AND_GRADING", label: "Sort & Grade" },
  { id: "AUTOMATED_PACKAGING", label: "Package" },
  { id: "COLD_STORAGE", label: "Cold Store" },
  { id: "WASTE_MANAGEMENT", label: "Biomass Recycle" },
  { id: "SYSTEM_CLEANING", label: "Clean CIP" },
  { id: "SANITIZATION_CIP", label: "Sanitize & UV" },
  { id: "SYSTEM_RESET", label: "Reset" },
  { id: "NEXT_CYCLE_PREPARED", label: "Next Cycle" }
];

let ws = null;
let currentSnapshot = null;
let eStopEngaged = false;
let canvasAnimationId = null;

// Initialize WebSocket
function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/telemetry`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("Connected to AURA-Farm OS Telemetry Stream.");
    document.getElementById("edge-sync-text").textContent = "ONLINE (STREAMING)";
    document.getElementById("edge-sync-text").className = "text-emerald-400 font-mono font-medium";
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      currentSnapshot = data;
      renderDashboard(data);
    } catch (e) {
      console.error("Error parsing telemetry message:", e);
    }
  };

  ws.onclose = () => {
    console.warn("WebSocket disconnected. Reconnecting in 2s...");
    document.getElementById("edge-sync-text").textContent = "DISCONNECTED";
    document.getElementById("edge-sync-text").className = "text-amber-400 font-mono font-medium";
    setTimeout(connectWebSocket, 2000);
  };
}

// Render Dashboard UI Elements
function renderDashboard(data) {
  if (!data) return;

  // 1. Header & Lifecycle state
  const lifecycle = data.lifecycle || {};
  document.getElementById("current-state-badge").textContent = lifecycle.state || "ACTIVE";
  document.getElementById("batch-id-text").textContent = lifecycle.batch_id || "AURA-BATCH-01";
  document.getElementById("cycle-badge").textContent = `#${lifecycle.cycle || 1}`;
  document.getElementById("cycle-day").textContent = lifecycle.cycle_day || 0;

  // 2. Render Lifecycle Stepper
  renderStepper(lifecycle.state);

  // 3. Water & Utility Telemetry
  const water = data.water || {};
  document.getElementById("val-ph").textContent = Number(water.ph || 6.0).toFixed(2);
  document.getElementById("val-ec").innerHTML = `${Number(water.ec_ms_cm || 1.6).toFixed(2)} <span class="text-xs font-normal text-slate-400">mS/cm</span>`;
  document.getElementById("val-do").innerHTML = `${Number(water.dissolved_oxygen_mg_l || 8.0).toFixed(1)} <span class="text-xs font-normal text-slate-400">mg/L</span>`;
  document.getElementById("water-reservoir-level").textContent = `${Number(water.reservoir_level_pct || 88).toFixed(1)}%`;
  document.getElementById("water-turbidity").textContent = `${Number(water.turbidity_ntu || 1.1).toFixed(2)} NTU`;
  document.getElementById("leak-status").textContent = water.leak_detected ? "DETECTED (AUTO-ISOLATED)" : "NONE";
  document.getElementById("leak-status").className = water.leak_detected ? "text-rose-400 font-bold" : "text-emerald-400";

  // 4. Climate Telemetry
  const climate = data.climate || {};
  document.getElementById("val-vpd").innerHTML = `${Number(climate.vpd_kpa || 0.85).toFixed(2)} <span class="text-xs font-normal text-slate-400">kPa</span>`;
  document.getElementById("val-temp").textContent = Number(climate.air_temp_c || 22.0).toFixed(1);
  document.getElementById("val-humidity").textContent = Number(climate.relative_humidity_pct || 65).toFixed(0);
  document.getElementById("val-co2").innerHTML = `${Number(climate.co2_ppm || 1000).toFixed(0)} <span class="text-xs font-normal text-slate-400">ppm</span>`;

  // 5. Energy Telemetry
  const energy = data.energy || {};
  document.getElementById("val-battery").textContent = `${Number(energy.battery_soc_pct || 85).toFixed(1)}%`;
  document.getElementById("val-solar").textContent = `${(Number(energy.solar_generation_w || 0) / 1000).toFixed(1)} kW`;

  // 6. Nutrient Storage Levels
  const nutrients = data.nutrients || {};
  const tA = Number(nutrients.tank_a_pct || 75).toFixed(0);
  const tB = Number(nutrients.tank_b_pct || 80).toFixed(0);
  const tPh = Number(nutrients.ph_down_pct || 65).toFixed(0);
  document.getElementById("tank-a-pct").textContent = `${tA}%`;
  document.getElementById("bar-tank-a").style.width = `${tA}%`;
  document.getElementById("tank-b-pct").textContent = `${tB}%`;
  document.getElementById("bar-tank-b").style.width = `${tB}%`;
  document.getElementById("tank-phdown-pct").textContent = `${tPh}%`;
  document.getElementById("bar-tank-phdown").style.width = `${tPh}%`;

  // 7. Zone Statuses
  const zones = lifecycle.zones || {};
  if (zones.NURSERY) document.getElementById("zone-nursery").textContent = zones.NURSERY;
  if (zones.VEGETATIVE_ZONE) document.getElementById("zone-vegetative").textContent = zones.VEGETATIVE_ZONE;
  if (zones.GROWTH_ZONE) document.getElementById("zone-growth").textContent = zones.GROWTH_ZONE;
  if (zones.MATURITY_ZONE) document.getElementById("zone-maturity").textContent = zones.MATURITY_ZONE;
  if (zones.HARVEST_ZONE) document.getElementById("zone-harvest").textContent = zones.HARVEST_ZONE;
  if (zones.QUARANTINE_ZONE) document.getElementById("zone-quarantine").textContent = zones.QUARANTINE_ZONE;

  // 8. Render Plant Grid Digital Twin
  renderPlantGrid(data.plants || []);

  // 9. Safety Decisions Table
  renderSafetyTable(data.safety?.recent_decisions || []);

  // 10. Totals
  document.getElementById("packages-count-text").textContent = data.total_packages_sealed || 0;
}

// Render Lifecycle Stepper
function renderStepper(currentState) {
  const container = document.getElementById("lifecycle-stepper");
  container.innerHTML = "";

  LIFECYCLE_STEPS.forEach((step, idx) => {
    const isCurrent = (step.id === currentState);
    const div = document.createElement("div");
    div.className = `flex items-center gap-1.5 px-3 py-1.5 rounded-lg border transition-all ${
      isCurrent 
        ? "bg-emerald-500/20 border-emerald-400 text-emerald-300 font-bold shadow-lg shadow-emerald-500/30 scale-105" 
        : "bg-slate-900/60 border-slate-800 text-slate-400 font-medium"
    }`;
    div.innerHTML = `
      <span class="w-4 h-4 rounded-full flex items-center justify-center text-[10px] ${
        isCurrent ? "bg-emerald-400 text-slate-950 font-black" : "bg-slate-800 text-slate-400"
      }">${idx + 1}</span>
      <span>${step.label}</span>
    `;
    container.appendChild(div);

    if (idx < LIFECYCLE_STEPS.length - 1) {
      const arrow = document.createElement("span");
      arrow.className = "text-slate-700 font-bold";
      arrow.textContent = "→";
      container.appendChild(arrow);
    }
  });
}

// Render Plant Digital Twin Cards
function renderPlantGrid(plants) {
  const grid = document.getElementById("plant-grid");
  if (!plants || plants.length === 0) {
    grid.innerHTML = `
      <div class="col-span-full py-8 text-center text-xs text-slate-500 font-mono">
        Growing channels currently undergoing automated Clean-In-Place (CIP) cycle or seeding.
      </div>
    `;
    return;
  }

  grid.innerHTML = "";
  plants.slice(0, 8).forEach(p => {
    const isDiseased = p.has_disease;
    const card = document.createElement("div");
    card.className = `p-3 rounded-xl border transition-all ${
      isDiseased 
        ? "bg-rose-950/30 border-rose-500/60 shadow-lg shadow-rose-900/30" 
        : "bg-slate-900/60 border-slate-800/80 hover:border-emerald-500/40"
    }`;

    card.innerHTML = `
      <div class="flex justify-between items-start text-[11px] mb-1">
        <span class="font-mono font-semibold text-slate-300">Slot C${p.channel_index}-S${p.slot_index}</span>
        <span class="px-1.5 py-0.2 rounded text-[10px] font-bold ${
          isDiseased ? "bg-rose-500 text-white" : "bg-emerald-500/20 text-emerald-400"
        }">${isDiseased ? "ISOLATE" : p.health}</span>
      </div>
      <div class="text-xs font-bold text-slate-200">${p.crop_name}</div>
      <div class="mt-2 text-[10px] text-slate-400 space-y-0.5 font-mono">
        <div class="flex justify-between"><span>Biomass:</span> <span class="text-slate-200">${p.biomass_estimated_g}g</span></div>
        <div class="flex justify-between"><span>Height:</span> <span class="text-slate-200">${p.height_cm}cm</span></div>
        <div class="flex justify-between"><span>Pruned:</span> <span class="text-slate-200">${p.pruned_count}x</span></div>
      </div>
    `;
    grid.appendChild(card);
  });
}

// Render Safety Engine Gatekeeper Decisions
function renderSafetyTable(decisions) {
  const tbody = document.getElementById("safety-log-body");
  if (!decisions || decisions.length === 0) return;

  tbody.innerHTML = "";
  decisions.forEach(d => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-900/40 transition";

    let gateBadge = "";
    if (d.gate === "ALLOWED") {
      gateBadge = `<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">ALLOWED</span>`;
    } else if (d.gate === "RESTRICTED") {
      gateBadge = `<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">RESTRICTED</span>`;
    } else {
      gateBadge = `<span class="px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30 font-bold">UNSAFE (REJECT)</span>`;
    }

    const timeStr = new Date(d.timestamp * 1000).toLocaleTimeString();
    tr.innerHTML = `
      <td class="py-2 px-3 text-slate-400">${timeStr}</td>
      <td class="py-2 px-3 text-cyan-300 font-semibold">${d.recommendation_source}</td>
      <td class="py-2 px-3 text-slate-200 font-bold">${d.proposed_action}</td>
      <td class="py-2 px-3">${gateBadge}</td>
      <td class="py-2 px-3 text-slate-400">${d.reason}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Simulated Vision Canvas Rendering (High-Tech Laser & Bounding Boxes)
function initVisionCanvas() {
  const canvas = document.getElementById("vision-canvas");
  const ctx = canvas.getContext("2d");
  canvas.width = 640;
  canvas.height = 360;

  let scanLineY = 0;

  function draw() {
    ctx.fillStyle = "#040d1a";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    ctx.strokeStyle = "rgba(16, 185, 129, 0.08)";
    ctx.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += 30) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 30) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Draw synthetic plant canopies
    const plants = [
      { x: 120, y: 160, r: 48, label: "PLANT-01 [NDVI 0.94]", color: "#10b981" },
      { x: 260, y: 170, r: 52, label: "PLANT-02 [NDVI 0.91]", color: "#10b981" },
      { x: 400, y: 155, r: 50, label: "PLANT-03 [NDVI 0.89]", color: "#10b981" },
      { x: 530, y: 165, r: 46, label: "PLANT-04 [NDVI 0.93]", color: "#10b981" }
    ];

    plants.forEach(p => {
      // Glow circle
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(16, 185, 129, 0.25)";
      ctx.fill();
      ctx.strokeStyle = p.color;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Bounding box
      const boxSize = p.r * 2 + 12;
      ctx.strokeStyle = "rgba(45, 212, 191, 0.6)";
      ctx.strokeRect(p.x - boxSize / 2, p.y - boxSize / 2, boxSize, boxSize);

      // Label
      ctx.fillStyle = "#2dd4bf";
      ctx.font = "10px JetBrains Mono";
      ctx.fillText(p.label, p.x - boxSize / 2, p.y - boxSize / 2 - 4);
    });

    // Moving laser scanning line
    scanLineY = (scanLineY + 2.5) % canvas.height;
    ctx.strokeStyle = "rgba(56, 189, 248, 0.85)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, scanLineY);
    ctx.lineTo(canvas.width, scanLineY);
    ctx.stroke();

    requestAnimationFrame(draw);
  }

  draw();
}

// Event Listeners for Controls & Scenarios
document.addEventListener("DOMContentLoaded", () => {
  connectWebSocket();
  initVisionCanvas();

  // Manual Tick Button
  document.getElementById("btn-manual-tick").addEventListener("click", async () => {
    try {
      const res = await fetch("/api/orchestrator/tick", { method: "POST" });
      const json = await res.json();
      console.log("Advanced tick manually:", json);
    } catch (e) {
      console.error("Tick error:", e);
    }
  });

  // Crop Selector Change
  document.getElementById("crop-select").addEventListener("change", async (e) => {
    try {
      await fetch("/api/crops/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ crop_name: e.target.value })
      });
    } catch (err) {
      console.error("Failed to change crop:", err);
    }
  });

  // Emergency Stop Toggle
  document.getElementById("btn-estop").addEventListener("click", async () => {
    eStopEngaged = !eStopEngaged;
    const btn = document.getElementById("btn-estop");
    if (eStopEngaged) {
      btn.className = "px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition flex items-center gap-1.5 shadow-lg";
      btn.innerHTML = `<i data-lucide="play" class="w-4 h-4"></i><span>RESUME</span>`;
    } else {
      btn.className = "px-3.5 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold transition flex items-center gap-1.5 shadow-lg shadow-rose-600/30";
      btn.innerHTML = `<i data-lucide="octagon-alert" class="w-4 h-4"></i><span>E-STOP</span>`;
    }
    lucide.createIcons();
    await fetch("/api/safety/emergency-stop", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ engaged: eStopEngaged, reason: "Operator Button" })
    });
  });

  // Scenario Buttons
  document.getElementById("btn-scenario-disease").addEventListener("click", async () => {
    await fetch("/api/scenarios/inject-disease", { method: "POST" });
  });

  document.getElementById("btn-scenario-power").addEventListener("click", async () => {
    await fetch("/api/scenarios/power-cut", { method: "POST" });
  });

  document.getElementById("btn-scenario-wan").addEventListener("click", async () => {
    await fetch("/api/scenarios/wan-drop", { method: "POST" });
  });
});
