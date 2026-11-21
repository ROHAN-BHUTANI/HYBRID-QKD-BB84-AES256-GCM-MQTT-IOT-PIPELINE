# -*- coding: utf-8 -*-
"""
Database Management Module.
Manages persistent SQLite storage for:
- Authenticated and tampered IoT sensor telemetry
- QKD key agreement sessions and QBER diagnostics
- Security, tamper detection, and replay alerts
- Device state and monotonic sequence tracking
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
    SQLite3 wrapper for IoT telemetry, QKD audit sessions, device sequence tracking, and security alerts.
    """
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        """Initializes database schema with constraints, indexes, and migrations."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table 1: Sensor Devices (Tracks monotonic sequence watermark for anti-replay)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_devices (
                device_id TEXT PRIMARY KEY,
                device_name TEXT NOT NULL,
                sensor_model TEXT DEFAULT 'BME280',
                location TEXT DEFAULT 'Field Node 01',
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_sequence_id INTEGER DEFAULT 0
            )
            """)

            # Table 2: Sensor Readings
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
                decryption_latency_ms REAL NOT NULL DEFAULT 0.0,
                e2e_latency_ms REAL NOT NULL DEFAULT 0.0,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_readings_device_status ON sensor_readings(device_id, status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_readings_received ON sensor_readings(received_at)")

            # Table 3: QKD Audit Sessions
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS qkd_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_timestamp TEXT NOT NULL,
                num_qubits INTEGER NOT NULL,
                sifted_length INTEGER NOT NULL,
                qber REAL NOT NULL,
                threshold REAL NOT NULL DEFAULT 0.11,
                is_valid INTEGER NOT NULL CHECK (is_valid IN (0, 1)),
                eve_present INTEGER NOT NULL CHECK (eve_present IN (0, 1)),
                execution_time_ms REAL NOT NULL,
                key_preview TEXT
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_qkd_timestamp ON qkd_sessions(session_timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_qkd_valid ON qkd_sessions(is_valid)")

            # Table 4: Security & Tamper Alerts
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                alert_type TEXT NOT NULL,
                details TEXT NOT NULL,
                device_id TEXT
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON security_alerts(alert_timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_type ON security_alerts(alert_type)")

            # Table 5: Key Lifecycle Events
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS key_lifecycle_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                state TEXT,
                key_id TEXT,
                old_key_id TEXT,
                new_key_id TEXT,
                invocation_count INTEGER,
                threshold INTEGER,
                qber REAL,
                pa_output_bits INTEGER,
                reconciled_bits INTEGER,
                duration_ms REAL,
                reason TEXT,
                details_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_lifecycle_event_type ON key_lifecycle_events(event_type)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_lifecycle_key_id ON key_lifecycle_events(key_id)"
            )

            # --- Migration Check for columns ---
            cursor.execute("PRAGMA table_info(security_alerts)")
            alert_cols = [col["name"] for col in cursor.fetchall()]
            if "severity" not in alert_cols:
                cursor.execute("ALTER TABLE security_alerts ADD COLUMN severity TEXT DEFAULT 'CRITICAL'")

            # Migration: add key_id column to sensor_readings if absent
            cursor.execute("PRAGMA table_info(sensor_readings)")
            reading_cols = [col["name"] for col in cursor.fetchall()]
            if "key_id" not in reading_cols:
                cursor.execute("ALTER TABLE sensor_readings ADD COLUMN key_id TEXT DEFAULT NULL")

            conn.commit()

    def get_device_sequence(self, device_id: str) -> int:
        """Retrieves the highest observed sequence ID for a device."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_sequence_id FROM sensor_devices WHERE device_id = ?", (device_id,))
            row = cursor.fetchone()
            if row:
                return row["last_sequence_id"]
            cursor.execute(
                "INSERT INTO sensor_devices (device_id, device_name, last_sequence_id) VALUES (?, ?, 0)",
                (device_id, f"Node-{device_id}")
            )
            conn.commit()
            return 0

    def update_device_sequence(self, device_id: str, sequence_id: int):
        """Updates the highest sequence ID watermark for a device."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO sensor_devices (device_id, device_name, last_sequence_id)
            VALUES (?, ?, ?)
            ON CONFLICT(device_id) DO UPDATE SET last_sequence_id = MAX(last_sequence_id, excluded.last_sequence_id)
            """, (device_id, f"Node-{device_id}", sequence_id))
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
        e2e_latency_ms: float,
        key_id: Optional[str] = None,
    ):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO sensor_readings (
                device_id, reading_id, sensor_timestamp, temperature_c,
                humidity_percent, pressure_hpa, status, decryption_latency_ms, e2e_latency_ms, key_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                device_id, reading_id, sensor_timestamp, temp,
                humidity, pressure, status, dec_latency_ms, e2e_latency_ms, key_id
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

    def log_key_lifecycle_event(self, event: dict):
        """
        Persist a structured key lifecycle event to the database.
        Never stores raw key material — only metadata and identifiers.
        """
        import json as _json
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO key_lifecycle_events (
                event_timestamp, event_type, state, key_id, old_key_id, new_key_id,
                invocation_count, threshold, qber, pa_output_bits, reconciled_bits,
                duration_ms, reason, details_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.get("timestamp_utc"),
                event.get("event_type"),
                event.get("state"),
                event.get("key_id"),
                event.get("old_key_id"),
                event.get("new_key_id"),
                event.get("invocation_count"),
                event.get("threshold"),
                event.get("qber"),
                event.get("pa_output_bits"),
                event.get("reconciled_bits"),
                event.get("duration_ms"),
                event.get("reason"),
                _json.dumps({k: v for k, v in event.items()
                             if k not in ("timestamp_utc", "event_type", "state")}),
            ))
            conn.commit()

    def get_lifecycle_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent key lifecycle events ordered newest-first."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM key_lifecycle_events ORDER BY id DESC LIMIT ?", (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def log_security_alert(self, alert_type: str, details: str, device_id: str, severity: str = "CRITICAL"):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO security_alerts (alert_type, details, device_id, severity)
            VALUES (?, ?, ?, ?)
            """, (alert_type, details, device_id, severity))
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
