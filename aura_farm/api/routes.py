"""
AURA-Farm REST API Endpoints
============================
Routes for telemetry, simulation controls, safety interlocks, and test scenarios.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time
from aura_farm.orchestrator import orchestrator
from aura_farm.core.safety_engine import safety_engine
from aura_farm.subsystems.production_planner import production_planner
from aura_farm.subsystems.edge_autonomy import edge_engine
from aura_farm.subsystems.energy_manager import energy_manager
from aura_farm.core.types import PlantHealthGrade

router = APIRouter(prefix="/api", tags=["AURA-Farm Control"])

class EmergencyStopRequest(BaseModel):
    engaged: bool
    reason: Optional[str] = "Operator Interface"

class CropSelectionRequest(BaseModel):
    crop_name: str

class DosingOverrideRequest(BaseModel):
    pump_type: str
    volume_ml: float

@router.get("/health")
def health():
    return {"status": "HEALTHY", "version": "1.0.0", "timestamp": time.time()}

@router.get("/status")
def get_farm_status():
    """Returns the complete digital twin state of all 27 capabilities."""
    return orchestrator.get_telemetry_snapshot()

@router.post("/orchestrator/tick")
def trigger_orchestrator_tick():
    """Advances one step of the closed-loop autonomous cycle."""
    snapshot = orchestrator.tick()
    return {"status": "SUCCESS", "current_state": snapshot["lifecycle"]["state"], "cycle": snapshot["lifecycle"]["cycle"]}

@router.post("/safety/emergency-stop")
def set_emergency_stop(req: EmergencyStopRequest):
    """Engages or releases the physical safety emergency stop interlock."""
    safety_engine.set_emergency_stop(req.engaged, req.reason)
    orchestrator.log_event(
        "SAFETY_INTERLOCK",
        f"Emergency Stop {'ENGAGED' if req.engaged else 'RELEASED'}. Reason: {req.reason}",
        level="CRITICAL" if req.engaged else "INFO"
    )
    return {"emergency_stop_engaged": safety_engine.emergency_stop_engaged}

@router.post("/crops/select")
def select_crop_recipe(req: CropSelectionRequest):
    """Switches the active crop recipe and production planner parameters."""
    if req.crop_name not in production_planner.catalog:
        raise HTTPException(status_code=400, detail=f"Crop '{req.crop_name}' not found in catalog.")
    recipe = production_planner.get_recipe(req.crop_name)
    orchestrator.recipe = recipe
    orchestrator.state_machine.recipe = recipe
    orchestrator.decision_engine.set_recipe(recipe)
    orchestrator.log_event("PLANNER", f"Crop recipe switched to {recipe.crop_name}")
    return {"status": "UPDATED", "crop": recipe.crop_name}

@router.post("/scenarios/inject-disease")
def scenario_inject_disease():
    """Simulates a fungal pathogen anomaly to showcase autonomous quarantine & UV-C treatment."""
    if not orchestrator.active_plants:
        # Seed test plants if empty
        orchestrator.tick()
    if orchestrator.active_plants:
        target = orchestrator.active_plants[0]
        target.has_disease = True
        target.disease_type = "Powdery Mildew (Erysiphe cichoracearum)"
        target.health = PlantHealthGrade.STRESSED
        orchestrator.log_event("SCENARIO", f"Simulated pathogen outbreak on {target.plant_id}.", level="WARNING")
        return {"status": "PATHOGEN_INJECTED", "target_plant_id": target.plant_id}
    return {"status": "NO_ACTIVE_PLANTS"}

@router.post("/scenarios/power-cut")
def scenario_power_cut():
    """Simulates grid failure to trigger microgrid priority load shedding (Section 23)."""
    energy_manager.telemetry.battery_soc_pct = 32.0
    energy_manager.update_energy_state(solar_irradiance_scale=0.1, grid_available=False)
    orchestrator.log_event("SCENARIO", "Simulated Grid Blackout! Microgrid priority shedding active.", level="CRITICAL")
    return {"status": "GRID_OUTAGE_TRIGGERED", "shedding": energy_manager.telemetry.is_load_shedding}

@router.post("/scenarios/wan-drop")
def scenario_wan_drop():
    """Simulates internet disconnection to showcase offline edge autonomy (Section 24)."""
    edge_engine.set_connectivity(not edge_engine.sync_state.is_online)
    status_str = "ONLINE" if edge_engine.sync_state.is_online else "OFFLINE"
    orchestrator.log_event("SCENARIO", f"WAN connectivity toggled to {status_str}.", level="WARNING")
    return {"status": f"WAN_{status_str}", "offline_queue": edge_engine.sync_state.offline_event_count}
