# System Architecture Document (SAD)

**Project Title:** Hybrid BB84 Quantum Key Distribution and AES-256 Encryption for Secure Cloud-Based IoT Communication  
**Document Version:** 1.0.0  
**Date:** November 2026

---

## 1. System Overview & Context Diagram (C4 Level 1)

The system context diagram illustrates the interaction between external actors and the major logical domains of the platform:

```mermaid
graph TD
    classDef actorStyle fill:#D4AF37,stroke:#8B6508,stroke-width:2px,color:#000000;
    classDef systemStyle fill:#1A1A1A,stroke:#D4AF37,stroke-width:2px,color:#FFFFFF;
    classDef extStyle fill:#2A2A2A,stroke:#666666,stroke-width:1px,color:#DDDDDD;

    User["Researcher / Systems Evaluator"]:::actorStyle
    Attacker["Quantum / Classical Adversary (Eve / MitM)"]:::actorStyle

    subgraph CorePlatform ["Hybrid Quantum-Safe IoT Security Platform"]
        QKDModule["Module A: Qiskit BB84 Simulator & Post-Processing"]:::systemStyle
        IoTEdge["Module B: IoT Edge Sensor & AES-256-GCM Client"]:::systemStyle
        MQTTBroker["Module C: MQTT Broker Bridge (Queue / Mosquitto)"]:::systemStyle
        CloudReceiver["Module D: Cloud Decryption & Anti-Replay Ingestion"]:::systemStyle
        Storage["Module E: SQLite Persistent Audit Storage"]:::systemStyle
        Dashboard["Module F: Real-time Golden-Black Web Dashboard"]:::systemStyle
    end

    User -->|Triggers BB84 & Experiments| Dashboard
    User -->|Views Live KPIs & Telemetry| Dashboard
    Attacker -.->|Intercepts Qubits (QBER ~25%)| QKDModule
    Attacker -.->|Modifies Ciphertext / Replays| MQTTBroker

    QKDModule -->|Shared 256-bit Key| IoTEdge
    QKDModule -->|Shared 256-bit Key| CloudReceiver
    IoTEdge -->|Publishes Encrypted Envelopes| MQTTBroker
    MQTTBroker -->|Dispatches Messages| CloudReceiver
    CloudReceiver -->|Persists Verified Data & Alerts| Storage
    Storage -->|Queries Stats & Readings| Dashboard
```

---

## 2. Level 1 Data Flow Diagram (DFD)

The Level 1 DFD decomposes the system into primary computational processes and data stores:

```mermaid
graph LR
    classDef procStyle fill:#1A1A1A,stroke:#D4AF37,stroke-width:2px,color:#FFFFFF;
    classDef storeStyle fill:#000000,stroke:#8B6508,stroke-width:2px,color:#D4AF37;
    classDef entStyle fill:#222222,stroke:#555555,stroke-width:1px,color:#FFFFFF;

    Alice["Alice (Transmitter)"]:::entStyle
    Bob["Bob (Receiver)"]:::entStyle
    Sensor["BME280 Sensor Client"]:::entStyle
    Cloud["Cloud Telemetry Service"]:::entStyle

    P1["1.0 Quantum State Simulation (Qiskit Aer)"]:::procStyle
    P2["2.0 Sifting, Reconciliation & Privacy Amplification"]:::procStyle
    P3["3.0 AES-256-GCM Envelope Encryption"]:::procStyle
    P4["4.0 MQTT Publish / Subscribe Dispatch"]:::procStyle
    P5["5.0 GMAC Verification & Anti-Replay Ingestion"]:::procStyle

    D1[("DS1: QKD Sessions Store")]:::storeStyle
    D2[("DS2: Active Keys Buffer")]:::storeStyle
    D3[("DS3: Telemetry & Alerts Store")]:::storeStyle

    Alice -->|Quantum States (Z, X)| P1
    P1 -->|Measurement Counts| Bob
    P1 -->|Raw Sifted Bits| P2
    P2 -->|Session Diagnostics| D1
    P2 -->|256-Bit Secret Key| D2
    
    D2 -->|Active Key| P3
    Sensor -->|Raw Telemetry Dict| P3
    P3 -->|Encrypted JSON Envelope| P4
    P4 -->|MQTT Topic Dispatch| P5
    D2 -->|Active Key| P5
    P5 -->|Verified Readings & Tamper Alerts| D3
    D3 -->|Historical Data| Cloud
```

---

## 3. Level 2 Data Flow Diagram (DFD: QKD Post-Processing)

```mermaid
graph TD
    classDef procStyle fill:#1A1A1A,stroke:#D4AF37,stroke-width:2px,color:#FFFFFF;
    classDef decStyle fill:#332200,stroke:#D4AF37,stroke-width:2px,color:#FFD700;

    InBits["Alice & Bob Raw Measurements"] --> P21["2.1 Basis Matching Comparison"]
    P21 --> Sifted["Sifted Key (~50% of N)"]
    Sifted --> P22["2.2 Random 25% Subsampling"]
    P22 --> P23["2.3 Calculate QBER"]
    
    P23 --> Check{"QBER <= 11.0%?"}:::decStyle
    Check -->|No| Abort["Abort Key Agreement; Trigger Intrusion Alert"]
    Check -->|Yes| P24["2.4 Discard Sampled Bits"]
    
    P24 --> Remaining["Remaining Discrepant Bits"]
    Remaining --> P25["2.5 Information Reconciliation (Cascade/Parity Search)"]
    P25 --> Reconciled["Identical Reconciled Bitstring"]
    Reconciled --> P26["2.6 Universal-Hash Privacy Amplification"]
    P26 --> FinalKey["Final Shared 256-Bit AES Key"]
```

