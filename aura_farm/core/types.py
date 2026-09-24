"""
AURA-Farm Core Domain Types and Pydantic Schemas
"""
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import time

class LifecycleState(str, Enum):
    IDLE = "IDLE"
    PLANNING = "PRODUCTION_PLANNING"
    SEED_INVENTORY_CHECK = "SEED_INVENTORY_CHECK"
    AUTOMATED_SEEDING = "AUTOMATED_SEEDING"
    GERMINATING = "GERMINATING"
    TRANSPLANTING = "ROBOTIC_TRANSPLANTING"
    VEGETATIVE_GROWTH = "VEGETATIVE_GROWTH"
    ROBOTIC_INSPECTION = "ROBOTIC_INSPECTION"
    ROBOTIC_PRUNING = "ROBOTIC_PRUNING"
    ROBOTIC_POLLINATION = "ROBOTIC_POLLINATION"
    DISEASE_RESPONSE = "DISEASE_RESPONSE"
    HARVEST_PREDICTION = "HARVEST_PREDICTION"
    AUTONOMOUS_HARVESTING = "AUTONOMOUS_HARVESTING"
    SORTING_AND_GRADING = "SORTING_AND_GRADING"
    AUTOMATED_PACKAGING = "AUTOMATED_PACKAGING"
    COLD_STORAGE = "COLD_STORAGE"
    WASTE_MANAGEMENT = "WASTE_MANAGEMENT"
    SYSTEM_CLEANING = "SYSTEM_CLEANING"
    SANITIZATION_CIP = "SANITIZATION_CIP"
    SYSTEM_RESET = "SYSTEM_RESET"
    NEXT_CYCLE_PREPARED = "NEXT_CYCLE_PREPARED"

class SafetyGate(str, Enum):
    ALLOWED = "ALLOWED"          # Within safe bounds -> execute immediately
    RESTRICTED = "RESTRICTED"    # Requires clamped rate or secondary verification
    UNSAFE = "UNSAFE"            # Violates physical limits -> hard reject

class FarmZone(str, Enum):
    NURSERY = "NURSERY"
    VEGETATIVE = "VEGETATIVE_ZONE"
    GROWTH = "GROWTH_ZONE"
    MATURITY = "MATURITY_ZONE"
    HARVEST = "HARVEST_ZONE"
    QUARANTINE = "QUARANTINE_ZONE"

