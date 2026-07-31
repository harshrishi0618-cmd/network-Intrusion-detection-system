# AI-NIDS — AI-Powered Network Intrusion Detection System

A real-time network intrusion detection system that combines two trained ML models (CIC IDS 2017 and UNSW-NB15) with anomaly detection to classify live network traffic and optionally block attacking IPs via the Windows Firewall.

## Architecture

```
Live Traffic (Scapy)
      │
      ▼
Flow Tracker  ──→  Feature Extraction (78 CIC IDS features per flow)
      │
      ▼
Fusion Engine
  ├─ CIC RF + IsolationForest
  └─ UNSW RF + IsolationForest
      │
      ▼
Decision: ALLOW / UNKNOWN_ATTACK / KNOWN_ATTACK
      │
      ▼
Alert Manager  ──→  SQLite DB  ──→  Streamlit Dashboard
      │
      ▼ (if no ACK within 30s)
Prevention Engine (Windows Firewall block)
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> Scapy on Windows also requires [Npcap](https://npcap.com/) to be installed.

### 2. Train the models (if not already trained)

```bash
# Preprocess datasets
python feature_engineering/preprocess_data.py
python feature_engineering/preprocess_unsw.py

# Train classifiers
python models/ml/train_rf.py
python models/ml/train_rf_unsw.py

# Train anomaly detectors
python models/anomaly/train_isolation_forest.py
python models/anomaly/train_isolation_forest_unsw.py
```

## Running

All commands must be run as **Administrator** (Scapy needs raw socket access).

### Start the monitor

```bash
python main.py
```

### Monitor a specific interface

```bash
python main.py --iface "Ethernet"
python main.py --iface "Wi-Fi"
```

### Launch the dashboard (separate terminal)

```bash
python main.py --dashboard
# or directly:
streamlit run dashboard/app.py
```

## Decision Logic

| Condition | Decision | Severity |
|-----------|----------|----------|
| RF confidence > 80%, label ≠ BENIGN (CIC model) | KNOWN_ATTACK | HIGH |
| RF confidence > 80%, label ≠ Normal (UNSW model) | KNOWN_ATTACK | HIGH |
| Anomaly score ≥ threshold (either model) | UNKNOWN_ATTACK | MEDIUM |
| Otherwise | ALLOW | LOW |

- **HIGH / MEDIUM** alerts wait 30 seconds for human acknowledgement before auto-escalating to firewall blocking.
- **LOW** alerts are logged only.

## Project Structure

```
ai-nids/
├── main.py                        # Entry point
├── requirements.txt
├── dashboard/app.py               # Streamlit UI
├── decision_engine/
│   ├── fusion_engine.py           # Dual-model ensemble detection
│   └── alert_manager.py          # Alert logging & escalation
├── feature_engineering/
│   ├── feature_mapper.py          # CIC → UNSW feature mapping
│   ├── preprocess_data.py         # CIC IDS 2017 preprocessing
│   └── preprocess_unsw.py        # UNSW-NB15 preprocessing
├── live_capture/live_monitor.py   # Scapy packet capture & flow tracking
├── logs/logger.py                 # SQLite alert persistence
├── models/
│   ├── ml/                        # RandomForest models
│   └── anomaly/                   # IsolationForest models
└── prevention_engine/
    └── prevent_attack.py          # Windows Firewall blocking
```

## Datasets

- [CIC IDS 2017](https://www.unb.ca/cic/datasets/ids-2017.html) — placed in `data/raw/CICIDS2017/`
- [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset) — placed in `data/raw/UNSW-NB15/`
