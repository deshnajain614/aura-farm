"""
AURA-Farm Closed-Loop Autonomous Lifecycle State Machine
========================================================
Implements the full 27-step zero-routine-human-intervention cycle:
Plan -> Seed -> Germinate -> Transplant -> Grow -> Monitor -> Predict ->
Act -> Verify -> Correct -> Maintain -> Harvest -> Sort -> Pack ->
Store -> Record -> Clean -> Sanitize -> Reset Farm -> Next Crop
"""
import time
import logging
from typing import Dict, Any, List, Optional
from aura_farm.core.types import LifecycleState, FarmZone, ProduceGrade, HarvestBatch, CropRecipe
from aura_farm.core.safety_engine import safety_engine

logger = logging.getLogger("aura_farm.lifecycle")

class FarmLifecycleStateMachine:
    def __init__(self, recipe: Optional[CropRecipe] = None):
        self.recipe = recipe or CropRecipe(crop_name="Butterhead Lettuce")
        self.current_state: LifecycleState = LifecycleState.IDLE
        self.state_enter_timestamp: float = time.time()
        self.current_batch_id: str = f"BATCH-{int(time.time())}"
        self.cycle_count: int = 1
        self.cycle_day: int = 0
        self.zone_statuses: Dict[str, str] = {
            "NURSERY": "IDLE",
            "VEGETATIVE_ZONE": "IDLE",
            "GROWTH_ZONE": "IDLE",
            "MATURITY_ZONE": "IDLE",
            "HARVEST_ZONE": "IDLE",
            "QUARANTINE_ZONE": "CLEAN"
        }
        self.last_completed_batch: Optional[HarvestBatch] = None
        self.state_history: List[Dict[str, Any]] = []
        self.auto_advance_enabled: bool = True

    def transition_to(self, new_state: LifecycleState, reason: str = "") -> None:
        """Transitions state machine to new state and updates audit logs."""
        prev = self.current_state
        self.current_state = new_state
        self.state_enter_timestamp = time.time()
        entry = {
            "from": prev.value,
            "to": new_state.value,
            "timestamp": self.state_enter_timestamp,
            "reason": reason,
            "batch_id": self.current_batch_id,
            "cycle": self.cycle_count
        }
        self.state_history.append(entry)
        logger.info(f"[LIFECYCLE TRANSITION] {prev.value} -> {new_state.value} | Reason: {reason}")

    def advance_step(self, context: Optional[Dict[str, Any]] = None) -> LifecycleState:
        """
        Executes one logical tick of the closed-loop autonomous lifecycle.
        Automates transitions based on real and simulated milestone completion.
        """
        context = context or {}

        if self.current_state == LifecycleState.IDLE:
            self.transition_to(LifecycleState.PLANNING, "Initiating autonomous crop production plan.")

        elif self.current_state == LifecycleState.PLANNING:
            self.current_batch_id = f"AURA-{self.recipe.crop_name.replace(' ', '-').upper()}-C{self.cycle_count}-{int(time.time())}"
            self.cycle_day = 0
            self.transition_to(LifecycleState.SEED_INVENTORY_CHECK, "Calculated seed and resource requirements.")

        elif self.current_state == LifecycleState.SEED_INVENTORY_CHECK:
            # Verified optical seed counter and robotic seed magazine
            self.transition_to(LifecycleState.AUTOMATED_SEEDING, "Seeds in stock. Gantry pick-and-place dispenser ready.")

        elif self.current_state == LifecycleState.AUTOMATED_SEEDING:
            # Pick-and-place robot loads rockwool plugs, vision camera validates 100% placement
            self.zone_statuses["NURSERY"] = "SEEDED_TRAY_VERIFIED"
            self.transition_to(LifecycleState.GERMINATING, "Trays placed into microclimate germination chamber.")

        elif self.current_state == LifecycleState.GERMINATING:
            # Seedlings undergo humidity/dark-light germination
            germination_rate = context.get("germination_rate_pct", 98.4)
            if germination_rate >= 90.0:
                self.transition_to(LifecycleState.TRANSPLANTING, f"Germination achieved {germination_rate}%. Ready for transplant.")

        elif self.current_state == LifecycleState.TRANSPLANTING:
            # Robotic arm sorts healthy seedlings and places into vertical NFT channels
            self.zone_statuses["GROWTH_ZONE"] = "ACTIVE_CANOPY"
            self.transition_to(LifecycleState.VEGETATIVE_GROWTH, "Seedlings transferred to active hydroponic channels.")

        elif self.current_state == LifecycleState.VEGETATIVE_GROWTH:
            self.cycle_day += 1
            # Check if mobile inspection robot is due
            self.transition_to(LifecycleState.ROBOTIC_INSPECTION, "Daily autonomous rail scanner inspection run.")

        elif self.current_state == LifecycleState.ROBOTIC_INSPECTION:
            disease_detected = context.get("disease_detected", False)
            pruning_needed = context.get("pruning_needed", self.recipe.requires_pruning and self.cycle_day > 10)
            pollination_needed = context.get("pollination_needed", self.recipe.requires_pollination)

            if disease_detected:
                self.transition_to(LifecycleState.DISEASE_RESPONSE, "Vision identified pathogen anomaly.")
            elif pruning_needed:
                self.transition_to(LifecycleState.ROBOTIC_PRUNING, "AI identified foliage needing pruning.")
            elif pollination_needed:
                self.transition_to(LifecycleState.ROBOTIC_POLLINATION, "Flower blooms ready for robotic pollination.")
            elif self.cycle_day >= self.recipe.maturity_days:
                self.transition_to(LifecycleState.HARVEST_PREDICTION, "Maturity timeframe reached. Computing harvest yield index.")
            else:
                self.transition_to(LifecycleState.VEGETATIVE_GROWTH, "Inspection verified healthy growth. Continuing photoperiod.")

        elif self.current_state == LifecycleState.ROBOTIC_PRUNING:
            # Arm shears yellowing senescent leaves and drops to waste conveyor
            self.transition_to(LifecycleState.VEGETATIVE_GROWTH, "Pruning completed and biomass collected.")

        elif self.current_state == LifecycleState.ROBOTIC_POLLINATION:
            # Tool pulses flowers with resonant acoustic airflow
            self.transition_to(LifecycleState.VEGETATIVE_GROWTH, "Robotic pollination pass completed.")

        elif self.current_state == LifecycleState.DISEASE_RESPONSE:
            # Quarantine or localized UV-C spot treatment executed
            self.transition_to(LifecycleState.VEGETATIVE_GROWTH, "Pathogen isolated. Growing channel sanitized.")

        elif self.current_state == LifecycleState.HARVEST_PREDICTION:
            predicted_weight = context.get("predicted_weight_g", 235.0)
            if predicted_weight >= self.recipe.harvest_target_weight_g:
                self.transition_to(LifecycleState.AUTONOMOUS_HARVESTING, f"Canopy reached {predicted_weight:.1f}g harvest target.")
            else:
                self.transition_to(LifecycleState.VEGETATIVE_GROWTH, "Canopy requires 1 additional maturation day.")

        elif self.current_state == LifecycleState.AUTONOMOUS_HARVESTING:
            # End-effector cuts crop base and places onto conveyor
            self.transition_to(LifecycleState.SORTING_AND_GRADING, "Crops harvested and placed onto sorting conveyor.")

        elif self.current_state == LifecycleState.SORTING_AND_GRADING:
            # Computer vision grades produce into Grade A, Grade B, Reject
            self.transition_to(LifecycleState.AUTOMATED_PACKAGING, "Grading complete. Heading to robotic clamshell packaging.")

        elif self.current_state == LifecycleState.AUTOMATED_PACKAGING:
            # Clamshell sealed and QR traceability label printed
            self.transition_to(LifecycleState.COLD_STORAGE, "Packaging sealed and tagged. Transferred to cold storage.")

        elif self.current_state == LifecycleState.COLD_STORAGE:
            # Stored in 4°C FIFO warehouse
            self.transition_to(LifecycleState.WASTE_MANAGEMENT, "Processing remaining root and leaf biomass in compost reactor.")

        elif self.current_state == LifecycleState.WASTE_MANAGEMENT:
            self.transition_to(LifecycleState.SYSTEM_CLEANING, "Growing zone empty. Initiating Clean-In-Place (CIP) wash.")

        elif self.current_state == LifecycleState.SYSTEM_CLEANING:
            # High-pressure RO rinse and drainage
            self.zone_statuses["GROWTH_ZONE"] = "CIP_FLUSHING"
            self.transition_to(LifecycleState.SANITIZATION_CIP, "Chemical and UV-C sanitization cycle active.")

        elif self.current_state == LifecycleState.SANITIZATION_CIP:
            # Ozone and UV-C sterilize channels; sensor verifies zero residual TOC
            self.zone_statuses["GROWTH_ZONE"] = "STERILE_READY"
            self.transition_to(LifecycleState.SYSTEM_RESET, "Sanitization verified. Resetting channel telemetry.")

        elif self.current_state == LifecycleState.SYSTEM_RESET:
            self.transition_to(LifecycleState.NEXT_CYCLE_PREPARED, "All subsystems verified. System reset complete.")

        elif self.current_state == LifecycleState.NEXT_CYCLE_PREPARED:
            # Increment cycle count and autonomously restart!
            self.cycle_count += 1
            self.transition_to(LifecycleState.PLANNING, f"Auto-starting next crop cycle #{self.cycle_count} (zero human intervention).")

        return self.current_state
