"""
AURA-Farm Configuration and System Parameters
"""
from pydantic import BaseModel, Field
import os

class SafetyLimitsConfig(BaseModel):
    # Absolute physical maximums to protect plant root systems and actuators
    max_single_dose_ml: float = 120.0
    max_dosing_rate_ml_per_hour: float = 500.0
    min_ph: float = 5.0
    max_ph: float = 7.5
    max_ph_change_rate_per_hour: float = 0.5
    min_ec_ms_cm: float = 0.8
    max_ec_ms_cm: float = 3.5
    max_water_temp_c: float = 26.0
    min_water_temp_c: float = 16.0
    min_dissolved_oxygen_mg_l: float = 5.0
    max_ambient_temp_c: float = 34.0
    min_ambient_temp_c: float = 14.0
    max_humidity_percent: float = 90.0
    min_humidity_percent: float = 40.0
    max_co2_ppm: float = 1800.0
    robot_max_speed_mm_s: float = 500.0
    robot_emergency_stop_enabled: bool = True

class SystemConfig(BaseModel):
    app_name: str = "AURA-Farm OS"
    version: str = "1.0.0"
    environment: str = os.getenv("AURA_ENV", "simulation")
    host: str = os.getenv("AURA_HOST", "0.0.0.0")
    port: int = int(os.getenv("AURA_PORT", "8000"))
    tick_rate_seconds: float = float(os.getenv("AURA_TICK_RATE", "1.5"))
    database_path: str = os.getenv("AURA_DB_PATH", "aura_farm_edge.db")
    jwt_secret_key: str = os.getenv("AURA_SECRET_KEY", "aura-farm-zero-human-autonomous-secret-key-2026")
    default_crop: str = "Butterhead Lettuce"
    safety: SafetyLimitsConfig = Field(default_factory=SafetyLimitsConfig)

config = SystemConfig()
