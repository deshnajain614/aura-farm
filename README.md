# 🌱 AURA-Farm OS (AI-HARVEST)
### Autonomous Unified Robotic Agriculture Farm Operating System

[![CI/CD Pipeline](https://github.com/aura-farm/aura-farm/actions/workflows/ci.yml/badge.svg)](https://github.com/aura-farm/aura-farm/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-teal.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-cyan.svg)](https://fastapi.tiangolo.com)
[![Zero Human Intervention](https://img.shields.io/badge/Human_Intervention-ZERO-green.svg)](#core-principle)

---

## 📖 Core Principle

> **"The farm should be able to start with seeds and resources, grow the crop, maintain itself, harvest the crop, clean the growing system, prepare the next cycle, and continue operating without a person routinely entering the farm."**

**AURA-Farm** (Autonomous Unified Robotic Agriculture Farm), also designated **AI-HARVEST OS**, is a production-grade, closed-loop software and robotic automation operating system for vertical CEA (Controlled Environment Agriculture) hydroponic facilities.

It combines an **AI Decision Brain**, an **Industrial Deterministic Safety Interlock Engine**, **IoT & Utility Subsystems (Water, Nutrients, HVAC, Spectrum Lighting, Microgrid)**, and **Autonomous Robotic Actuation (Seeding, Mobile Inspection, Pruning, Pollination, Harvesting, Conveyor Sorting, Packaging, and Clean-In-Place Sanitization)** into a unified continuous loop.

---

## 🏗️ Complete Closed-Loop Architecture (27 Subsystems)

```text
                                  AUTONOMOUS FARM OS
                                          │
                                          ▼
                                PRODUCTION PLANNER (#1)
                                          │
                                          ▼
                               SEED MANAGEMENT (#1, #2)
                                          │
                                          ▼
                               AUTOMATED SEEDING (#2)
                                          │
                                          ▼
                                  GERMINATION (#3)
                                          │
                                          ▼
                             ROBOT TRANSPLANTING (#4, #5)
                                          │
                                          ▼
                                 GROWING CYCLE (#5)
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        ▼                                 ▼                                 ▼
   WATER (#6)                      NUTRIENTS (#7)                   ENVIRONMENT (#8, #9)
 (Intake, Filter, RO,             (A, B, pH Down/Up,               (HVAC, Fans, CO2, VPD,
  DO, Turbidity, Recycle)        Auto-Refill, Safe Mode)            Spectrum LED, DLI)
        │                                 │                                 │
        └─────────────────────────────────┼─────────────────────────────────┘
                                          ▼
                                AI PLANT VISION (#10)
                                          │
              ┌───────────────────────────┼───────────────────────────┐
              ▼                           ▼                           ▼
         HEALTH (#10)               DISEASE (#13, #14)           GROWTH (#10)
        (NDVI, Vigor)              (Pathogen Isolation,          (Biomass, Dia)
                                     UV-C Spot Treatment)
              │                           │                           │
              └───────────────────────────┼───────────────────────────┘
                                          ▼
                              AI DECISION ENGINE (#26)
                                          │
                                          ▼
                                SAFETY ENGINE (#26)
                   (ALLOWED -> Execute | RESTRICTED -> Clamp | UNSAFE -> Reject)
                                          │
                                          ▼
                              ROBOTIC ACTIONS (#10-#15)
                                          │
                 ┌────────────────────────┼────────────────────────┐
                 ▼                        ▼                        ▼
           Pruning (#11)          Pollination (#12)        Inspection (#10)
                 │                        │                        │
                 └────────────────────────┼────────────────────────┘
                                          ▼
                              HARVEST PREDICTION (#15)
                                          │
                                          ▼
                               HARVESTING ROBOT (#15)
                                          │
                                          ▼
                             SORTING & GRADING (#16)
                          (Grade A / Grade B / Reject)
                                          │
                                          ▼
                             AUTOMATED PACKING (#17)
                          (Weigh, Clamshell, QR Trace)
                                          │
                                          ▼
                              AUTONOMOUS STORAGE (#18)
                           (4°C Cold Room, FEFO Matrix)
                                          │
                                          ▼
                               WASTE MANAGEMENT (#19)
                           (Biomass Shredder, Compost)
                                          │
                                          ▼
                             CROP-CYCLE CLEANING (#20)
                          (Drain, Pressure Wash, Flush)
                                          │
                                          ▼
                              SANITIZATION ROBOT (#20)
                           (Dissolved Ozone, UV-C CIP)
                                          │
                                          ▼
                                 SYSTEM RESET (#20)
                                          │
                                          ▼
                                NEXT CROP CYCLE (#27)
                                          │
                                          └───────────────────────────→ LOOP
```

---

## 🛡️ Autonomous Decision Hierarchy (Section 26)

To guarantee safety and prevent catastrophic crop failures or physical actuator collisions, **no AI model directly actuates machinery**. All recommendations pass through a deterministic physical interlock layer:

```text
                  AI BRAIN
                     │  (e.g., "Dose 250ml Nutrient Stock A")
                     ▼
              Recommendation
                     │
                     ▼
              DECISION ENGINE
                     │  (Structures command & validates recipe bounds)
                     ▼
              SAFETY ENGINE
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
     ALLOWED     RESTRICTED     UNSAFE
     (Execute)  (Clamp Rate)   (Hard Reject)
```

### Safety Interlock Rules Enforced:
1. **Emergency Stop (E-Stop)**: When engaged, all physical motion and dosing is instantly locked.
2. **Dosing Clamping**: Single dose strictly capped at $\le 120\text{ ml}$; hourly rate capped at $\le 500\text{ ml/h}$.
3. **Biological Envelope**: Climate targets restricted to $14^\circ\text{C} \le T \le 34^\circ\text{C}$, $\text{CO}_2 \le 1800\text{ ppm}$.
4. **CIP Chemical Lockout**: Clean-In-Place chemical/ozone flushes are rejected if active crops are detected in the zone.

---

## ⚡ Key Subsystems Summary

| Subsystem | Prompt Section | Primary Responsibility |
|---|---|---|
| **Production Planner** | §1, §2 | Crop recipe matrix (Lettuce, Basil, Strawberries, Tomatoes), seed buffer calculations, schedule. |
| **Seeding Robot** | §2 | Optical seed inventory, gantry pick-and-place dispenser, CV tray validation (missing/doubles). |
| **Germination Chamber** | §3 | Microclimate dark/light regime, ultrasonic misting, AI radicle & cotyledon readiness scoring. |
| **Transplanting Robot** | §4, §5 | Healthy seedling selection, skips stunted plugs, records batch lineage, dynamic zone positioning. |
| **Water Utility** | §6 | Closed-loop intake, RO filtration, UV sterilization, recovery loop (95% recycled), leak detection. |
| **Nutrient System** | §7 | Multi-tank automated dosing (A, B, pH Down/Up), ultrasonic inventory, auto-switchover to backup cartridges. |
| **Climate Control** | §8 | HVAC, variable fans, exhaust louvers, ultrasonic humidifier, CO₂ injection, real-time VPD calculation. |
| **Lighting System** | §9 | Multi-channel spectral control (Deep Red 660nm, Royal Blue 450nm, White), photoperiod & DLI accumulator. |
| **Mobile Inspector** | §10 | Autonomous rail/aisle rover, multispectral NDVI scanning, canopy diameter, leaf chlorosis detection. |
| **Robotic Pruning** | §11 | 3D target coordinates, articulated micro-shears, cut confirmation, pneumatic waste suction. |
| **Robotic Pollination** | §12 | Blossom anthesis detection, acoustic resonant air-pulse pollination, per-slot event recording. |
| **Disease & Pest Response** | §13, §14 | Pathogen detection cross-checked with environmental telemetry, robotic isolation to Quarantine Zone. |
| **Autonomous Harvester** | §15 | Soft gripper, pneumatic shear cut, digital load cell weight measurement, planned vs actual yield analysis. |
| **Sorting & Grading** | §16 | High-speed optical conveyor classification: Grade A (Premium), Grade B (Commercial), Rejected (Compost). |
| **Packaging Cell** | §17 | Robotic clamshell packaging, tamper-evident sealing, thermal QR traceability code generator. |
| **Autonomous Storage** | §18 | 4°C climate-controlled storage gantry, FEFO (First Expired, First Out) dispatch queue. |
| **Waste Management** | §19 | Biomass shredder, thermophilic composting vessel monitoring, bio-fertilizer digestate production. |
| **CIP Sanitization** | §20 | Post-harvest drainage, rotary pressure wash, dissolved ozone flush, UV-C tunnel sweep, purity check. |
| **Predictive Maintenance** | §21, §22 | Vibration FFT, motor winding temp, current draw, automatic failover to redundant standby pump. |
| **Energy Management** | §23 | Microgrid orchestrator (Solar PV, BESS, Grid) with 3-tier priority load shedding (Water/Sensors > HVAC > LEDs). |
| **Edge Autonomy** | §24 | Offline-native SQLite WAL database, continues operation during WAN drops, automatic cloud re-sync. |
| **Cybersecurity** | §25 | Cryptographic device authentication, HMAC-SHA256 signed actuation, RBAC, tamper-evident audit log. |
| **State Machine** | §27 | Master closed-loop orchestrator that restarts the next cycle autonomously without humans. |

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (or Docker)
- Git (included or installed)

### 2. Installation
```bash
# Clone or navigate to the project directory
cd aura-farm

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch the Application & Dashboard
```bash
# Run AURA-Farm OS
python -m aura_farm.main
```

Open your browser and navigate to:
- **Interactive Web Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive REST API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Real-Time Telemetry WebSocket**: `ws://localhost:8000/ws/telemetry`

---

## 🧪 Testing and Simulation

Run the automated test suite verifying all safety interlocks, state transitions, and subsystems:
```bash
pytest tests/ -v
```

Run the standalone CLI simulation harness:
```bash
# Run 25 autonomous lifecycle ticks with real-time telemetry output:
python scripts/run_simulation.py --ticks 25
```

---

## 🐳 Docker Deployment

Run AURA-Farm OS inside a lightweight Docker container:
```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

---

## 📤 Upload to Your GitHub Repository

We have provided an automated script and standard Git workflow so you can push this project to your GitHub account:

### Method 1: Using the PowerShell Helper Script (Windows)
```powershell
# Run the setup script with your GitHub repository URL:
.\scripts\setup_github_repo.ps1 -RepoUrl "https://github.com/YOUR_USERNAME/aura-farm.git"
```

### Method 2: Standard Git Commands
```bash
# 1. Initialize git
git init -b main

# 2. Add all files
git add .

# 3. Create initial commit
git commit -m "feat: initial commit of AURA-Farm autonomous robotic hydroponic farm OS"

# 4. Link your remote GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/aura-farm.git

# 5. Push to GitHub
git push -u origin main
```

---

## 📊 Interactive Web Dashboard Preview

The built-in modern dashboard includes:
- **Live 27-Step Lifecycle Stepper**: Visualizes real-time progression through Seeding, Germination, Transplant, Vegetative Growth, Inspection, Pruning, Harvesting, CIP Sanitization, and Reset.
- **Rack Channel Digital Twin**: Color-coded plant tiles with health scores, biomass estimates, and pruning markers.
- **Synthetic AI Vision Feed**: Canvas scanner simulating rail inspection rover camera with bounding boxes and NDVI overlays.
- **Section 26 Safety Interlock Table**: Live log of AI recommendations vs Safety Gate decisions (`ALLOWED`, `RESTRICTED`, `UNSAFE`).
- **Interactive Scenario Triggers**:
  - `Pathogen Outbreak Simulation` (triggers autonomous robotic isolation to Quarantine zone)
  - `Grid Blackout Simulation` (triggers microgrid load shedding to protect water circulation)
  - `Cloud WAN Drop Simulation` (triggers offline edge local SQLite storage)
  - `EMERGENCY STOP` hard interlock

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
