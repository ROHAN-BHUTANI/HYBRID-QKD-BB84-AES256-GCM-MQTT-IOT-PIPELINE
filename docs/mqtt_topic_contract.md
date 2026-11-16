# MQTT Topic & Message Contract Specification

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Standard:** OASIS MQTT v5.0 / v3.1.1  
**Broker Host:** `localhost` (default) or containerized Mosquitto service on port 1883  
**Date:** November 2026

---

## 1. Topic Taxonomy

The platform adopts a hierarchical topic structure designed for multi-tenant IoT edge deployments:

```
iot/
└── {device_id}/
    ├── encrypted-data       [QoS 1] Encrypted AES-256-GCM telemetry envelopes
    ├── status               [QoS 1] Device health, heartbeat, and connection state
    └── security-events      [QoS 2] Tamper alerts, tag failures, and replay incidents
```

### Standard Default Topics
- **Data Ingestion:** `iot/secure/data` (Default shared topic for prototype sensor telemetry)
- **Status & Heartbeat:** `iot/secure/status`
- **Security Events:** `iot/secure/security-events`

---

## 2. Message Schemas & Payload Contracts

### 2.1 Schema 1: Plaintext Telemetry Payload (Pre-Encryption)
This canonical dictionary is serialized into JSON bytes and fed into `CryptoUtils.encrypt_payload()`:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PlaintextSensorPayload",
  "type": "object",
  "required": ["device_id", "reading_id", "timestamp", "sensor_type", "temperature_c", "humidity_percent", "pressure_hpa"],
  "properties": {
    "device_id": { "type": "string", "example": "IOT-WEATHER-STATION-01" },
    "reading_id": { "type": "integer", "minimum": 1, "example": 42 },
    "timestamp": { "type": "string", "format": "date-time", "example": "2026-11-16T10:45:00.123456Z" },
    "sensor_type": { "type": "string", "example": "BME280_ENVIRONMENTAL" },
    "temperature_c": { "type": "number", "minimum": -40.0, "maximum": 85.0, "example": 23.45 },
    "humidity_percent": { "type": "number", "minimum": 0.0, "maximum": 100.0, "example": 54.20 },
    "pressure_hpa": { "type": "number", "minimum": 300.0, "maximum": 1100.0, "example": 1013.25 }
  }
}
```

### 2.2 Schema 2: Encrypted Transport Envelope (Over the Wire)
This is the actual payload transmitted over MQTT topic `iot/secure/data`. It contains only Base64-encoded ciphertext, nonce, tag, and transmission timing metadata:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EncryptedMqttEnvelope",
  "type": "object",
  "required": ["device_id", "timestamp_ns", "nonce", "ciphertext", "tag", "payload_size_bytes"],
  "properties": {
    "device_id": { "type": "string", "example": "IOT-WEATHER-STATION-01" },
    "timestamp_ns": { "type": "integer", "description": "High-resolution transmission timestamp in nanoseconds", "example": 1793544562000000 },
    "nonce": { "type": "string", "description": "Base64 encoded 96-bit unique IV", "example": "v3JbNq7K19eXm0Pq" },
    "ciphertext": { "type": "string", "description": "Base64 encoded AES-256-GCM ciphertext bytes" },
    "tag": { "type": "string", "description": "Base64 encoded 128-bit authentication tag", "example": "Ab89Zkl74NmQpT1==" },
    "payload_size_bytes": { "type": "integer", "description": "Original plaintext length before encryption", "example": 184 }
  }
}
```

### 2.3 Schema 3: Security Alert Notification
Emitted to `iot/secure/security-events` when an integrity violation, replay attack, or quantum intrusion is detected:
```json
{
  "event_id": "SEC-ALERT-8921",
  "timestamp": "2026-11-16T10:45:00.125Z",
  "alert_type": "INTEGRITY_VIOLATION",
  "severity": "CRITICAL",
  "device_id": "IOT-WEATHER-STATION-01",
  "details": "AES-256-GCM authentication tag mismatch (InvalidTag). Ciphertext modified in transit.",
  "action_taken": "PAYLOAD_DROPPED_AND_QUARANTINED"
}
```

---

## 3. Transport Quality of Service (QoS) & Reliability Policy
- **Telemetry Data (QoS 1 — At least once delivery):** Guarantees delivery via MQTT `PUBACK` packets. Replays caused by network re-transmissions are caught and filtered by the cloud receiver's sequence watermark.
- **Keepalive & Clean Session:** Clients configure a 60-second keepalive timer. Reconnection triggers an automated `CONNACK` check.
- **Queue Mode Distinction:** When `USE_SIMULATED_BROKER = True`, the underlying in-memory queue guarantees thread-safe, zero-packet-loss FIFO message delivery across application threads.
