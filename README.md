# Smart Grid Load-Balancer with Agentic AI

A decentralized grid management system that balances energy load to prevent blackouts using multi-agent AI with LangGraph, LangChain, and Groq API.

## 🌐 Overview

This project implements an **agentic AI system** for managing electric grids with volatile renewable energy and EV charging spikes. It uses two specialized AI agents working in concert:

1. **Demand Response Agent** - Communicates with smart thermostats to lower load during peak stress
2. **Storage Trigger Agent** - Discharges industrial battery reserves when spot prices are low or grid frequency dips

## 🏗️ Architecture

### Core Components

```
SmartGridManager (Orchestrator)
├── DemandResponseAgent (LangGraph-based)
│   ├── Grid State Analysis
│   ├── Device Identification
│   ├── Action Generation
│   ├── Optimization
│   └── Validation
│
└── StorageTriggerAgent (LangGraph-based)
    ├── Grid Condition Assessment
    ├── Price Signal Analysis
    ├── Frequency Health Evaluation
    ├── Decision Making
    └── Action Generation
```

### Key Models

- **GridState**: Real-time grid conditions (demand, generation, frequency, renewable %)
- **SmartThermostat**: Connected device with load reduction capacity and flexibility score
- **DemandResponseAction**: Specific commands to thermostats
- **StorageTriggerAction**: Battery discharge/charge decisions

## 🚀 Features

### Demand Response Agent
- Analyzes grid stress levels in real-time
- Identifies responsive thermostats by flexibility score
- Generates prioritized actions for temperature adjustment
- Optimizes for maximum load reduction with minimum user discomfort
- Validates all actions before execution

### Storage Trigger Agent
- Monitors grid frequency for stability
- Evaluates spot electricity prices
- Makes autonomous discharge/charge decisions
- Triggers battery storage when:
  - Grid frequency drops below threshold (59.5 Hz)
  - Spot prices are low (<$30/MWh)
  - Demand exceeds generation significantly

### Grid Manager
- Orchestrates both agents
- Manages 1000+ thermostat devices
- Tracks action history
- Provides real-time grid summary
- Executes decisions across device network

## 📋 Installation

