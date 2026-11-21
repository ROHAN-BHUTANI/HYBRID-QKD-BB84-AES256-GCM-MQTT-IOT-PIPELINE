# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures.
"""
import pytest
import os
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Pre-import AerSimulator to initialize C++ runtime / DLL handles early in process lifecycle
try:
    from qiskit_aer import AerSimulator
except Exception:
    pass

import config
from cloud_receiver.database import DatabaseManager


@pytest.fixture(autouse=True)
def reset_simulated_broker():
    """
    Reset the SimulatedBroker singleton's subscriber table before each test.
    Prevents stale subscriptions from prior tests from receiving messages
    encrypted under a different key and generating spurious tampering alerts.
    """
    from broker.broker_bridge import SimulatedBroker
    SimulatedBroker.reset_for_testing()
    yield
    SimulatedBroker.reset_for_testing()


@pytest.fixture
def test_db(tmp_path):
    """Provides a temporary, isolated SQLite database for testing."""
    temp_db_path = str(tmp_path / "test_iot_cloud.db")
    db = DatabaseManager(db_path=temp_db_path)
    return db


@pytest.fixture
def sample_key():
    """Provides a valid 32-byte (256-bit) test AES key."""
    return os.urandom(32)
