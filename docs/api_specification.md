# API Specification (REST & Internal Module Contracts)

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Date:** November 2026

---

## 1. Flask Dashboard REST APIs

The web dashboard and external diagnostic scripts interact with the backend via the following HTTP/JSON endpoints:

### 1.1 `GET /api/stats`
Retrieves aggregated telemetry, system operational status, and active key diagnostics.
- **Request:** None
- **Response `200 OK`:**
  ```json
  {
    "active_key_preview": "7a8b9c1d...",
    "latest_qkd": {
      "execution_time_ms": 45.2,
      "is_valid": 1,
      "num_qubits": 512,
      "qber": 0.0,
      "sifted_length": 258,
      "timestamp": "2026-11-16T10:30:00Z"
    },
    "summary": {
      "active_alerts": 1,
      "authenticated_readings": 150,
      "avg_dec_latency_ms": 0.035,
      "avg_e2e_latency_ms": 0.42,
      "tampered_readings": 2,
      "total_readings": 152
    }
  }
  ```

### 1.2 `GET /api/readings`
Fetches a reverse-chronological list of recent decrypted sensor readings.
- **Parameters (Query string):** `limit` (integer, default: 25)
- **Response `200 OK`:** Array of reading objects:
  ```json
  [
    {
      "decryption_latency_ms": 0.032,
      "device_id": "IOT-WEATHER-STATION-01",
      "e2e_latency_ms": 0.38,
      "humidity_percent": 58.4,
      "id": 152,
      "pressure_hpa": 1012.8,
      "reading_id": 152,
      "received_at": "2026-11-16 10:45:00",
      "sensor_timestamp": "2026-11-16T10:44:59.980Z",
      "status": "AUTHENTICATED",
      "temperature_c": 23.2
    }
  ]
  ```

### 1.3 `GET /api/alerts`
Fetches security alerts, tamper incidents, and QBER intrusion logs.
- **Parameters (Query string):** `limit` (integer, default: 20)
- **Response `200 OK`:** Array of alert objects.

### 1.4 `POST /api/run_qkd`
Triggers an on-demand BB84 key agreement session in Qiskit Aer.
- **Request Body (JSON):**
  ```json
  {
    "num_qubits": 512,
    "enable_eve": false,
    "eve_prob": 1.0
  }
  ```
- **Response `200 OK`:** Complete `BB84Result` diagnostics.

### 1.5 `POST /api/send_reading`
Triggers immediate sensor collection, AES-256-GCM encryption, and publication.
- **Request Body (JSON):**
  ```json
  {
    "tamper": false
  }
  ```
- **Response `200 OK`:** Confirmation, encryption time, and packet envelope.

---

## 2. Internal Python Module Interfaces

### 2.1 Module A: `qkd.bb84.BB84Simulator`
```python
def run(
    self,
    num_qubits: int = 512,
    enable_eve: bool = False,
    eve_prob: float = 1.0,
    sample_fraction: float = 0.25,
    threshold: float = 0.11,
    noise_param: float = 0.0
) -> BB84Result:
    """
    Executes quantum circuit simulation across num_qubits, performs sifting,
    evaluates QBER against threshold, executes error reconciliation, and 
    derives a 256-bit AES key via universal hashing.
    """
```

### 2.2 Module B: `iot_client.crypto_utils.CryptoUtils`
```python
@staticmethod
def encrypt_payload(
    aes_key: bytes,
    payload_dict: Dict[str, Any],
    associated_data: Optional[bytes] = None
) -> Tuple[Dict[str, Any], float]:
    """
    Encrypts canonical JSON payload with AES-256-GCM using a unique 96-bit nonce.
    Returns: (envelope_dict, encryption_time_ms)
    Raises: ValueError if len(aes_key) != 32.
    """

@staticmethod
def decrypt_payload(
    aes_key: bytes,
    envelope: Dict[str, Any],
    associated_data: Optional[bytes] = None
) -> Tuple[Dict[str, Any], float]:
    """
    Verifies 128-bit authentication tag and decrypts ciphertext.
    Returns: (decrypted_dict, decryption_time_ms)
    Raises: InvalidTag if authentication verification fails.
    """
```

### 2.3 Module C: `cloud_receiver.receiver.CloudReceiver`
```python
def _on_mqtt_message(self, topic: str, payload_str: str) -> None:
    """
    Triggered upon message arrival. Enforces monotonic sequence checking,
    calls CryptoUtils.decrypt_payload, measures nanosecond E2E latency,
    and updates SQLite.
    """
```
