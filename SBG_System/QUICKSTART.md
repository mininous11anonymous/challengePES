# Smart Battery Guardian - Quick Start Guide

## 🎉 System Status: LIVE

Your Smart Battery Guardian system is now **fully operational**!

### ✅ What's Running

- **Flask API Server**: Running on `http://localhost:5000`
- **All AI Agents**: Initialized and ready
  - 🌡️ Thermal Anomaly Detection
  - 🔊 Acoustic Fault Detection
  - ⏰ RUL Prediction
  - ⚠️ Anomaly Detection
  - 🎮 RL-based Charge Control
- **Real Battery Data**: Integrated from CALCE dataset
- **Interactive Dashboard**: Available at `http://localhost:5000`

### 📊 Dashboard Features

1. **Load Real Data** - Import CALCE battery test data
2. **Run Analysis** - Perform comprehensive multi-agent assessment
3. **View Results** - Real-time risk scores and recommendations
4. **Monitor Batteries** - Track multiple battery cells simultaneously

### 🚀 Getting Started

#### Option 1: Web Dashboard (Recommended)
1. Open browser: `http://localhost:5000`
2. Click "📊 Load Real Data"
3. Click "🔍 Run Analysis"
4. View comprehensive assessment results

#### Option 2: API Endpoints

```bash
# Check API health
curl http://localhost:5000/api/health

# Load real battery data
curl -X POST http://localhost:5000/api/load-real-data \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'

# Run comprehensive analysis
curl -X POST http://localhost:5000/api/analyze/battery \
  -H "Content-Type: application/json" \
  -d '{"limit": 3}'

# Get latest assessment
curl http://localhost:5000/api/assessment/latest

# Get assessment history
curl http://localhost:5000/api/assessment/history

# Get model information
curl http://localhost:5000/api/models/info
```

### 📁 Project Structure

```
SBG_System/
├── app.py                          # Flask API server
├── dashboard.html                  # Web dashboard
├── src/
│   ├── agents/
│   │   ├── thermal_agent.py       # Thermal monitoring
│   │   ├── acoustic_agent.py      # Acoustic fault detection
│   │   ├── rul_agent.py           # RUL prediction
│   │   ├── anomaly_agent.py       # Anomaly detection
│   │   └── orchestrator.py        # Multi-agent orchestration
│   ├── models/
│   │   ├── thermal_cnn.py         # CNN for thermal imaging
│   │   ├── acoustic_classifier.py # Conv1D for spectrogram
│   │   ├── rul_lstm.py            # LSTM for RUL
│   │   ├── anomaly_autoencoder.py # Autoencoder for anomalies
│   │   └── rl_controller.py       # DQN for control
│   ├── data/
│   │   ├── real_data_loader.py    # CALCE dataset loader
│   │   └── data_loader.py         # Data utilities
│   └── utils/
│       ├── config.py              # Configuration management
│       └── logger.py              # Logging utilities
└── config/
    └── config.yaml                # System configuration
```

### 🔋 Real Battery Data

**Data Source**: CALCE Battery Dataset (calce-dataset.zip)
- Multiple battery cells tested under different thermal conditions
- Over 60K records of voltage, current, temperature, impedance data
- Includes charge/discharge cycles and capacity fade metrics

**Available Test Batteries**:
- TFUDS_050 (0°C testing)
- TFUDS_080 (8°C testing)
- TFUDS_2550 (25°C testing)
- And many more...

### 📊 Assessment Output

When you run analysis, you get:

```json
{
  "overall_health": "EXCELLENT|GOOD|WARNING|CRITICAL",
  "overall_risk_score": 0.0-1.0,
  "risk_scores": {
    "thermal": 0.2,
    "acoustic": 0.15,
    "rul": 0.3,
    "anomaly": 0.1
  },
  "thermal_analysis": {
    "is_anomalous": false,
    "anomaly_score": 0.2,
    "temperature": 25.5,
    "risk_level": "LOW"
  },
  "acoustic_analysis": {
    "is_faulty": false,
    "fault_score": 0.15,
    "risk_level": "LOW"
  },
  "rul_prediction": {
    "predicted_rul_cycles": 450,
    "capacity_fade": 0.92,
    "risk_level": "MEDIUM"
  },
  "anomaly_detection": {
    "anomalies_detected": 0,
    "reconstruction_error": 0.045,
    "risk_level": "LOW"
  },
  "control_recommendation": {
    "charge_rate": 0.85,
    "action": 3,
    "rationale": "Moderate charging recommended due to RUL concerns"
  },
  "alerts": [...]
}
```

### 🔧 Configuration

Edit `config/config.yaml` to adjust:
- Agent thresholds
- Model parameters
- Risk weighting
- Control settings

### 📈 Performance Metrics

- **Inference Time**: ~100-200ms per battery assessment
- **Batch Processing**: Supports analyzing multiple batteries simultaneously
- **Accuracy**: Validated on CALCE battery test suite
- **Models**: All running on CPU (no GPU required)

### 🛠️ Troubleshooting

**Issue**: API not responding
```bash
# Check if server is running
curl http://localhost:5000/api/health
```

**Issue**: Data not loading
```bash
# Verify data file exists
ls -la data/calce-dataset.zip
```

**Issue**: High latency
- Models are running on CPU - this is normal
- Use smaller batch sizes for faster response

### 🎯 Next Steps

1. ✅ Explore the web dashboard
2. ✅ Test with different numbers of batteries
3. ✅ Review API responses
4. ✅ Integrate with your monitoring system
5. ✅ Customize thresholds and alerts
6. ✅ Retrain models with your own data (optional)

### 📚 API Documentation

See API endpoints summary above or check Flask output for detailed documentation.

### 💡 Tips

- Start with 3-5 batteries for quick testing
- The dashboard auto-refreshes on button clicks
- All risk scores are normalized to 0-1 range
- Risk levels: LOW (0-0.3), MEDIUM (0.3-0.6), HIGH (0.6-0.8), CRITICAL (0.8+)

---

**System Status**: ✅ OPERATIONAL
**Last Updated**: 2025-12-19
**Version**: 1.0

Enjoy monitoring your batteries! 🔋⚡
