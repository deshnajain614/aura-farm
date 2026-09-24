"""
Production Planner Subsystem (Prompt Sections 1 & 2)
===================================================
Calculates seed requirements, batch timelines, resource allocations,
and projected yields based on crop recipe matrices.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import time
from aura_farm.core.types import CropRecipe

CROP_CATALOG: Dict[str, CropRecipe] = {
    "Butterhead Lettuce": CropRecipe(
        crop_name="Butterhead Lettuce",
        germination_days=3,
        vegetative_days=18,
        maturity_days=26,
        harvest_target_weight_g=220.0,
        target_ph=6.0,
        target_ec_ms_cm=1.6,
        target_air_temp_day_c=22.0,
        target_air_temp_night_c=18.0,
        target_humidity_pct=65.0,
        target_co2_ppm=1000.0,
        target_dli_mol_m2_d=15.0,
        photoperiod_hours=16.0,
        requires_pruning=True,
        requires_pollination=False
    ),
    "Genovese Basil": CropRecipe(
        crop_name="Genovese Basil",
        germination_days=4,
        vegetative_days=16,
        maturity_days=24,
        harvest_target_weight_g=150.0,
        target_ph=6.2,
        target_ec_ms_cm=1.8,
        target_air_temp_day_c=24.0,
        target_air_temp_night_c=20.0,
        target_humidity_pct=60.0,
        target_co2_ppm=900.0,
        target_dli_mol_m2_d=16.5,
        photoperiod_hours=18.0,
        requires_pruning=True,
        requires_pollination=False
    ),
    "Albion Strawberries": CropRecipe(
        crop_name="Albion Strawberries",
        germination_days=7,
        vegetative_days=28,
        maturity_days=45,
        harvest_target_weight_g=30.0,
        target_ph=5.8,
        target_ec_ms_cm=1.9,
        target_air_temp_day_c=21.0,
        target_air_temp_night_c=16.0,
        target_humidity_pct=68.0,
        target_co2_ppm=1100.0,
        target_dli_mol_m2_d=18.0,
        photoperiod_hours=14.0,
        requires_pruning=True,
        requires_pollination=True
    ),
    "Cherry Tomatoes": CropRecipe(
        crop_name="Cherry Tomatoes",
        germination_days=5,
        vegetative_days=30,
        maturity_days=55,
        harvest_target_weight_g=25.0,
        target_ph=6.1,
        target_ec_ms_cm=2.4,
        target_air_temp_day_c=24.5,
        target_air_temp_night_c=19.0,
        target_humidity_pct=65.0,
        target_co2_ppm=1200.0,
        target_dli_mol_m2_d=22.0,
        photoperiod_hours=16.0,
        requires_pruning=True,
        requires_pollination=True
    )
}

class ProductionPlan(BaseModel):
    batch_id: str
    crop: CropRecipe
    target_plant_count: int = 120
    required_seeds: int = 132  # 10% safety buffer for germination variance
    channels_needed: int = 6
    estimated_yield_kg: float = 26.4
    created_at: float = Field(default_factory=time.time)

class ProductionPlanner:
    def __init__(self):
        self.catalog = CROP_CATALOG

    def get_recipe(self, crop_name: str) -> CropRecipe:
        return self.catalog.get(crop_name, self.catalog["Butterhead Lettuce"])

    def create_plan(self, crop_name: str, target_count: int = 120) -> ProductionPlan:
        recipe = self.get_recipe(crop_name)
        # 10% buffer for germination loss
        required_seeds = int(target_count * 1.10)
        channels_needed = max(1, target_count // 20)
        estimated_yield_kg = round((target_count * recipe.harvest_target_weight_g) / 1000.0, 2)
        batch_id = f"AURA-{crop_name[:4].upper()}-{int(time.time())}"

        return ProductionPlan(
            batch_id=batch_id,
            crop=recipe,
            target_plant_count=target_count,
            required_seeds=required_seeds,
            channels_needed=channels_needed,
            estimated_yield_kg=estimated_yield_kg
        )

production_planner = ProductionPlanner()
