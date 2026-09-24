"""
Tests for Sections 6 & 7: Autonomous Water and Nutrient Handling
"""
import pytest
from aura_farm.subsystems.nutrient_system import NutrientHandlingSystem
from aura_farm.subsystems.water_utility import WaterUtilitySystem

def test_nutrient_low_level_triggers_automatic_refill():
    nutrients = NutrientHandlingSystem()
    nutrients.state.tank_a_pct = 10.0  # Below 15% threshold
    nutrients.state.backup_cartridges_available = True

    nutrients.check_levels_and_autorefill()

    # Automatically transferred from backup cartridge
    assert nutrients.state.tank_a_pct == 95.0
    assert not nutrients.state.safe_operating_mode

def test_nutrient_depleted_without_backup_triggers_safe_mode():
    nutrients = NutrientHandlingSystem()
    nutrients.state.tank_b_pct = 5.0
    nutrients.state.backup_cartridges_available = False

    nutrients.check_levels_and_autorefill()

    assert nutrients.state.safe_operating_mode

def test_water_leak_detection():
    water = WaterUtilitySystem()
    # High recovery loss triggers leak detection
    water.telemetry.recovery_recirculation_rate_pct = 80.0
    is_leak = water.check_for_leaks()

    assert is_leak
    assert water.telemetry.leak_detected
