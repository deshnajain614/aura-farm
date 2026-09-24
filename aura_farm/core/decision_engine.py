"""
AURA-Farm AI Decision Engine
============================
Integrates telemetry, vision inferences, and biological crop recipes to generate
optimal agronomic actions and route them through the Safety Engine.
"""
from typing import Dict, Any, List, Optional
import math
import logging
from aura_farm.core.types import (
    WaterTelemetry, ClimateTelemetry, LightingTelemetry,
    CropRecipe, SafetyGate, SafetyDecision, FarmZone
)
from aura_farm.core.safety_engine import safety_engine

logger = logging.getLogger("aura_farm.decision")

class DecisionEngine:
    def __init__(self, recipe: Optional[CropRecipe] = None):
        self.recipe = recipe or CropRecipe(crop_name="Butterhead Lettuce")
        self.action_history: List[SafetyDecision] = []

    def set_recipe(self, recipe: CropRecipe):
        self.recipe = recipe
        logger.info(f"Updated active crop recipe to: {recipe.crop_name}")

    def evaluate_water_nutrients(self, water: WaterTelemetry) -> List[SafetyDecision]:
        """Calculates closed-loop corrections for pH and EC."""
        decisions: List[SafetyDecision] = []

        # 1. pH Correction
        delta_ph = water.ph - self.recipe.target_ph
        if delta_ph > 0.25: # pH too high -> dose pH down (acid)
            dose_ml = min(40.0, max(5.0, delta_ph * 25.0))
            dec = safety_engine.evaluate_action(
                source="AI_DECISION_ENGINE_PH_REGULATOR",
                proposed_action="DOSE_PH_DOWN",
                parameters={"volume_ml": round(dose_ml, 1), "reason": f"Current pH {water.ph:.2f} > target {self.recipe.target_ph:.2f}"}
            )
            decisions.append(dec)
        elif delta_ph < -0.25: # pH too low -> dose pH up (alkali)
            dose_ml = min(35.0, max(5.0, abs(delta_ph) * 20.0))
            dec = safety_engine.evaluate_action(
                source="AI_DECISION_ENGINE_PH_REGULATOR",
                proposed_action="DOSE_PH_UP",
                parameters={"volume_ml": round(dose_ml, 1), "reason": f"Current pH {water.ph:.2f} < target {self.recipe.target_ph:.2f}"}
            )
            decisions.append(dec)

        # 2. EC (Electrical Conductivity) Correction
        delta_ec = self.recipe.target_ec_ms_cm - water.ec_ms_cm
        if delta_ec > 0.15: # Nutrients depleted -> dose stock A & B in balanced ratio
            dose_ml = min(50.0, max(10.0, delta_ec * 40.0))
            dec_a = safety_engine.evaluate_action(
                source="AI_DECISION_ENGINE_NUTRIENT_DOSER",
                proposed_action="DOSE_NUTRIENT_A",
                parameters={"volume_ml": round(dose_ml, 1), "reason": f"Current EC {water.ec_ms_cm:.2f} < target {self.recipe.target_ec_ms_cm:.2f}"}
            )
            dec_b = safety_engine.evaluate_action(
                source="AI_DECISION_ENGINE_NUTRIENT_DOSER",
                proposed_action="DOSE_NUTRIENT_B",
                parameters={"volume_ml": round(dose_ml, 1), "reason": f"Current EC {water.ec_ms_cm:.2f} < target {self.recipe.target_ec_ms_cm:.2f}"}
            )
            decisions.extend([dec_a, dec_b])

        # 3. Water reservoir level check
        if water.reservoir_level_pct < 65.0:
            dec_topup = safety_engine.evaluate_action(
                source="AI_DECISION_ENGINE_WATER_UTILITY",
                proposed_action="TOP_UP_RO_WATER",
                parameters={"volume_liters": 25.0, "reason": f"Reservoir level {water.reservoir_level_pct:.1f}% below threshold"}
            )
            decisions.append(dec_topup)

        self.action_history.extend(decisions)
        return decisions

    def evaluate_climate(self, climate: ClimateTelemetry) -> List[SafetyDecision]:
        """Optimizes temperature, humidity, VPD, and CO2 enrichment."""
        decisions: List[SafetyDecision] = []

        # VPD Optimization (Vapor Pressure Deficit)
        # Optimal leafy green VPD is 0.8 - 1.2 kPa
        target_vpd_min = 0.75
        target_vpd_max = 1.15

        if climate.vpd_kpa < target_vpd_min: # Stagnant/too humid -> increase dehumidification & fan circulation
            dec = safety_engine.evaluate_action(
                source="AI_DECISION_ENGINE_VPD_OPTIMIZER",
                proposed_action="SET_CLIMATE_TARGETS",
                parameters={
                    "temp_c": self.recipe.target_air_temp_day_c,
                    "humidity_pct": climate.relative_humidity_pct - 5.0,
                    "fans_pct": 75.0,
                    "reason": f"VPD {climate.vpd_kpa:.2f} kPa is too low; increasing transpiration rate"
                }
            )
            decisions.append(dec)
        elif climate.vpd_kpa > target_vpd_max: # Too dry -> humidify to avoid leaf stomatal closure
            dec = safety_engine.evaluate_action(
                source="AI_DECISION_ENGINE_VPD_OPTIMIZER",
                proposed_action="SET_CLIMATE_TARGETS",
                parameters={
                    "temp_c": self.recipe.target_air_temp_day_c,
                    "humidity_pct": climate.relative_humidity_pct + 8.0,
                    "humidifier_active": True,
                    "reason": f"VPD {climate.vpd_kpa:.2f} kPa is too high; preventing leaf water stress"
                }
            )
            decisions.append(dec)

        # CO2 Enrichment
        if climate.co2_ppm < (self.recipe.target_co2_ppm - 150):
            dec_co2 = safety_engine.evaluate_action(
                source="AI_DECISION_ENGINE_CO2_SYSTEM",
                proposed_action="INJECT_CO2",
                parameters={"target_ppm": self.recipe.target_co2_ppm, "duration_seconds": 45}
            )
            decisions.append(dec_co2)

        self.action_history.extend(decisions)
        return decisions

    def evaluate_lighting(self, light: LightingTelemetry, hour_of_day: float = 10.0) -> List[SafetyDecision]:
        """Calculates dynamic lighting and photoperiod regulation."""
        decisions: List[SafetyDecision] = []

        # Day/Night Photoperiod check
        is_day = hour_of_day < self.recipe.photoperiod_hours
        if is_day and not light.lights_on:
            dec = safety_engine.evaluate_action(
                source="AI_DECISION_ENGINE_LIGHT_CONTROLLER",
                proposed_action="SET_LIGHTING_STATE",
                parameters={"lights_on": True, "ppfd_target": self.recipe.target_dli_mol_m2_d / (self.recipe.photoperiod_hours * 3600) * 1e6}
            )
            decisions.append(dec)
        elif not is_day and light.lights_on:
            dec = safety_engine.evaluate_action(
                source="AI_DECISION_ENGINE_LIGHT_CONTROLLER",
                proposed_action="SET_LIGHTING_STATE",
                parameters={"lights_on": False, "ppfd_target": 0.0}
            )
            decisions.append(dec)

        self.action_history.extend(decisions)
        return decisions
