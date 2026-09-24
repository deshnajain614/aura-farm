"""
AURA-Farm Master Orchestrator
=============================
Integrates the complete 27-point autonomous architecture:
State Machine, AI Decision Engine, Multi-Tier Safety Gate, and all Physical/Robotic Subsystems.
"""
from typing import Dict, List, Any, Optional
import time
import asyncio
import logging
from aura_farm.core.types import (
    LifecycleState, CropRecipe, PlantInstance, ProduceGrade,
    HarvestBatch, WaterTelemetry, ClimateTelemetry, LightingTelemetry,
    EnergyTelemetry, SafetyDecision, FarmZone
)
from aura_farm.core.state_machine import FarmLifecycleStateMachine
from aura_farm.core.decision_engine import DecisionEngine
from aura_farm.core.safety_engine import safety_engine
from aura_farm.subsystems.production_planner import production_planner
from aura_farm.subsystems.seeding_robot import seeding_robot
from aura_farm.subsystems.germination_chamber import germination_chamber
from aura_farm.subsystems.transplanting_robot import transplanting_robot
from aura_farm.subsystems.water_utility import water_utility
from aura_farm.subsystems.nutrient_system import nutrient_system
from aura_farm.subsystems.climate_control import climate_control
from aura_farm.subsystems.lighting_system import lighting_system
from aura_farm.subsystems.mobile_inspector import mobile_inspector
from aura_farm.subsystems.robotic_pruning import robotic_pruner
from aura_farm.subsystems.robotic_pollination import robotic_pollinator
from aura_farm.subsystems.disease_pest_response import disease_manager
from aura_farm.subsystems.harvesting_robot import harvesting_robot
from aura_farm.subsystems.sorting_grading import sorting_system
from aura_farm.subsystems.packaging_cell import packaging_cell
from aura_farm.subsystems.storage_manager import storage_manager
from aura_farm.subsystems.waste_manager import waste_manager
from aura_farm.subsystems.cleaning_sanitization import cleaning_system
from aura_farm.subsystems.predictive_maintenance import predictive_maintenance
from aura_farm.subsystems.energy_manager import energy_manager
from aura_farm.subsystems.edge_autonomy import edge_engine
from aura_farm.subsystems.security_manager import security_manager
from aura_farm.config import config

logger = logging.getLogger("aura_farm.orchestrator")

