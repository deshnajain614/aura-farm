"""
Autonomous Nutrient Handling & Automated Dosing Subsystem (Prompt Section 7)
============================================================================
- Controls Stock Tanks (A, B, pH Down, pH Up).
- Automated peristaltic dosing pumps for closed-loop EC and pH balancing.
- Ultrasonic tank level sensors monitor remaining chemical volume.
- Automated bulk replenishment switchover from secondary backup cartridges.
- Safe operating mode fallback if backup cartridges are exhausted.
"""
from typing import Dict, Any
import logging
from aura_farm.core.types import NutrientTankState
from aura_farm.core.safety_engine import safety_engine

logger = logging.getLogger("aura_farm.nutrients")

class NutrientHandlingSystem:
    def __init__(self):
        self.state = NutrientTankState()
        self.dosing_pumps_active: Dict[str, bool] = {
            "PUMP_A": False,
            "PUMP_B": False,
            "PUMP_PH_DOWN": False,
            "PUMP_PH_UP": False
        }

    def check_levels_and_autorefill(self):
        """
        Detects low levels and triggers automated valve transfer from backup cartridges.
        Enters safe operating mode if replenishment is depleted.
        """
        tanks = [
            ("Tank A", self.state.tank_a_pct),
            ("Tank B", self.state.tank_b_pct),
            ("pH Down", self.state.ph_down_pct),
            ("pH Up", self.state.ph_up_pct)
        ]

        for name, level in tanks:
            if level < 15.0:
                logger.warning(f"Nutrient System: {name} is low ({level:.1f}%).")
                if self.state.backup_cartridges_available:
                    logger.info(f"Automated Refill: Transferring 10L from bulk backup cartridge into {name}...")
                    self.state.auto_refill_in_progress = True
                    # Replenish
                    if name == "Tank A":
                        self.state.tank_a_pct = 95.0
                    elif name == "Tank B":
                        self.state.tank_b_pct = 95.0
                    elif name == "pH Down":
                        self.state.ph_down_pct = 95.0
                    elif name == "pH Up":
                        self.state.ph_up_pct = 95.0
                    self.state.auto_refill_in_progress = False
                    logger.info(f"{name} refill verified at 95%.")
                else:
                    logger.critical(f"Nutrient Alert: No backup cartridge available for {name}! Entering SAFE OPERATING MODE.")
                    self.state.safe_operating_mode = True

    def dose_nutrient_a(self, ml: float) -> bool:
        if self.state.tank_a_pct <= 2.0:
            return False
        self.state.tank_a_pct = max(0.0, self.state.tank_a_pct - (ml / 50.0))
        logger.info(f"Nutrient Pump A: Dosed {ml:.1f} ml stock solution.")
        self.check_levels_and_autorefill()
        return True

    def dose_nutrient_b(self, ml: float) -> bool:
        if self.state.tank_b_pct <= 2.0:
            return False
        self.state.tank_b_pct = max(0.0, self.state.tank_b_pct - (ml / 50.0))
        logger.info(f"Nutrient Pump B: Dosed {ml:.1f} ml stock solution.")
        self.check_levels_and_autorefill()
        return True

    def dose_ph_down(self, ml: float) -> bool:
        if self.state.ph_down_pct <= 2.0:
            return False
        self.state.ph_down_pct = max(0.0, self.state.ph_down_pct - (ml / 40.0))
        logger.info(f"pH Dosing Pump: Dosed {ml:.1f} ml pH Down.")
        self.check_levels_and_autorefill()
        return True

    def dose_ph_up(self, ml: float) -> bool:
        if self.state.ph_up_pct <= 2.0:
            return False
        self.state.ph_up_pct = max(0.0, self.state.ph_up_pct - (ml / 40.0))
        logger.info(f"pH Dosing Pump: Dosed {ml:.1f} ml pH Up.")
        self.check_levels_and_autorefill()
        return True

nutrient_system = NutrientHandlingSystem()
