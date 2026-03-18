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

### Demand Response Agent (4-Node LangGraph)

```
Input: GridState + Thermostat List
    ↓
1️⃣ analyze_grid_state
   • Check: frequency_hz < 59.9 OR demand_surplus > 50 MW?
   • Output: need_dr (boolean)
    ↓
2️⃣ select_responsive_devices
   • Filter thermostats by flexibility (>0.5)
   • Sort by flexibility_score (highest first)
   • Select top N devices
    ↓
3️⃣ plan_dr_actions
   • For each selected device:
     - Calculate: target_temp = current_temp - 2°C
     - Calculate: reduction = capacity * flexibility * 0.5 MW
   • Output: List[DRAction]
    ↓
4️⃣ validate_actions
   • Verify target_temp within bounds
   • Check expected reductions sum
   • Return final validated actions
    ↓
Output: Result{'actions': [...], 'analysis': '...'}
```

### Real-World Decision Example

| Condition | Input | Decision | Actions |
|-----------|-------|----------|---------|
| **CRITICAL** | freq=59.71 Hz | Grid stressed | 3 actions, ~1.5 MW reduction |
| **NORMAL** | freq=60.07 Hz | Grid stable | 0 actions (no DR needed) |
| **NORMAL** | freq=60.00 Hz | Grid stable | 0 actions (no DR needed) |

## 🧠 LLM Configuration

- **Model**: Llama 3.1 8B Instant (via Groq)
- **Temperature**: 0.3 (deterministic responses)
- **Max Tokens**: 512 per decision
- **Latency**: ~2-5 seconds (includes network + inference)
- **Cost**: Free with Groq community tier

## 📈 Grid Status Definitions

| Status | Frequency | Surplus | DR Action |
|--------|-----------|---------|-----------|
| 🟢 NORMAL | ≥60.0 Hz | Any | None (stable) |
| 🟡 WARNING | 59.5-59.9 Hz | <50 MW | Prepare devices |
| 🔴 CRITICAL | <59.5 Hz OR >50 MW surplus | Peak | Execute DR |

## 🌡️ Thermostat Flexibility Scoring

Flexibility (0-1) determines how quickly a device can respond:
- **0.9-1.0**: Office/Tech buildings (high responsiveness)
- **0.7-0.8**: Commercial spaces (good responsiveness)
- **0.5-0.7**: Residential areas (moderate, comfort-aware)
- **<0.5**: Not selected for DR (comfort priority)

### Device Selection Example
```
Scenario 1: 5 devices selected
├── TH_002 (flex=0.90) ✓ Selected
├── TH_004 (flex=0.85) ✓ Selected  
├── TH_001 (flex=0.80) ✓ Selected
└── TH_000 (flex=0.70) ✗ Not selected
└── TH_003 (flex=0.75) ✗ Not selected
```

## 🔐 Security & Constraints

- ✅ API keys stored in `.env` (never committed)
- ✅ Temperature changes bounded within ±5°C
- ✅ All actions validated before execution
- ✅ Device-specific action constraints enforced
- ✅ Audit trail of all DR decisions

## 🧪 Testing

### Run All Scenarios

```bash
# Interactive dashboard with Kaggle data
streamlit run dashboard.py

# Command-line demonstration
python example_with_real_data.py

# Test agent with synthetic data
python test_agent_fix.py
```

### Test Output Example

```
--- SCENARIO 1 ---
Grid Frequency: 59.71 Hz
Grid Demand: 119.140 MW
Thermostats: 5 devices

✅ AGENT ANALYSIS:
Grid stress detected: critical

📋 DR ACTIONS:
Actions Generated: 3
Expected Reduction: 1.5000 MW
Impact: 1.26% of demand
```

### Unit Testing Demand Response Agent

```python
from demand_response_agent import create_dr_agent
from models import GridState, GridStatus, Thermostat, ThermostatMode

# Create test agent
agent = create_dr_agent()

# Create stressed grid
grid = GridState(
    datetime.now(),
    demand_mw=500, generation_mw=400,
    frequency_hz=59.7,  # Below threshold
    status=GridStatus.CRITICAL,
    renewable_pct=75
)

# Create thermostats
thermostats = [
    Thermostat(f"TH_{i:03d}", f"Bldg {i}", 22, 22,
              ThermostatMode.COOLING, 0.5, 0.7 + i*0.01)
    for i in range(5)
]

# Run agent
result = agent.invoke({
    'grid': grid,
    'thermostats': thermostats
})

assert len(result['actions']) > 0
assert result['analysis'] != ""
```

## 📁 Project Structure

