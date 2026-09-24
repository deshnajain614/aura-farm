"""
Robotic Transplanting & Plant Positioning Subsystem (Prompt Sections 4 & 5)
===========================================================================
- Selectively transfers verified healthy seedlings from plug trays to growing channels.
- Skips unhealthy/stunted seedlings.
- Records full digital batch traceability: Batch -> Seedling -> Channel Location -> Health History.
- Manages vertical dynamic plant spacing across Nursery -> Vegetative -> Growth -> Maturity -> Harvest zones.
"""
from typing import Dict, List, Optional
import time
import logging
from aura_farm.core.types import PlantInstance, FarmZone, PlantHealthGrade
from aura_farm.core.safety_engine import safety_engine

logger = logging.getLogger("aura_farm.transplanting")

class TransplantingRobot:
    def __init__(self):
        self.active_plants: Dict[str, PlantInstance] = {}
        self.transplant_log: List[Dict[str, Any]] = []
        self.channel_capacity: int = 20
        self.gantry_state: str = "IDLE"

    def execute_transplant(
        self,
        batch_id: str,
        crop_name: str,
        candidate_count: int,
        unhealthy_flagged: List[str]
    ) -> List[PlantInstance]:
        """
        Picks healthy seedlings, skips unhealthy ones, places them into NFT/DWC channels,
        and creates digital twin plant records.
        """
        self.gantry_state = "TRANSPLANTING_IN_PROGRESS"
        transplanted_plants: List[PlantInstance] = []
        channel_idx = 1
        slot_idx = 1

        for i in range(1, candidate_count + 1):
            seedling_id = f"PLUG-{i:03d}"

            # Architectural Rule: If a seedling is unhealthy -> Robot skips it
            if seedling_id in unhealthy_flagged:
                logger.warning(f"Robotic Arm: Skipping stunted/defective seedling {seedling_id} per CV instruction.")
                continue

            plant_id = f"{batch_id}-{seedling_id}"
            plant = PlantInstance(
                plant_id=plant_id,
                batch_id=batch_id,
                crop_name=crop_name,
                zone=FarmZone.GROWTH,
                channel_index=channel_idx,
                slot_index=slot_idx,
                health=PlantHealthGrade.EXCELLENT,
                health_score_pct=99.0,
                growth_day=1,
                height_cm=4.5,
                biomass_estimated_g=8.0
            )

            self.active_plants[plant_id] = plant
            transplanted_plants.append(plant)

            # Advance channel and slot positions
            slot_idx += 1
            if slot_idx > self.channel_capacity:
                slot_idx = 1
                channel_idx += 1

        self.gantry_state = "TRANSPLANT_COMPLETE"
        logger.info(f"Transplant Complete: {len(transplanted_plants)} healthy plants placed into channels. Batch ID: {batch_id}")
        return transplanted_plants

    def reposition_plants_by_stage(self, plant_id: str, current_day: int, maturity_days: int) -> FarmZone:
        """
        Section 5: Autonomous plant positioning.
        Dynamically moves plants between zones to optimize light spacing and canopy density.
        Nursery -> Vegetative Zone -> Growth Zone -> Maturity Zone -> Harvest Zone
        """
        if plant_id not in self.active_plants:
            return FarmZone.GROWTH

        plant = self.active_plants[plant_id]
        stage_ratio = current_day / max(1, maturity_days)

        if stage_ratio < 0.20:
            target_zone = FarmZone.VEGETATIVE
        elif stage_ratio < 0.65:
            target_zone = FarmZone.GROWTH
        elif stage_ratio < 0.95:
            target_zone = FarmZone.MATURITY
        else:
            target_zone = FarmZone.HARVEST

        if plant.zone != target_zone:
            logger.info(f"Dynamic Spacing Shuttle: Moving {plant_id} from {plant.zone.value} to {target_zone.value}")
            plant.zone = target_zone

        return plant.zone

transplanting_robot = TransplantingRobot()
