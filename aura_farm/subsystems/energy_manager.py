"""
Autonomous Microgrid Energy Management Subsystem (Prompt Section 23)
====================================================================
Manages Solar PV, Battery Storage (BESS), Grid Interconnect, and facility loads.
Implements 3-tier priority power shedding:
- Tier 1 (Critical): Life-support water circulation, root aeration, edge controllers, core sensors.
- Tier 2 (Essential): Climate HVAC, dehumidification, air circulation fans.
- Tier 3 (Curtailable): High-intensity supplemental LED grow lights.
"""
from typing import Dict, Any
import logging
from aura_farm.core.types import EnergyTelemetry

logger = logging.getLogger("aura_farm.energy")

class AutonomousEnergyManager:
    def __init__(self):
        self.telemetry = EnergyTelemetry()

    def update_energy_state(self, solar_irradiance_scale: float = 1.0, grid_available: bool = True) -> EnergyTelemetry:
        """Simulates microgrid balances and executes priority shedding when power drops."""
        # Solar generation varies with daylight (0 to 6000W)
        self.telemetry.solar_generation_w = round(4800.0 * max(0.0, solar_irradiance_scale), 1)

        # Baseline facility consumption
        tier_1 = 650.0   # Circulation & controllers (MUST NOT STOP)
        tier_2 = 1450.0  # HVAC cooling
        tier_3 = 1800.0  # Full grow lighting

        # Scenario: Power constraint (grid outage + low solar)
        if not grid_available and self.telemetry.battery_soc_pct < 40.0:
            # Low Battery Safe Mode: Shed Tier 3 (lights dimmed or turned off)
            self.telemetry.is_load_shedding = True
            tier_3 = 0.0
            tier_2 = 800.0  # Eco HVAC
            logger.warning("MICROGRID PRIORITY SHEDDING: Dimming Grow LEDs to safeguard water circulation & controllers!")
        else:
            self.telemetry.is_load_shedding = False

        self.telemetry.tier_1_critical_w = tier_1
        self.telemetry.tier_2_essential_w = tier_2
        self.telemetry.tier_3_curtailable_w = tier_3
        self.telemetry.total_consumption_w = tier_1 + tier_2 + tier_3

        # Net balance
        net = self.telemetry.solar_generation_w - self.telemetry.total_consumption_w
        if net > 0:
            # Charging battery
            self.telemetry.battery_soc_pct = min(100.0, round(self.telemetry.battery_soc_pct + 0.5, 1))
            self.telemetry.grid_power_w = 0.0
        else:
            # Discharging battery or drawing from grid
            if grid_available:
                self.telemetry.grid_power_w = abs(net)
            else:
                self.telemetry.grid_power_w = 0.0
                self.telemetry.battery_soc_pct = max(10.0, round(self.telemetry.battery_soc_pct - 0.8, 1))

        return self.telemetry

energy_manager = AutonomousEnergyManager()