### Prerequisites
- Python 3.9+
- Groq API key (free tier available at https://console.groq.com)

### Setup

1. **Clone/Navigate to project directory**
   ```bash
   cd smartGridLoadBalancer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

5. **Get Groq API Key**
   - Go to https://console.groq.com
   - Sign up/login
   - Create API key in Settings
   - Copy to your `.env` file

## 🎯 Usage

### Basic Usage

```python
from grid_manager import SmartGridManager
from models import GridState, SmartThermostat, GridStatus, ThermostatMode
from datetime import datetime

# Initialize manager
manager = SmartGridManager()

# Register thermostats
thermostat = SmartThermostat(
    device_id="THERMO_001",
    location="Office Building A",
    current_temperature=22.5,
    target_temperature=22.0,
    mode=ThermostatMode.COOLING,
    max_reduction_capacity=0.15,  # MW
    flexibility_score=0.85,
)
manager.register_thermostat(thermostat)

# Create grid state
grid_state = GridState(
    timestamp=datetime.now(),
    total_demand_mw=920.0,
    total_generation_mw=850.0,
    grid_frequency_hz=59.8,
    status=GridStatus.WARNING,
    renewable_generation_pct=35,
    storage_available_mw=120.0,
    storage_capacity_mw=200.0,
    peak_load_threshold_mw=1100.0,
)

# Make grid decision
spot_price = 95.0  # $/MWh
decision = manager.make_grid_decision(grid_state, spot_price)

# Execute decision
results = manager.execute_decision(decision)

# Check results
print(f"DR Actions Sent: {results['dr_actions_sent']}")
print(f"Storage Action: {decision.storage_action}")
```

### Running Demonstrations

```bash
python main.py
```

This runs 4 complete scenarios:
1. **Normal Operations** - Standard grid conditions
2. **Peak Load Stress** - Critical demand period
3. **Emergency Response** - Frequency collapse risk
4. **Continuous Monitoring** - 24-hour simulation

### Example Output

```
SCENARIO 2: PEAK LOAD STRESS (Critical)

Grid State: critical
Demand: 1000.0 MW | Generation: 870.0 MW
Deficit: 130.0 MW
Frequency: 59.6 Hz (FALLING!) | Stress: 118.2%

Decision Summary:
- Demand Response Actions: 4
- Total Load Reduction: 0.52 MW
- Storage Action: discharge at 100% intensity
- Expected Storage Output: 95.00 MW
- Confidence: 89%

EXECUTING DECISION
✓ Demand Response: THERMO_001 - reduce_temperature to 20.0°C
✓ Demand Response: THERMO_003 - reduce_temperature to 19.5°C
✓ Storage: DISCHARGE at 100% intensity (95.0 MW for 60 min)

Impact Assessment:
Total Load Relief: 95.52 MW
New Demand Balance: 904.48 MW
```

## 📊 Agent Decision Flow

### Demand Response Agent Flow

```
analyze_grid_state
    ↓
identify_responsive_devices (filter by flexibility)
    ↓
generate_dr_actions (LLM generates specific commands)
    ↓
optimize_actions (maximize efficiency, minimize discomfort)
    ↓
validate_actions (verify device compatibility)
    ↓
return validated actions
```

### Storage Trigger Agent Flow

```
assess_conditions (overall grid health)
    ↓
check_price_signals (spot price analysis)
    ↓
evaluate_frequency (stability assessment)
    ↓
make_decision (discharge/charge/hold)
    ↓
generate_action (create trigger command)
    ↓
return action
```

## 🧠 AI Model Details

- **LLM Model**: Llama 3.1 70B Versatile (via Groq)
- **Framework**: LangGraph for agent orchestration
- **Temperature**: 0.2-0.3 (deterministic decisions)
- **Max Tokens**: 1024-2048 per decision

The Groq API provides real-time LLM inference (sub-100ms latency) through specialized inference servers for instant grid decisions.

## 🔄 Grid Status Levels

| Status | Frequency (Hz) | Demand Stress | Action |
|--------|---|---|---|
| NORMAL | ≥60.0 | <50% | Monitor |
| WARNING | 59.5-59.9 | 50-100% | Prepare DR |
| CRITICAL | 59.0-59.4 | 100-150% | Full DR + Storage |
| EMERGENCY | <59.0 | >150% | Max discharge |

## 📈 Thermostat Flexibility Scoring

Flexibility Score (0-1) impacts device selection:
- **0.9-1.0**: Office Buildings, Tech Campuses (high flexibility)
- **0.7-0.8**: Commercial Spaces (good flexibility)
- **0.5-0.7**: Residential (lower flexibility, comfort priority)
- **<0.5**: Not recommended for DR

## 🔐 Security Considerations

- Store API keys in `.env`, never in code
- Validate all temperature changes within comfort bounds
- Maintain audit logs of all actions
- Implement rate limiting on device commands
- Use encryption for device communication in production

## 🧪 Testing

Run the comprehensive demo:
```bash
python main.py
```

For specific agent testing:

```python
# Test Demand Response Agent
from demand_response_agent import DemandResponseAgent
agent = DemandResponseAgent()
result = agent.run(grid_state, thermostats)

# Test Storage Trigger Agent
from storage_trigger_agent import StorageTriggerAgent
agent = StorageTriggerAgent()
result = agent.run(grid_state, spot_price)
```

## 📝 Configuration

### Thermostat Parameters
- `max_reduction_capacity`: Maximum MW this device can reduce (0.01-0.5)
- `flexibility_score`: 0-1, how easily device can respond
- `owner_preferences`: Min/max comfort temperature bounds

### Grid Parameters
- `peak_load_threshold_mw`: Grid capacity threshold (usually 1000-1500 MW)
- `low_frequency_threshold_hz`: Frequency emergency threshold (59.0-59.5 Hz)
- `renewable_generation_pct`: Percentage from renewable sources

## 🌍 Real-World Integration

To integrate with real grid infrastructure:

1. **Replace mock thermostat updates** in `grid_manager._execute_dr_action()` with:
   - REST API calls to thermostat APIs
   - MQTT messages to IoT devices
   - Pub/Sub messaging for real-time control

2. **Connect real grid data** from:
   - SCADA systems
   - Smart meter networks
   - Market data providers
   - Weather APIs

3. **Implement persistence**:
   - Database for decision history
   - Time-series DB for grid metrics
   - Audit logging

## 📚 Key Concepts

### Agentic AI Pattern
The agents operate autonomously within defined constraints, using LLM reasoning to make complex grid decisions without human intervention.

### Frequency-Based Control
Grid frequency (50/60 Hz) is the primary stability metric. Deviation triggers automatic load reduction or battery discharge.

### Multi-Agent Orchestration
LangGraph enables sequential agent execution with state management, allowing demand response and storage trigger to work together.

### Groq API Optimization
Groq's inference engine provides <100ms response times critical for real-time grid control.

## 🤝 Contributing

This project demonstrates patterns for:
- Multi-agent AI systems using LangGraph
- Real-time LLM inference via Groq
- Energy grid optimization
- IoT device orchestration

## 📄 License

MIT License - Feel free to use for research and production.

## 🔗 References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [Groq API Docs](https://console.groq.com/docs)
- [Smart Grid Concepts](https://en.wikipedia.org/wiki/Smart_grid)

## ⚡ Performance Notes

- **Decision latency**: ~2-5 seconds (includes LLM inference)
- **Throughput**: Can manage 1000+ thermostats per decision cycle
- **Memory**: ~200-300 MB per agent instance
- **Cost**: Minimal with Groq free tier

## 🐛 Troubleshooting

**GROQ_API_KEY not found**
- Ensure `.env` file exists in project root
- Check API key is valid at console.groq.com

**LLM response parsing errors**
- Check JSON formatting in agent responses
- Verify Groq API is accessible
- Check network connectivity

**Device not found**
- Verify thermostat IDs match registration
- Check thermostat is marked as responsive

## 💡 Future Enhancements

- [ ] Machine learning model for demand prediction
- [ ] Multi-node federation for regional grids
- [ ] V2G (Vehicle-to-Grid) integration
- [ ] Solar/Wind forecasting integration
- [ ] Dynamic pricing optimization
- [ ] Real-time anomaly detection

---

**Questions?** Create an issue or check the example usage in `main.py`.