```
smartGridLoadBalancer/
├── demand_response_agent.py    # 4-node LangGraph workflow
├── dr_controller.py            # Thermostat management & execution
├── data_loader.py              # Kaggle dataset integration
├── models.py                   # Data structures (GridState, Thermostat, etc)
├── dashboard.py                # Streamlit UI (4 tabs)
├── example_with_real_data.py   # Demo script with scenarios
├── test_agent_fix.py           # Unit tests
├── requirements.txt            # Dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

## 📝 Configuration

### Environment Variables (.env)
```bash
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
# Optional: Kaggle credentials (for dataset auto-download)
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
```

### Thermostat Parameters
```python
Thermostat(
    device_id="TH_001",           # Unique identifier
    location="Office Building",   # Physical location
    current_temp=22.5,            # Current temperature (°C)
    target_temp=22.0,             # Target setpoint
    mode=ThermostatMode.COOLING,  # HEATING or COOLING
    capacity_mw=0.5,              # Max reduction capacity
    flexibility=0.85              # 0-1 responsiveness score
)
```

### Grid Parameters
```python
GridState(
    timestamp=now,
    demand_mw=800,              # Current demand (MW)
    generation_mw=750,          # Current generation (MW)
    frequency_hz=59.8,          # Grid frequency
    status=GridStatus.CRITICAL, # NORMAL/WARNING/CRITICAL
    renewable_pct=45,           # Renewable % of generation
    stress_level=0.95           # Stress metric (0-1)
)
```

## 📊 Dashboard Features

### 📊 Dashboard Tab
- Real-time grid metrics (demand, generation, frequency)
- Supply vs demand bar chart
- Energy mix pie chart (renewable vs traditional)
- Scenario selector buttons
- "Run DR Agent" button for live execution

### 🌡️ Devices Tab
- Total devices, capacity, average temperature metrics
- Device status table (ID, location, current/target temps, capacity, flexibility)
- Capacity distribution chart by device

### 📈 Analytics Tab
- Dataset overview (50K records, 16 features)
- Power consumption distribution
- Power factor analysis
- Solar and wind power distribution
- Environmental factors (temperature, humidity, voltage, current)

### ℹ️ About Tab
- System architecture overview
- Feature list and capabilities
- Quick start instructions

## 🐛 Troubleshooting

### GROQ_API_KEY not found
```bash
# Check .env file exists
ls -la .env

# Set environment variable
export GROQ_API_KEY="your-key-here"

# Verify
echo $GROQ_API_KEY
```

### Streamlit app not starting
```bash
# Clear Streamlit cache
streamlit cache clear

# Check port is available
lsof -i :8501

# Use different port
streamlit run dashboard.py --server.port 8502
```

### Kaggle dataset not downloading
```bash
# Ensure kagglehub is installed
pip install kagglehub

# Check internet connection
ping console.groq.com
```

### Agent returns "No DR actions needed" for stressed grid
- Verify grid frequency < 59.9 Hz or surplus > 50 MW
- Check thermostat flexibility > 0.5
- Confirm at least 3 devices registered
- Check GROQ_API_KEY is valid

## ✨ Recent Updates (March 19, 2026)

### Fixed Issues
✅ **Scenario Differentiation Bug**
- Problem: All scenarios showed identical data
- Root Cause: `example_with_real_data.py` reused controller across scenarios, accumulating thermostats
- Solution: Create fresh controller for each scenario
- Verification: Scenario 1 shows 59.71 Hz with 3 actions, Scenarios 2-3 show normal frequency with 0 actions

✅ **Dashboard Scenario Selection**
- Problem: Clicking scenario buttons didn't switch between scenarios
- Root Cause: Streamlit rerun was resetting `selected_scenario` variable to 0
- Solution: Implemented Streamlit `session_state` for persistent selection
- Verification: Dashboard now properly switches scenarios, metrics update in real-time

### Tested Scenarios
```
Dashboard: http://localhost:8501
│
├── Scenario 1: 59.71 Hz (CRITICAL) → 5 devices, 3 actions
├── Scenario 2: 60.07 Hz (NORMAL)   → 8 devices, 0 actions
└── Scenario 3: 60.00 Hz (NORMAL)   → 11 devices, 0 actions
```

## 📚 Key Insights

### Deterministic vs LLM-Based
- **Old Approach**: LLM generated device selections and actions (unreliable JSON parsing)
- **New Approach**: Deterministic algorithms using mathematical thresholds
- **Result**: 100% consistent, fast, and verifiable decisions

### Scenario Variation Strategy
Real data produces naturally varied scenarios:
- **Scenario 1**: Low frequency (59.71 Hz) triggers critical status and DR actions
- **Scenario 2**: Near-normal frequency (60.07 Hz) with different demand patterns
- **Scenario 3**: Stable frequency (60.00 Hz) requiring no response

### Grid Stress Detection
```python
def needs_dr(grid: GridState) -> bool:
    return (grid.frequency_hz < 59.9 or 
            grid.demand_surplus > 50)
```

## 🔗 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Groq API Console](https://console.groq.com)
- [Kaggle Smart Grid Dataset](https://www.kaggle.com/datasets/ziya07/smart-grid-real-time-load-monitoring-dataset)
- [Smart Grid Standards (IEC 61970)](https://en.wikipedia.org/wiki/IEC_61970)

## ⚡ Performance

| Aspect | Value |
|--------|-------|
| Decision Time | 2-5 seconds |
| LLM Latency | ~1-2 seconds (Groq) |
| Data Load Time | ~1-2 seconds (50K records) |
| Dashboard Startup | ~3-5 seconds |
| Max Devices/Scenario | 100+ thermostats |
| Memory Usage | 150-200 MB |

## 💡 Future Enhancements

- [ ] Time-series forecasting for demand prediction
- [ ] Machine learning model for device responsiveness
- [ ] Multi-region federation support
- [ ] Vehicle-to-Grid (V2G) integration
- [ ] Solar/wind generation forecasting
- [ ] Price-responsive DR scheduling
- [ ] Real-time SCADA connectivity
- [ ] Anomaly detection for grid faults
- [ ] Advanced visualization dashboards
- [ ] API gateway for third-party integrations

---

**Current Status**: ✅ Fully functional with real Kaggle data, interactive dashboard, and tested scenarios.

**Questions or Issues?** Review the [troubleshooting](#-troubleshooting) section or check the example scripts in the project.
