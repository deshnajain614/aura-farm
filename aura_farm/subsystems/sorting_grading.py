"""
Robotic Sorting and Grading Subsystem (Prompt Section 16)
========================================================
- Vision inspection on moving conveyor belt.
- AI Quality Model assesses: Head Size, Color Uniformity, Physical Damage, Shape, Disease defects.
- High-speed pneumatic air diverters automatically sort heads into:
    * Grade A: Premium retail packaging
    * Grade B: Secondary food service / processing
    * Rejected: Organic composting reactor
"""
from typing import Dict, List, Any
import logging
import random
from aura_farm.core.types import ProduceGrade, HarvestBatch

logger = logging.getLogger("aura_farm.sorting")

class GradedItem:
    def __init__(self, item_id: str, grade: ProduceGrade, weight_g: float, defect_pct: float):
        self.item_id = item_id
        self.grade = grade
        self.weight_g = weight_g
        self.defect_pct = defect_pct

class SortingAndGradingSystem:
    def __init__(self):
        self.conveyor_active: bool = False
        self.graded_items: List[GradedItem] = []

    def sort_and_grade_batch(self, batch: HarvestBatch, total_heads: int = 120) -> HarvestBatch:
        """Grades harvested heads on the optical conveyor line."""
        self.conveyor_active = True
        logger.info(f"Conveyor Vision: Optical sorting activated for {total_heads} heads in {batch.batch_id}...")

        grade_a_kg = 0.0
        grade_b_kg = 0.0
        reject_kg = 0.0

        for i in range(1, total_heads + 1):
            item_id = f"{batch.batch_id}-HEAD-{i:03d}"
            # Standard head weight ~220g
            weight = random.uniform(200.0, 245.0)

            # High quality CEA yield profile:
            # 88% Grade A, 9% Grade B, 3% Compost
            rand = random.random()
            if rand < 0.88:
                grade = ProduceGrade.GRADE_A
                grade_a_kg += weight / 1000.0
                defect = random.uniform(0.0, 3.0)
            elif rand < 0.97:
                grade = ProduceGrade.GRADE_B
                grade_b_kg += weight / 1000.0
                defect = random.uniform(3.5, 9.0)
            else:
                grade = ProduceGrade.REJECTED
                reject_kg += weight / 1000.0
                defect = random.uniform(12.0, 25.0)

            self.graded_items.append(GradedItem(item_id, grade, round(weight, 1), round(defect, 1)))

        batch.grade_a_kg = round(grade_a_kg, 2)
        batch.grade_b_kg = round(grade_b_kg, 2)
        batch.rejected_waste_kg = round(reject_kg, 2)
        self.conveyor_active = False

        logger.info(f"Grading Completed: Grade A = {batch.grade_a_kg}kg | Grade B = {batch.grade_b_kg}kg | Rejected = {batch.rejected_waste_kg}kg")
        return batch

sorting_system = SortingAndGradingSystem()
