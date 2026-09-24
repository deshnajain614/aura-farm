"""
Autonomous Lighting Subsystem (Prompt Section 9)
================================================
Controls multi-channel horticultural LED fixtures:
- Deep Red (660nm)
- Royal Blue (450nm)
- Far Red (730nm)
- Full Spectrum White (4000K)
Manages Photoperiod, Daily Light Integral (DLI), and ambient dimming.
"""
from typing import Dict, Any
import logging
from aura_farm.core.types import LightingTelemetry

logger = logging.getLogger("aura_farm.lighting")

class LightingSystem:
    def __init__(self):
        self.telemetry = LightingTelemetry()

    def update_photoperiod_and_dli(self, hour_of_day: float, delta_hours: float = 0.5):
        """Calculates accumulated DLI (Daily Light Integral in mol/m²/day)."""
        is_day = hour_of_day < self.telemetry.photoperiod_hours
        self.telemetry.lights_on = is_day

        if self.telemetry.lights_on:
            # DLI = PPFD (umol/m2/s) * 3600 * hours / 1,000,000
            incremental_dli = (self.telemetry.current_ppfd_umol_m2_s * 3600.0 * delta_hours) / 1_000_000.0
            self.telemetry.accumulated_dli = round(self.telemetry.accumulated_dli + incremental_dli, 2)
        else:
            if hour_of_day >= 23.5:
                # Reset daily counter at midnight
                self.telemetry.accumulated_dli = 0.0

    def set_spectrum_recipe(self, red: float, blue: float, white: float):
        """Dynamically tunes light spectrum ratios for vegetative vs fruiting states."""
        self.telemetry.spectrum_deep_red_pct = red
        self.telemetry.spectrum_royal_blue_pct = blue
        self.telemetry.spectrum_white_pct = white
        logger.info(f"Lighting Spectrum Updated: Red {red}% | Blue {blue}% | White {white}%")

    def dim_for_energy_saving(self, scale_factor: float):
        """Dims lights during peak grid tariff or battery power preservation."""
        self.telemetry.current_ppfd_umol_m2_s = round(240.0 * scale_factor, 1)

lighting_system = LightingSystem()
