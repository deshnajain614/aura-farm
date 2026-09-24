"""
Tests for Section 24: Internet Failure Handling and Local Edge Storage
"""
import pytest
import os
from aura_farm.subsystems.edge_autonomy import EdgeAutonomyEngine

def test_offline_edge_event_buffering_and_resync(tmp_path):
    test_db = str(tmp_path / "test_edge.db")
    edge = EdgeAutonomyEngine(test_db)

    # 1. Simulate Cloud Drop
    edge.set_connectivity(False)
    assert not edge.sync_state.is_online

    # 2. Log events while offline
    edge.log_edge_event("ROBOT_HARVEST", {"batch": "BATCH-1", "weight_kg": 24.5})
    edge.log_edge_event("CIP_FLUSH", {"zone": "GROWTH_ZONE"})

    assert edge.sync_state.offline_event_count == 2

    # 3. Simulate Cloud Restoration
    edge.set_connectivity(True)
    assert edge.sync_state.is_online
    assert edge.sync_state.offline_event_count == 0
