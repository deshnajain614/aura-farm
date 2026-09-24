"""
Autonomous Storage Management Subsystem (Prompt Section 18)
===========================================================
- Controls cold storage room atmosphere (target 3.5 - 4.5°C, 92% RH, ethylene filtration).
- Implements FIFO (First In, First Out) and FEFO (First Expired, First Out) inventory matrix.
- Generates autonomous dispatch queues for cold-chain handoff.
"""
from typing import Dict, List, Optional
import time
import logging
from aura_farm.core.types import HarvestBatch

logger = logging.getLogger("aura_farm.storage")

class StorageBin:
    def __init__(self, bin_id: str, batch: HarvestBatch, expiry_timestamp: float):
        self.bin_id = bin_id
        self.batch = batch
        self.stored_at = time.time()
        self.expiry_timestamp = expiry_timestamp

class AutonomousStorageManager:
    def __init__(self):
        self.storage_temp_c: float = 4.0
        self.storage_humidity_pct: float = 92.0
        self.ethylene_scrubber_active: bool = True
        self.inventory: List[StorageBin] = []

    def store_batch(self, batch: HarvestBatch, shelf_life_days: int = 14) -> str:
        """Stores packaged batch in climate-controlled storage gantry."""
        bin_id = f"COLD-BAY-{len(self.inventory) + 1:02d}"
        expiry = time.time() + (shelf_life_days * 86400.0)
        bin_item = StorageBin(bin_id, batch, expiry)
        self.inventory.append(bin_item)
        batch.cold_storage_location = bin_id
        logger.info(f"Cold Storage: Placed {batch.packages_sealed} units from {batch.batch_id} into {bin_id} at {self.storage_temp_c}°C.")
        return bin_id

    def get_fefo_dispatch_queue(self) -> List[StorageBin]:
        """Sorts inventory using First-Expired, First-Out (FEFO) logic."""
        sorted_bins = sorted(self.inventory, key=lambda b: b.expiry_timestamp)
        return sorted_bins

storage_manager = AutonomousStorageManager()
