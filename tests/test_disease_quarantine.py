"""
Tests for Sections 13 & 14: Disease & Pest Response and Autonomous Quarantine
"""
import pytest
from aura_farm.subsystems.disease_pest_response import DiseaseAndPestManager
from aura_farm.core.types import PlantInstance, FarmZone, PlantHealthGrade, WaterTelemetry, ClimateTelemetry

def test_disease_high_risk_triggers_quarantine_isolation():
    manager = DiseaseAndPestManager()

    plant = PlantInstance(
        plant_id="TEST-PLANT-99",
        batch_id="TEST-BATCH",
        crop_name="Butterhead Lettuce",
        zone=FarmZone.GROWTH,
        has_disease=True,
        disease_type="Powdery Mildew"
    )

    # Adverse environmental conditions that accelerate fungal pathogen transmission:
    # High RH (85%) + Warm Water (24.5°C)
    water = WaterTelemetry(water_temp_c=24.5)
    climate = ClimateTelemetry(relative_humidity_pct=85.0)

    incident = manager.evaluate_and_respond(plant, water, climate)

    assert incident is not None
    assert incident.risk_level == "HIGH"
    # Robotic arm transferred plant to Quarantine Zone
    assert plant.zone == FarmZone.QUARANTINE
    assert plant.health == PlantHealthGrade.DISEASED
    assert manager.quarantine_zone_count == 1