---

## 4. Use Case Diagram

```mermaid
graph TD
    classDef userActor fill:#D4AF37,stroke:#8B6508,stroke-width:2px,color:#000000;
    classDef ucStyle fill:#1E1E1E,stroke:#D4AF37,stroke-width:1px,color:#FFFFFF;

    Researcher["Security Researcher"]:::userActor
    SysAdmin["System Operator"]:::userActor

    subgraph UseCases ["Platform Core Capabilities"]
        UC1(["UC-01: Run Clean BB84 Simulation"]):::ucStyle
        UC2(["UC-02: Run BB84 under Eve Interception"]):::ucStyle
        UC3(["UC-03: Transmit Authenticated Telemetry"]):::ucStyle
        UC4(["UC-04: Inject MitM Tampered Packet"]):::ucStyle
        UC5(["UC-05: Execute Parameter Sweeps & Benchmarks"]):::ucStyle
        UC6(["UC-06: Inspect Live Audit Logs & KPIs"]):::ucStyle
        UC7(["UC-07: Export Experimental CSV Datasets"]):::ucStyle
    end

    Researcher --> UC1
    Researcher --> UC2
    Researcher --> UC3
    Researcher --> UC4
    Researcher --> UC5
    SysAdmin --> UC6
    SysAdmin --> UC7
```

---

## 5. Sequence Diagrams

### 5.1 Sequence 1: End-to-End Clean Quantum Key Agreement & Post-Processing
```mermaid
sequenceDiagram
    autonumber
    participant Alice as Alice (Qiskit Engine)
    participant Channel as Quantum Channel (Aer)
    participant Bob as Bob (Qiskit Engine)
    participant KDF as Post-Processing Engine
    participant DB as SQLite DB

    Alice->>Alice: Generate N random bits & bases (Z/X)
    Alice->>Channel: Transmit single-photon circuits
    Bob->>Bob: Generate random measurement bases (Z/X)
    Channel->>Bob: Measure qubits in chosen bases
    Alice->>Bob: Public basis announcement (Classical Channel)
    Bob->>Alice: Confirm matching basis positions
    Note over Alice,Bob: Basis Sifting (~50% yield)
    Alice->>Bob: Disclose 25% random sample bits
    Bob->>Bob: Calculate QBER = errors / sample_size
    Bob->>Alice: Confirm QBER <= 11% threshold
    Alice->>Bob: Discard sampled verification bits
    Alice->>Bob: Interactive Information Reconciliation (Parity checks)
    Note over Alice,Bob: Reconciled bitstrings now identical
    Alice->>KDF: Universal Hashing / Privacy Amplification
    Bob->>KDF: Universal Hashing / Privacy Amplification
    KDF-->>Alice: 256-bit AES Secret Key
    KDF-->>Bob: 256-bit AES Secret Key
    Alice->>DB: Log QKD session diagnostics (QBER, timing)
```

### 5.2 Sequence 2: IoT Telemetry Ingestion, Anti-Replay, and Tamper Detection
```mermaid
sequenceDiagram
    autonumber
    participant Sensor as IoT Edge Sensor
    participant Crypto as AES-GCM Encryptor
    participant Broker as MQTT Broker Bridge
    participant Cloud as Cloud Receiver
    participant DB as SQLite Database

    Sensor->>Sensor: Sample BME280 (Temp, Humidity, Pressure)
    Sensor->>Sensor: Increment sequence counter (reading_id)
    Sensor->>Crypto: encrypt_payload(AES_Key, Payload_Dict)
    Crypto->>Crypto: Generate unique 96-bit nonce
    Crypto->>Crypto: Compute AES-256-GCM ciphertext + 128-bit tag
    Crypto-->>Sensor: Base64 JSON Envelope
    Sensor->>Broker: MQTT Publish (topic: iot/secure/data)
    Broker->>Cloud: Dispatch MQTT message
    Cloud->>Cloud: Validate reading_id against RFC 64-packet sliding window bitmap (Anti-Replay)
    alt Payload is Valid and Untampered
        Cloud->>Cloud: decrypt_and_verify(AES_Key, Envelope)
        Note over Cloud: GMAC Tag Matches (Authentication Valid)
        Cloud->>DB: INSERT INTO sensor_readings (status='AUTHENTICATED')
        Cloud->>Cloud: Compute E2E Latency (ns -> ms)
    else Payload or Tag Modified in Transit (MitM Attack)
        Cloud->>Cloud: decrypt_and_verify(AES_Key, Tampered_Envelope)
        Note over Cloud: GMAC Tag Mismatch -> raises InvalidTag!
        Cloud->>DB: INSERT INTO security_alerts (type='INTEGRITY_VIOLATION')
        Cloud->>DB: INSERT INTO sensor_readings (status='TAMPERED')
    end
```
