"""
Tests for Closed-Loop AI Decision Engine
"""
import pytest
from aura_farm.core.decision_engine import DecisionEngine
from aura_farm.core.types import WaterTelemetry, ClimateTelemetry, CropRecipe, SafetyGate

def test_ph_correction_dosing():
    recipe = CropRecipe(crop_name="Butterhead Lettuce", target_ph=6.0)
    engine = DecisionEngine(recipe)

    # Telemetry: pH is 6.5 (> 6.0 target) -> should recommend DOSE_PH_DOWN
    water = WaterTelemetry(ph=6.5)
    decisions = engine.evaluate_water_nutrients(water)

    assert len(decisions) >= 1
    ph_dec = next((d for d in decisions if d.proposed_action == "DOSE_PH_DOWN"), None)
    assert ph_dec is not None
    assert ph_dec.gate == SafetyGate.ALLOWED
    assert ph_dec.parameters["volume_ml"] > 0

def test_nutrient_ec_correction_dosing():
    recipe = CropRecipe(crop_name="Butterhead Lettuce", target_ec_ms_cm=1.8)
    engine = DecisionEngine(recipe)

    # Telemetry: EC is 1.2 (depleted nutrients) -> should recommend DOSE_NUTRIENT_A and B
    water = WaterTelemetry(ec_ms_cm=1.2)
    decisions = engine.evaluate_water_nutrients(water)

    actions = [d.proposed_action for d in decisions]
    assert "DOSE_NUTRIENT_A" in actions
    assert "DOSE_NUTRIENT_B" in actions
