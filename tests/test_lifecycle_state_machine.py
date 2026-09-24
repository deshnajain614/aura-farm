"""
Tests for Section 1 & 27: Autonomous Closed-Loop Lifecycle State Machine
"""
import pytest
from aura_farm.core.state_machine import FarmLifecycleStateMachine
from aura_farm.core.types import LifecycleState, CropRecipe

def test_full_autonomous_cycle_progression():
    recipe = CropRecipe(
        crop_name="Butterhead Lettuce",
        germination_days=3,
        vegetative_days=18,
        maturity_days=26,
        harvest_target_weight_g=220.0
    )
    sm = FarmLifecycleStateMachine(recipe)

    # 1. IDLE -> PLANNING
    state = sm.advance_step()
    assert state == LifecycleState.PLANNING

    # 2. PLANNING -> SEED_INVENTORY_CHECK
    state = sm.advance_step()
    assert state == LifecycleState.SEED_INVENTORY_CHECK

    # 3. SEED_INVENTORY_CHECK -> AUTOMATED_SEEDING
    state = sm.advance_step()
    assert state == LifecycleState.AUTOMATED_SEEDING

    # 4. AUTOMATED_SEEDING -> GERMINATING
    state = sm.advance_step()
    assert state == LifecycleState.GERMINATING

    # 5. GERMINATING -> TRANSPLANTING
    state = sm.advance_step({"germination_rate_pct": 98.0})
    assert state == LifecycleState.TRANSPLANTING

    # 6. TRANSPLANTING -> VEGETATIVE_GROWTH
    state = sm.advance_step()
    assert state == LifecycleState.VEGETATIVE_GROWTH

    # 7. VEGETATIVE_GROWTH -> ROBOTIC_INSPECTION
    state = sm.advance_step()
    assert state == LifecycleState.ROBOTIC_INSPECTION

    # Simulate fast forwarding to harvest day
    sm.cycle_day = 28
    state = sm.advance_step({
        "disease_detected": False,
        "pruning_needed": False,
        "pollination_needed": False
    })
    assert state == LifecycleState.HARVEST_PREDICTION

    # HARVEST_PREDICTION -> AUTONOMOUS_HARVESTING
    state = sm.advance_step({"predicted_weight_g": 235.0})
    assert state == LifecycleState.AUTONOMOUS_HARVESTING

    # AUTONOMOUS_HARVESTING -> SORTING_AND_GRADING
    state = sm.advance_step()
    assert state == LifecycleState.SORTING_AND_GRADING

    # SORTING_AND_GRADING -> AUTOMATED_PACKAGING
    state = sm.advance_step()
    assert state == LifecycleState.AUTOMATED_PACKAGING

    # AUTOMATED_PACKAGING -> COLD_STORAGE
    state = sm.advance_step()
    assert state == LifecycleState.COLD_STORAGE

    # COLD_STORAGE -> WASTE_MANAGEMENT
    state = sm.advance_step()
    assert state == LifecycleState.WASTE_MANAGEMENT

    # WASTE_MANAGEMENT -> SYSTEM_CLEANING
    state = sm.advance_step()
    assert state == LifecycleState.SYSTEM_CLEANING

    # SYSTEM_CLEANING -> SANITIZATION_CIP
    state = sm.advance_step()
    assert state == LifecycleState.SANITIZATION_CIP

    # SANITIZATION_CIP -> SYSTEM_RESET
    state = sm.advance_step()
    assert state == LifecycleState.SYSTEM_RESET

    # SYSTEM_RESET -> NEXT_CYCLE_PREPARED
    state = sm.advance_step()
    assert state == LifecycleState.NEXT_CYCLE_PREPARED

    # NEXT_CYCLE_PREPARED -> Automatically restarts at PLANNING with cycle #2!
    state = sm.advance_step()
    assert state == LifecycleState.PLANNING
    assert sm.cycle_count == 2
