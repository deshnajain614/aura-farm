"""
Automated Germination Chamber Subsystem (Prompt Section 3)
=========================================================
Controls germination microclimate (dark/light, humidity, misting, air flow)
and performs computer vision analysis on seedling emergence & vigor.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import time
import random
import logging

logger = logging.getLogger("aura_farm.germination")

class GerminationAnalysisResult(BaseModel):
    batch_id: str
    total_seeds: int
    germinated_count: int
    germination_rate_pct: float
    average_radicle_length_mm: float
    average_health_score_pct: float
    ready_for_transplant: bool
    unhealthy_seedlings_flagged: List[str] = []

class GerminationChamber:
    def __init__(self):
        self.temperature_c: float = 23.5
        self.humidity_pct: float = 94.0
        self.misting_active: bool = False
        self.circulation_fan_pct: float = 35.0
        self.photoperiod_active: bool = False # Darkness during initial 48h
        self.days_in_chamber: float = 0.0

    def update_environment(self, stage_hours: float):
        """Simulates chamber environmental regime as seeds sprout."""
        self.days_in_chamber = round(stage_hours / 24.0, 1)
        if stage_hours < 48:
            # Dark, high humidity period
            self.photoperiod_active = False
            self.humidity_pct = 95.0
            self.temperature_c = 24.0
        else:
            # Low-intensity nursery light turned on to prevent etiolation (stretching)
            self.photoperiod_active = True
            self.humidity_pct = 85.0
            self.temperature_c = 22.5

    def analyze_seedlings_vision(self, batch_id: str, total_seeds: int = 120) -> GerminationAnalysisResult:
        """
        AI Computer Vision Analysis of seedling canopy image.
        Assesses germination rate, root/shoot vigor, and tags stunted seedlings for skipping.
        """
        unhealthy: List[str] = []
        germinated = 0

        for i in range(1, total_seeds + 1):
            seedling_id = f"PLUG-{i:03d}"
            # Realistic biological germination outcome: ~97% sprout rate
            if random.random() < 0.97:
                germinated += 1
                # 2% stunted/damping-off
                if random.random() < 0.02:
                    unhealthy.append(seedling_id)

        germ_rate = round((germinated / total_seeds) * 100.0, 1)
        avg_radicle = round(random.uniform(14.0, 22.0), 1)
        avg_health = round(random.uniform(94.0, 99.0), 1)
        ready = (germ_rate >= 90.0 and avg_radicle >= 12.0)

        logger.info(f"AI Germination Vision: {batch_id} -> Germ Rate: {germ_rate}% | Health: {avg_health}% | Ready: {ready}")

        return GerminationAnalysisResult(
            batch_id=batch_id,
            total_seeds=total_seeds,
            germinated_count=germinated,
            germination_rate_pct=germ_rate,
            average_radicle_length_mm=avg_radicle,
            average_health_score_pct=avg_health,
            ready_for_transplant=ready,
            unhealthy_seedlings_flagged=unhealthy
        )

germination_chamber = GerminationChamber()
