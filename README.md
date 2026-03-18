# Smart Grid Load-Balancer with Agentic AI

An intelligent demand response system for managing electric grids using AI-powered load balancing with LangGraph, LangChain, and Groq API. Uses real Kaggle smart grid dataset with interactive Streamlit dashboard.

## 🌐 Overview

This project implements an **Demand Response Agent** that automatically identifies stressed grids and intelligently manages thermostat loads to prevent blackouts. It uses:

- **LangGraph**: 4-node agentic workflow for deterministic decision-making
- **Real Data**: 50,000 real smart grid measurements from Kaggle
- **AI Decision Engine**: Groq API for fast LLM inference
- **Interactive Dashboard**: Streamlit UI with real-time visualization
- **Scenario Testing**: Multiple grid conditions to test DR responses

## 🏗️ Architecture

### Demand Response Agent (4-Node Workflow)

```
DemandResponseAgent (LangGraph-based)
├── 1️⃣ analyze_grid_state
│   └── Check: Frequency < 59.9 Hz OR Surplus > 50 MW?
├── 2️⃣ select_responsive_devices  
│   └── Sort by flexibility score, select top candidates
├── 3️⃣ plan_dr_actions
│   └── Calculate temperature targets for max reduction
└── 4️⃣ validate_actions
    └── Verify actions are safe and achievable
```

### Core Components

- **DRController**: Manages thermostat pool and executes agent decisions
- **SmartGridDataLoader**: Loads and processes Kaggle dataset (50K records)
- **GridState**: Real-time grid conditions (demand, generation, frequency, status)
- **Thermostat**: Connected device with current temp, target temp, capacity, flexibility
- **DRAction**: Specific temperature adjustment commands

## 🚀 Features

### Demand Response Agent
- ✅ Analyzes real grid stress (frequency-based detection)
- ✅ Deterministic device selection using flexibility scores
- ✅ Generates temperature-adjustment actions for load reduction
- ✅ Validates all actions before execution
- ✅ Works with 50,000+ real smart grid measurements
- ✅ Responds differently based on actual grid conditions (NORMAL, WARNING, CRITICAL)

### Interactive Dashboard (Streamlit)
- 📊 **Dashboard Tab**: Real-time grid metrics with supply vs demand visualization
- 🌡️ **Devices Tab**: Thermostat pool status, capacity distribution, device details
- 📈 **Analytics Tab**: Historical grid data analysis from Kaggle dataset
- ℹ️ **About Tab**: System documentation and architecture overview
- 🎛️ **Scenario Selection**: Switch between different grid conditions
- ▶️ **DR Agent Execution**: Run agent with one click, see real-time actions

### Real Data Integration
- 📥 Loads Kaggle smart grid dataset automatically
- 🔄 Generates 3 realistic scenarios with different grid conditions
- 📊 16 features: power consumption, voltage, frequency, renewable %, temperature, humidity, etc.
- 🌍 100,000x scaling from residential (kW) to regional (MW) levels

## 📋 Installation

### Prerequisites
- Python 3.9+
- Groq API key (free tier: https://console.groq.com)
- Kaggle account (for dataset, optional - auto-downloads)

### Setup

1. **Clone/Navigate to project**
   ```bash
   cd smartGridLoadBalancer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   export GROQ_API_KEY="your-api-key-here"
   ```

5. **Get Groq API Key**
   - Visit https://console.groq.com
   - Sign up/login (free)
   - Create API key in Settings
   - Copy to `.env` file

## 🎯 Quick Start

### Run Interactive Dashboard

```bash
streamlit run dashboard.py
```

Open browser to `http://localhost:8501` and:
1. Select **Real Kaggle Data** from sidebar
2. Click scenario buttons to switch between grid conditions
3. Click **"▶️ Run DR Agent"** to see real-time actions
4. Browse **Devices tab** to see thermostat pool details
5. Check **Analytics tab** for historical grid data

### Run Example Script

```bash
python example_with_real_data.py
```

Shows 3 scenarios with real grid data:
- **Scenario 1**: 59.71 Hz (CRITICAL) - 5 devices, 3 DR actions
- **Scenario 2**: 60.07 Hz (Normal) - 8 devices, 0 actions
- **Scenario 3**: 60.00 Hz (Normal) - 11 devices, 0 actions

### Basic Python Usage

```python
from data_loader import SmartGridDataLoader
from dr_controller import DRController
from models import GridState

# Load real Kaggle data
loader = SmartGridDataLoader()
scenarios = loader.get_dataset_scenarios(samples=3)

# Run agent on a scenario
scenario = scenarios[0]
grid = scenario['grid']
thermostats = scenario['thermostats']

controller = DRController()
for t in thermostats:
    controller.register_thermostat(t)

# Execute demand response
result = controller.run_dr(grid)
print(f"Actions: {len(result['actions'])}")
print(f"Analysis: {result['analysis']}")

# Apply actions to devices
controller.apply_all_actions(result['actions'])
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