class PlantHealthGrade(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    STRESSED = "STRESSED"
    DISEASED = "DISEASED"
    DEAD = "DEAD"

class ProduceGrade(str, Enum):
    GRADE_A = "GRADE_A_PREMIUM"
    GRADE_B = "GRADE_B_COMMERCIAL"
    REJECTED = "REJECTED_COMPOST"

class RoleType(str, Enum):
    SYSTEM_AUTONOMOUS = "SYSTEM_AUTONOMOUS"
    FARM_ADMIN = "FARM_ADMIN"
    FIELD_TECHNICIAN = "FIELD_TECHNICIAN"
    AUDITOR = "AUDITOR"

# --- Telemetry Models ---

class WaterTelemetry(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    ph: float = 6.0
    ec_ms_cm: float = 1.6
    water_temp_c: float = 20.5
    dissolved_oxygen_mg_l: float = 7.8
    turbidity_ntu: float = 1.2
    flow_rate_l_min: float = 14.8
    reservoir_level_pct: float = 88.0
    leak_detected: bool = False
    uv_sterilizer_active: bool = True
    recovery_recirculation_rate_pct: float = 95.0

class NutrientTankState(BaseModel):
    tank_a_pct: float = 78.0
    tank_b_pct: float = 82.0
    ph_down_pct: float = 65.0
    ph_up_pct: float = 90.0
    backup_cartridges_available: bool = True
    auto_refill_in_progress: bool = False
    safe_operating_mode: bool = False

class ClimateTelemetry(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    air_temp_c: float = 22.4
    relative_humidity_pct: float = 68.0
    vpd_kpa: float = 0.85
    co2_ppm: float = 1050.0
    hvac_status: str = "COOLING_STABLE"
    fans_pct: float = 60.0
    dehumidifier_active: bool = False
    humidifier_active: bool = False

class LightingTelemetry(BaseModel):
    photoperiod_hours: float = 16.0
    current_ppfd_umol_m2_s: float = 240.0
    target_dli_mol_m2_d: float = 14.5
    accumulated_dli: float = 10.2
    spectrum_deep_red_pct: float = 60.0
    spectrum_royal_blue_pct: float = 20.0
    spectrum_white_pct: float = 20.0
    lights_on: bool = True

class RoboticSubsystemStatus(BaseModel):
    seeder_robot_state: str = "IDLE"
    mobile_inspector_position: str = "BAY_3"
    mobile_inspector_battery_pct: float = 94.0
    pruning_robot_state: str = "READY"
    pollination_robot_state: str = "READY"
    harvesting_robot_state: str = "STANDBY"
    conveyor_active: bool = False
    packaging_cell_state: str = "STANDBY"
    sanitization_robot_state: str = "STANDBY"
    emergency_stop_triggered: bool = False

class EnergyTelemetry(BaseModel):
    solar_generation_w: float = 3800.0
    battery_soc_pct: float = 86.5
    grid_power_w: float = 450.0
    total_consumption_w: float = 3100.0
    tier_1_critical_w: float = 650.0     # Pumps, DO, edge controller
    tier_2_essential_w: float = 1450.0   # HVAC, dehumidifier
    tier_3_curtailable_w: float = 1000.0 # Grow LED lights
    is_load_shedding: bool = False

class EquipmentHealth(BaseModel):
    name: str
    vibration_mm_s: float = 1.2
    temp_c: float = 38.0
    current_amps: float = 4.2
    run_hours: float = 1420.0
    health_score_pct: float = 95.0
    redundant_backup_ready: bool = True
    predictive_failure_alert: bool = False

class PlantInstance(BaseModel):
    plant_id: str
    batch_id: str
    crop_name: str
    zone: FarmZone = FarmZone.GROWTH
    channel_index: int = 1
    slot_index: int = 1
    health: PlantHealthGrade = PlantHealthGrade.EXCELLENT
    health_score_pct: float = 98.0
    growth_day: int = 14
    height_cm: float = 12.5
    biomass_estimated_g: float = 140.0
    has_disease: bool = False
    disease_type: Optional[str] = None
    pruned_count: int = 1
    pollinated: bool = False
    is_ready_for_harvest: bool = False

class HarvestBatch(BaseModel):
    batch_id: str
    crop_name: str
    total_yield_kg: float = 0.0
    target_yield_kg: float = 0.0
    grade_a_kg: float = 0.0
    grade_b_kg: float = 0.0
    rejected_waste_kg: float = 0.0
    packages_sealed: int = 0
    traceability_qr: str = ""
    cold_storage_location: str = "ZONE_A_BIN_04"
    harvest_timestamp: float = Field(default_factory=time.time)

class SafetyDecision(BaseModel):
    recommendation_source: str
    proposed_action: str
    parameters: Dict[str, Any]
    gate: SafetyGate
    reason: str
    timestamp: float = Field(default_factory=time.time)
    executed: bool = False

class EdgeSyncState(BaseModel):
    is_online: bool = True
    offline_event_count: int = 0
    last_cloud_sync_timestamp: float = Field(default_factory=time.time)
    heartbeat_interval_s: float = 10.0

class CropRecipe(BaseModel):
    crop_name: str
    germination_days: int = 3
    vegetative_days: int = 18
    maturity_days: int = 28
    harvest_target_weight_g: float = 220.0
    target_ph: float = 6.0
    target_ec_ms_cm: float = 1.6
    target_air_temp_day_c: float = 22.0
    target_air_temp_night_c: float = 18.0
    target_humidity_pct: float = 65.0
    target_co2_ppm: float = 1000.0
    target_dli_mol_m2_d: float = 15.0
    photoperiod_hours: float = 16.0
    requires_pruning: bool = True
    requires_pollination: bool = False
