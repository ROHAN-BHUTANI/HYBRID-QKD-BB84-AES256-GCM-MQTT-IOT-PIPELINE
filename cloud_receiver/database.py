# -*- coding: utf-8 -*-
"""
Database Management Module.
Manages persistent SQLite storage for:
- Authenticated and tampered IoT sensor telemetry
- QKD key agreement sessions and QBER diagnostics
- Security and tamper detection alerts
"""
import os
import sys
import sqlite3
from typing import List, Dict, Any, Optional

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


class DatabaseManager:
    """
    SQLite3 wrapper for IoT telemetry, QKD audit sessions, and security alerts.
    """
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes database schema if tables do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table 1: Sensor Readings
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                reading_id INTEGER,
                sensor_timestamp TEXT,
                temperature_c REAL,
                humidity_percent REAL,
                pressure_hpa REAL,
                status TEXT NOT NULL,
                decryption_latency_ms REAL,
                e2e_latency_ms REAL,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Table 2: QKD Audit Sessions
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS qkd_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_timestamp TEXT NOT NULL,
                num_qubits INTEGER NOT NULL,
                sifted_length INTEGER NOT NULL,
                qber REAL NOT NULL,
                threshold REAL NOT NULL,
                is_valid INTEGER NOT NULL,
                eve_present INTEGER NOT NULL,
                execution_time_ms REAL NOT NULL,
                key_preview TEXT
            )
            """)

            # Table 3: Security & Tamper Alerts
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                alert_type TEXT NOT NULL,
                details TEXT NOT NULL,
                device_id TEXT
            )
            """)
            conn.commit()

    def log_sensor_reading(
        self,
        device_id: str,
        reading_id: Optional[int],
        sensor_timestamp: str,
        temp: Optional[float],
        humidity: Optional[float],
        pressure: Optional[float],
        status: str,
        dec_latency_ms: float,
        e2e_latency_ms: float
    ):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO sensor_readings (
                device_id, reading_id, sensor_timestamp, temperature_c,
                humidity_percent, pressure_hpa, status, decryption_latency_ms, e2e_latency_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                device_id, reading_id, sensor_timestamp, temp,
                humidity, pressure, status, dec_latency_ms, e2e_latency_ms
            ))
            conn.commit()

    def log_qkd_session(
        self,
        timestamp: str,
        num_qubits: int,
        sifted_len: int,
        qber: float,
        threshold: float,
        is_valid: bool,
        eve_present: bool,
        exec_ms: float,
        key_preview: str = ""
    ):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO qkd_sessions (
                session_timestamp, num_qubits, sifted_length, qber,
                threshold, is_valid, eve_present, execution_time_ms, key_preview
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, num_qubits, sifted_len, qber,
                threshold, 1 if is_valid else 0, 1 if eve_present else 0,
                exec_ms, key_preview
            ))
            conn.commit()

    def log_security_alert(self, alert_type: str, details: str, device_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO security_alerts (alert_type, details, device_id)
            VALUES (?, ?, ?)
            """, (alert_type, details, device_id))
            conn.commit()

    def get_recent_readings(self, limit: int = 25) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM sensor_readings ORDER BY id DESC LIMIT ?", (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_latest_qkd_session(self) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM qkd_sessions ORDER BY id DESC LIMIT 1"
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_security_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM security_alerts ORDER BY id DESC LIMIT ?", (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_system_summary(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sensor_readings WHERE status = 'AUTHENTICATED'")
            auth_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM sensor_readings WHERE status != 'AUTHENTICATED'")
            tamper_count = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(decryption_latency_ms), AVG(e2e_latency_ms) FROM sensor_readings WHERE status = 'AUTHENTICATED'")
            avg_dec, avg_e2e = cursor.fetchone()

            cursor.execute("SELECT COUNT(*) FROM qkd_sessions")
            total_qkd = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM qkd_sessions WHERE is_valid = 1")
            valid_qkd = cursor.fetchone()[0]

            return {
                "authenticated_packets": auth_count,
                "tampered_packets": tamper_count,
                "avg_decryption_ms": round(avg_dec or 0.0, 3),
                "avg_e2e_latency_ms": round(avg_e2e or 0.0, 3),
                "total_qkd_sessions": total_qkd,
                "successful_qkd_sessions": valid_qkd
            }

