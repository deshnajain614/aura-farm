"""
Autonomous Climate Control Subsystem (Prompt Section 8)
======================================================
Regulates HVAC (heating/cooling), Variable Speed Fans, Exhaust Louvers,
Ultrasonic Humidifiers, Desiccant Dehumidifiers, and CO2 enrichment.
Computes and regulates Vapor Pressure Deficit (VPD).
"""
import math
import random
import time
import logging
from aura_farm.core.types import ClimateTelemetry

logger = logging.getLogger("aura_farm.climate")

class ClimateControlSystem:
    def __init__(self):
        self.telemetry = ClimateTelemetry()
        self.hvac_cooling_active: bool = False
        self.hvac_heating_active: bool = False
        self.exhaust_open: bool = False
        self.co2_solenoid_open: bool = False

    def calculate_vpd(self, air_temp_c: float, rh_pct: float, leaf_temp_offset_c: float = -1.5) -> float:
        """
        Calculates Vapor Pressure Deficit in kPa.
        VPD = Saturation Vapor Pressure (VPsat) - Actual Vapor Pressure (VPair)
        """
        leaf_temp = air_temp_c + leaf_temp_offset_c
        vp_sat = 0.61078 * math.exp((17.27 * leaf_temp) / (leaf_temp + 237.3))
        vp_air = (rh_pct / 100.0) * (0.61078 * math.exp((17.27 * air_temp_c) / (air_temp_c + 237.3)))
        vpd = max(0.1, vp_sat - vp_air)
        return round(vpd, 2)

    def read_sensors(self) -> ClimateTelemetry:
        """Reads air temperature, humidity, VPD, and CO2 sensors."""
        # Simulated gentle ambient fluctuation
        self.telemetry.air_temp_c = round(self.telemetry.air_temp_c + random.uniform(-0.15, 0.15), 1)
        self.telemetry.relative_humidity_pct = round(max(45.0, min(85.0, self.telemetry.relative_humidity_pct + random.uniform(-0.5, 0.5))), 1)
        self.telemetry.vpd_kpa = self.calculate_vpd(self.telemetry.air_temp_c, self.telemetry.relative_humidity_pct)
        self.telemetry.co2_ppm = round(max(400.0, min(1600.0, self.telemetry.co2_ppm + random.uniform(-10.0, 10.0))), 0)
        self.telemetry.timestamp = time.time()
        return self.telemetry

    def adjust_climate(self, target_temp: float, target_humidity: float, fans_pct: float = 65.0):
        """Applies HVAC and dehumidifier actuator changes."""
        if self.telemetry.air_temp_c > target_temp + 0.8:
            self.hvac_cooling_active = True
            self.hvac_heating_active = False
            self.telemetry.hvac_status = "HVAC_COOLING"
            self.telemetry.air_temp_c -= 0.3
        elif self.telemetry.air_temp_c < target_temp - 0.8:
            self.hvac_cooling_active = False
            self.hvac_heating_active = True
            self.telemetry.hvac_status = "HVAC_HEATING"
            self.telemetry.air_temp_c += 0.3
        else:
            self.hvac_cooling_active = False
            self.hvac_heating_active = False
            self.telemetry.hvac_status = "HVAC_STABLE_ECO"

        if self.telemetry.relative_humidity_pct > target_humidity + 4.0:
            self.telemetry.dehumidifier_active = True
            self.telemetry.humidifier_active = False
            self.telemetry.relative_humidity_pct -= 0.8
        elif self.telemetry.relative_humidity_pct < target_humidity - 4.0:
            self.telemetry.dehumidifier_active = False
            self.telemetry.humidifier_active = True
            self.telemetry.relative_humidity_pct += 0.8
        else:
            self.telemetry.dehumidifier_active = False
            self.telemetry.humidifier_active = False

        self.telemetry.fans_pct = fans_pct
        self.telemetry.vpd_kpa = self.calculate_vpd(self.telemetry.air_temp_c, self.telemetry.relative_humidity_pct)

    def inject_co2(self, target_ppm: float = 1000.0):
        """Opens solenoid to enrich canopy with CO2 for enhanced photosynthesis."""
        self.co2_solenoid_open = True
        self.telemetry.co2_ppm = min(target_ppm, self.telemetry.co2_ppm + 85.0)
        logger.info(f"CO2 Injector: Solenoid open -> Chamber enriched to {self.telemetry.co2_ppm:.0f} ppm.")
        self.co2_solenoid_open = False

climate_control = ClimateControlSystem()
