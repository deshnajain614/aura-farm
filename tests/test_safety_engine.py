"""
Tests for Section 26: Multi-tier Safety Engine Gatekeeper
"""
import pytest
from aura_farm.core.safety_engine import SafetyEngine
from aura_farm.core.types import SafetyGate

def test_emergency_stop_hard_reject():
    engine = SafetyEngine()
    engine.set_emergency_stop(True, "Unit Test E-Stop")

    decision = engine.evaluate_action(
        source="AI_DECISION_ENGINE",
        proposed_action="DOSE_NUTRIENT_A",
        parameters={"volume_ml": 20.0}
    )

    assert decision.gate == SafetyGate.UNSAFE
    assert not decision.executed
    assert "Emergency Stop is engaged" in decision.reason

def test_max_single_dose_rejection():
    engine = SafetyEngine()
    # Limit is 120 ml, request 250 ml
    decision = engine.evaluate_action(
        source="AI_MODEL_ANOMALY",
        proposed_action="DOSE_NUTRIENT_A",
        parameters={"volume_ml": 250.0}
    )

    assert decision.gate == SafetyGate.UNSAFE
    assert not decision.executed
    assert "exceeds single dose safety limit" in decision.reason

def test_safe_dosing_allowed():
    engine = SafetyEngine()
    decision = engine.evaluate_action(
        source="AI_DECISION_ENGINE",
        proposed_action="DOSE_NUTRIENT_A",
        parameters={"volume_ml": 25.0}
    )

    assert decision.gate == SafetyGate.ALLOWED
    assert decision.executed

def test_climate_biological_bounds_rejection():
    engine = SafetyEngine()
    # Ambient max is 34°C, request 45°C
    decision = engine.evaluate_action(
        source="MALICIOUS_OR_BUGGY_AGENT",
        proposed_action="SET_CLIMATE_TARGETS",
        parameters={"temp_c": 45.0}
    )

    assert decision.gate == SafetyGate.UNSAFE
    assert not decision.executed
    assert "exceeds biological envelope" in decision.reason

def test_cip_zone_empty_check():
    engine = SafetyEngine()
    # Cannot flush if active crop present
    decision = engine.evaluate_action(
        source="CIP_CONTROLLER",
        proposed_action="TRIGGER_CIP_FLUSH",
        parameters={"is_zone_empty": False}
    )
    assert decision.gate == SafetyGate.UNSAFE
    assert not decision.executed