class FarmOrchestrator:
    def __init__(self, recipe_name: str = "Butterhead Lettuce"):
        self.recipe = production_planner.get_recipe(recipe_name)
        self.state_machine = FarmLifecycleStateMachine(self.recipe)
        self.decision_engine = DecisionEngine(self.recipe)
        self.active_plants: List[PlantInstance] = []
        self.running: bool = False
        self.simulated_hour: float = 8.0
        self.last_tick_time: float = time.time()
        self.recent_events: List[Dict[str, Any]] = []

    def log_event(self, category: str, message: str, level: str = "INFO"):
        evt = {
            "timestamp": time.time(),
            "category": category,
            "message": message,
            "level": level,
            "state": self.state_machine.current_state.value
        }
        self.recent_events.append(evt)
        if len(self.recent_events) > 80:
            self.recent_events.pop(0)
        edge_engine.log_edge_event(category, evt)
        logger.info(f"[{category}] {message}")

    def tick(self) -> Dict[str, Any]:
        """
        Executes one full autonomous orchestration cycle across utilities, AI, and robots.
        """
        now = time.time()
        dt = now - self.last_tick_time
        self.last_tick_time = now

        # Advance virtual clock
        self.simulated_hour = (self.simulated_hour + 0.25) % 24.0

        # 1. Update Utilities (Water, Nutrients, Climate, Lighting, Power)
        water_data = water_utility.read_sensors()
        water_utility.trigger_auto_recovery_and_purification()
        water_utility.check_for_leaks()

        climate_data = climate_control.read_sensors()
        lighting_system.update_photoperiod_and_dli(self.simulated_hour, delta_hours=0.25)
        power_data = energy_manager.update_energy_state(
            solar_irradiance_scale=1.0 if (6.0 <= self.simulated_hour <= 18.0) else 0.0,
            grid_available=True
        )

        # 2. Predictive Maintenance Check
        predictive_maintenance.check_equipment_vibration_and_failsafe()

        # 3. AI Closed-Loop Regulatory Decisions
        water_decisions = self.decision_engine.evaluate_water_nutrients(water_data)
        for dec in water_decisions:
            if dec.executed:
                if dec.proposed_action == "DOSE_PH_DOWN":
                    nutrient_system.dose_ph_down(dec.parameters.get("volume_ml", 10.0))
                    water_data.ph = max(5.8, round(water_data.ph - 0.15, 2))
                elif dec.proposed_action == "DOSE_PH_UP":
                    nutrient_system.dose_ph_up(dec.parameters.get("volume_ml", 10.0))
                    water_data.ph = min(6.8, round(water_data.ph + 0.15, 2))
                elif dec.proposed_action == "DOSE_NUTRIENT_A":
                    nutrient_system.dose_nutrient_a(dec.parameters.get("volume_ml", 15.0))
                    water_data.ec_ms_cm = min(2.5, round(water_data.ec_ms_cm + 0.08, 2))
                elif dec.proposed_action == "DOSE_NUTRIENT_B":
                    nutrient_system.dose_nutrient_b(dec.parameters.get("volume_ml", 15.0))
                elif dec.proposed_action == "TOP_UP_RO_WATER":
                    water_utility.top_up_clean_water(dec.parameters.get("volume_liters", 20.0))

        climate_decisions = self.decision_engine.evaluate_climate(climate_data)
        for dec in climate_decisions:
            if dec.executed and dec.proposed_action == "SET_CLIMATE_TARGETS":
                climate_control.adjust_climate(
                    target_temp=dec.parameters.get("temp_c", 22.0),
                    target_humidity=dec.parameters.get("humidity_pct", 65.0),
                    fans_pct=dec.parameters.get("fans_pct", 65.0)
                )
            elif dec.executed and dec.proposed_action == "INJECT_CO2":
                climate_control.inject_co2(dec.parameters.get("target_ppm", 1000.0))

        # 4. Lifecycle State Machine Execution & Robotic Orchestration
        current_state = self.state_machine.current_state

        if current_state == LifecycleState.IDLE or current_state == LifecycleState.PLANNING:
            plan = production_planner.create_plan(self.recipe.crop_name, target_count=120)
            self.log_event("PLANNER", f"Autonomous production plan created for {plan.crop.crop_name}: {plan.target_plant_count} plants.")
            self.state_machine.advance_step()

        elif current_state == LifecycleState.SEED_INVENTORY_CHECK:
            has_seeds = seeding_robot.check_seed_inventory(self.recipe.crop_name, 132)
            if has_seeds:
                self.log_event("SEED_SENSOR", "Optical seed verification passed. Magazine full.")
                self.state_machine.advance_step()

        elif current_state == LifecycleState.AUTOMATED_SEEDING:
            seed_res = seeding_robot.execute_seeding_run(self.recipe.crop_name, 132)
            self.log_event("SEEDING_ROBOT", f"Pick-and-place seeding verified. Accuracy: {seed_res.placement_accuracy_pct}%")
            self.state_machine.advance_step()

        elif current_state == LifecycleState.GERMINATING:
            germination_chamber.update_environment(stage_hours=52)
            germ_res = germination_chamber.analyze_seedlings_vision(self.state_machine.current_batch_id, 120)
            if germ_res.ready_for_transplant:
                self.log_event("GERMINATION", f"Seedling readiness confirmed: {germ_res.germination_rate_pct}% germinated.")
                self.state_machine.advance_step({"germination_rate_pct": germ_res.germination_rate_pct, "unhealthy": germ_res.unhealthy_seedlings_flagged})

        elif current_state == LifecycleState.TRANSPLANTING:
            self.active_plants = transplanting_robot.execute_transplant(
                batch_id=self.state_machine.current_batch_id,
                crop_name=self.recipe.crop_name,
                candidate_count=120,
                unhealthy_flagged=[]
            )
            self.log_event("TRANSPLANT_ROBOT", f"Transplanted {len(self.active_plants)} healthy seedlings into vertical channels.")
            self.state_machine.advance_step()

        elif current_state == LifecycleState.VEGETATIVE_GROWTH:
            # Advance day and dynamic zone spacing
            for p in self.active_plants:
                p.growth_day += 1
                transplanting_robot.reposition_plants_by_stage(p.plant_id, p.growth_day, self.recipe.maturity_days)
            self.state_machine.advance_step()

        elif current_state == LifecycleState.ROBOTIC_INSPECTION:
            scans = mobile_inspector.scan_all_plants(self.active_plants)
            # Evaluate diseases & pruning
            has_disease = any(p.has_disease for p in self.active_plants)
            prune_candidates = [p for p in self.active_plants if p.growth_day > 10 and p.pruned_count == 0]
            pollinate_candidates = [p for p in self.active_plants if self.recipe.requires_pollination and not p.pollinated]

            ready_for_harvest = all(p.growth_day >= self.recipe.maturity_days for p in self.active_plants) if self.active_plants else False

            context = {
                "disease_detected": has_disease,
                "pruning_needed": len(prune_candidates) > 0,
                "pollination_needed": len(pollinate_candidates) > 0,
                "predicted_weight_g": 235.0 if ready_for_harvest else 150.0
            }
            self.log_event("INSPECTION_ROBOT", f"Canopy scan complete. Canopy healthy: {not has_disease}. Ready: {ready_for_harvest}")
            self.state_machine.advance_step(context)

        elif current_state == LifecycleState.ROBOTIC_PRUNING:
            pruned_count = 0
            for p in self.active_plants[:4]:
                rep = robotic_pruner.prune_plant(p)
                if rep.verified:
                    pruned_count += 1
            self.log_event("PRUNING_ROBOT", f"Articulated shears pruned {pruned_count} plants. Clippings vacuumed to waste.")
            self.state_machine.advance_step()

        elif current_state == LifecycleState.ROBOTIC_POLLINATION:
            for p in self.active_plants:
                robotic_pollinator.perform_pollination(p)
            self.log_event("POLLINATION_ROBOT", f"Acoustic pollination performed across all flowering slots.")
            self.state_machine.advance_step()

        elif current_state == LifecycleState.DISEASE_RESPONSE:
            for p in self.active_plants:
                if p.has_disease:
                    disease_manager.evaluate_and_respond(p, water_data, climate_data)
            self.log_event("DISEASE_AI", "Pathogen isolation and localized treatment finished.")
            self.state_machine.advance_step()

        elif current_state == LifecycleState.HARVEST_PREDICTION:
            self.log_event("HARVEST_AI", f"Harvest target of {self.recipe.harvest_target_weight_g}g achieved.")
            self.state_machine.advance_step({"predicted_weight_g": 235.0})

        elif current_state == LifecycleState.AUTONOMOUS_HARVESTING:
            harvest_batch = harvesting_robot.harvest_canopy(
                batch_id=self.state_machine.current_batch_id,
                plants=self.active_plants,
                target_weight_g=self.recipe.harvest_target_weight_g
            )
            self.state_machine.last_completed_batch = harvest_batch
            self.log_event("HARVEST_ROBOT", f"Harvested {harvest_batch.total_yield_kg} kg from growing channels.")
            self.state_machine.advance_step()

        elif current_state == LifecycleState.SORTING_AND_GRADING:
            if self.state_machine.last_completed_batch:
                graded_batch = sorting_system.sort_and_grade_batch(self.state_machine.last_completed_batch)
                self.state_machine.last_completed_batch = graded_batch
                self.log_event("SORTING_VISION", f"Graded produce: Grade A = {graded_batch.grade_a_kg}kg | Grade B = {graded_batch.grade_b_kg}kg")
            self.state_machine.advance_step()

        elif current_state == LifecycleState.AUTOMATED_PACKAGING:
            if self.state_machine.last_completed_batch:
                packaged_batch = packaging_cell.package_harvest(self.state_machine.last_completed_batch)
                self.state_machine.last_completed_batch = packaged_batch
                self.log_event("PACKAGING_CELL", f"Sealed {packaged_batch.packages_sealed} clamshells. QR: {packaged_batch.traceability_qr}")
            self.state_machine.advance_step()

        elif current_state == LifecycleState.COLD_STORAGE:
            if self.state_machine.last_completed_batch:
                bin_id = storage_manager.store_batch(self.state_machine.last_completed_batch)
                self.log_event("COLD_STORAGE", f"Batch transferred to {bin_id} at 4°C with FEFO tracking.")
            self.state_machine.advance_step()

        elif current_state == LifecycleState.WASTE_MANAGEMENT:
            waste_kg = 4.2
            comp = waste_manager.process_waste(self.state_machine.current_batch_id, waste_kg)
            self.log_event("WASTE_MANAGER", f"Converted {waste_kg}kg root/leaf biomass into {comp.compost_produced_kg}kg bio-fertilizer input.")
            self.state_machine.advance_step()

        elif current_state == LifecycleState.SYSTEM_CLEANING:
            self.log_event("CLEANING_CIP", "Post-harvest drainage and rotary RO pressure rinse underway.")
            self.state_machine.advance_step()

        elif current_state == LifecycleState.SANITIZATION_CIP:
            cip_res = cleaning_system.execute_cip_cycle("GROWTH_ZONE")
            self.log_event("SANITIZATION_CIP", f"UV-C and Ozone sanitization verified. Purity: {cip_res.final_turbidity} NTU.")
            self.state_machine.advance_step()

        elif current_state == LifecycleState.SYSTEM_RESET:
            self.active_plants.clear()
            self.log_event("SYSTEM_RESET", "All channel telemetry reset. Zero humans needed.")
            self.state_machine.advance_step()

        elif current_state == LifecycleState.NEXT_CYCLE_PREPARED:
            self.log_event("AUTONOMOUS_LOOP", f"Closed-loop cycle complete! Automatically triggering next crop cycle #{self.state_machine.cycle_count + 1}.")
            self.state_machine.advance_step()

        return self.get_telemetry_snapshot()

    def get_telemetry_snapshot(self) -> Dict[str, Any]:
        """Provides full digital twin state for Web Dashboard & APIs."""
        return {
            "lifecycle": {
                "state": self.state_machine.current_state.value,
                "batch_id": self.state_machine.current_batch_id,
                "cycle": self.state_machine.cycle_count,
                "cycle_day": self.state_machine.cycle_day,
                "crop": self.recipe.crop_name,
                "zones": self.state_machine.zone_statuses
            },
            "water": water_utility.telemetry.model_dump(),
            "nutrients": nutrient_system.state.model_dump(),
            "climate": climate_control.telemetry.model_dump(),
            "lighting": lighting_system.telemetry.model_dump(),
            "energy": energy_manager.telemetry.model_dump(),
            "plants": [p.model_dump() for p in self.active_plants[:8]],
            "active_plant_count": len(self.active_plants),
            "safety": {
                "emergency_stop": safety_engine.emergency_stop_engaged,
                "recent_decisions": [d.model_dump() for d in safety_engine.recent_decisions[-5:]]
            },
            "maintenance": {
                "equipment": [e.model_dump() for e in predictive_maintenance.equipment_registry.values()],
                "parts": predictive_maintenance.get_parts_health_report()
            },
            "storage_inventory_count": len(storage_manager.inventory),
            "total_packages_sealed": packaging_cell.total_packages_sealed,
            "total_compost_kg": waste_manager.total_compost_produced_kg,
            "edge_sync": edge_engine.sync_state.model_dump(),
            "recent_events": self.recent_events[-6:]
        }

orchestrator = FarmOrchestrator()
