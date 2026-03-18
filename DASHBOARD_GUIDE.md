# 📊 Smart Grid Demand Response Dashboard

**Interactive web-based interface for monitoring and controlling AI-powered smart grid demand response**

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Key
Create `.env` file with your Groq API key:
```
GROQ_API_KEY=your_key_here
```

Get a free key: https://console.groq.com

### 3. Run Dashboard
```bash
streamlit run dashboard.py
```

Or use the convenience script:
```bash
bash run_dashboard.sh
```

The dashboard will open at **http://localhost:8501**

---

## 📖 Dashboard Features

### 🎯 Tab 1: Dashboard (Real-Time Grid Status)

**What You See:**
- **4 Main Metrics**
  - ⚡ Current demand (MW) with stress level
  - 🔋 Available generation with renewable %
  - 📡 Grid frequency in Hz
  - 🟢/🟡/🔴 Grid status (Normal/Warning/Critical)

- **Scenario Selection**
  - Choose from 1-5 grid scenarios
  - Real Kaggle data OR synthetic scenarios
  - Each shows different grid conditions

- **Supply vs Demand Chart**
  - Visual comparison of power flow
  - Real-time demand and generation

- **Energy Mix Pie Chart**
  - Renewable vs traditional generation
  - Historical data from dataset

- **🤖 Demand Response Agent Control**
  - **▶️ Run DR Agent** - Analyzes grid and recommends actions
  - **✅ Apply All Actions** - Executes temperature adjustments
  - Shows number of actions, reduction amount, and impact %
  - Expandable details for each device action

---

### 🌡️ Tab 2: Devices (Thermostat Pool)

**What You See:**
- **Device Statistics**
  - Total devices in pool
  - Total load reduction capacity (MW)
  - Average temperature across pool
  - Average response flexibility (0-1 scale)

- **Device Status Table**
  - Device ID and location
  - Current vs target temperature
  - Operating mode (heating/cooling/off)
  - Individual load reduction capacity
  - Response flexibility score
  - Online/offline status

- **Capacity Distribution Chart**
  - Bar chart showing each device's capacity
  - Color-coded by flexibility (darker = more flexible)
  - Identifies high-capacity responsive devices

---

### 📈 Tab 3: Analytics (Dataset Insights)

**What You See** *(with Real Kaggle Data selected)*:

- **Dataset Overview**
  - 50,000 records of real smart grid measurements
  - Time period: Full year 2024
  - 16 different features

- **Power Metrics**
  - Power consumption distribution histogram
  - Power factor distribution
  - Shows typical load patterns

- **Renewable Energy**
  - Solar generation distribution (box plot)
  - Wind generation distribution (box plot)
  - Variability and capacity analysis

- **Environmental Factors**
  - Average temperature
  - Average humidity
  - Voltage and current statistics

---

### ℹ️ Tab 4: About

- System architecture explanation
- Key metrics and thresholds
- LLM configuration (Groq API)
- Complete file list and descriptions
- Setup instructions
- Dependency list

---

## 💡 How to Use

### Scenario 1: Monitor Normal Grid
1. Go to **Dashboard** tab
2. Select "Real Kaggle Data" from sidebar
3. Click "Scenario 1" button
4. View all metrics - everything is green/normal
5. Click "Run DR Agent" - should say no actions needed

### Scenario 2: Peak Demand Response
1. Click "Scenario 2" button
2. Notice frequency drops to 59.7 Hz (warning)
3. Notice demand exceeds generation (orange bar longer)
4. Click "Run DR Agent"
5. Agent suggests temperature reductions
6. Click "Apply All Actions"
7. Watch thermostat targets update in **Devices** tab

### Scenario 3: Emergency Response
1. Click "Scenario 3" button  
2. Notice frequency at critical level (<59.5 Hz)
3. Stress level shows high percentage
4. Click "Run DR Agent"
5. Agent recommends aggressive load reduction
6. Check action details in expandable boxes
7. See which devices contribute most to reduction

### Analyze Real Data Patterns
1. Go to **Analytics** tab
2. View power consumption patterns
3. See renewable generation opportunities
4. Check environmental factor distributions
5. Understand grid variability

---

## 🔧 Configuration

### Sidebar Options
- **Select Data Source**
  - Real Kaggle Data: Uses actual smart grid measurements
  - Synthetic Scenarios: Pre-configured test cases
  
- **Number of Scenarios** *(when Real Kaggle Data selected)*
  - 1-5 scenarios to analyze
  - More scenarios = more grid conditions

### Grid Status Indicator
- 🟢 **NORMAL** - Frequency ≥ 59.9 Hz, balanced supply
- 🟡 **WARNING** - Frequency 59.5-59.9 Hz or slight imbalance
- 🔴 **CRITICAL** - Frequency < 59.5 Hz or major imbalance

---

## 📊 Understanding the Metrics

### Stress Level (0-100%)
- Excess demand divided by capacity
- 0% = No stress (balanced grid)
- 50%+ = Needs demand response
- 100%+ = Critical (emergency measures)

### Power Factor
- Measure of reactive vs active power
- 1.0 = Perfect
- < 0.95 = Degraded, affects frequency

### Frequency (Hz)
- Should be 60 Hz
- < 59.5 Hz = Grid collapse risk
- > 60.5 Hz = Oversupply risk

### Renewable %
- Percentage of generation from solar/wind
- Higher = cleaner but more variable
- Lower = stable but less sustainable

---

## 🎯 DR Agent Behavior

### What the Agent Does
1. **Analyzes** grid stress level (frequency, load balance)
2. **Selects** most responsive thermostats
3. **Plans** specific temperature adjustments (±2-4°C)
4. **Validates** actions are safe (16-28°C bounds)

### Expected Results
- **Normal grid**: No actions (grid is stable)
- **Warning grid**: 3-5 devices, 10-50 MW reduction
- **Critical grid**: 8-15 devices, 100+ MW reduction

### Safety Features
- Temperature kept within comfort bounds
- Only responsive devices selected
- Actions validated before execution
- Real-time monitoring enabled

---

## 📱 Layout

```
┌─────────────────────────────────────────┐
│        Smart Grid DR Dashboard          │
├──────────────────────────────────────────┤
│ Dashboard │ Devices │ Analytics │ About │
├──────────────────────────────────────────┤
│                                          │
│  [Configuration Sidebar]    [Main View]  │
│  • Data Source              • Metrics   │
│  • Scenarios                • Charts    │
│  • Options                  • Controls  │
│                                          │
└──────────────────────────────────────────┘
```

---

## ⚙️ Technical Details

### Tech Stack
- **Frontend**: Streamlit (Python web framework)
- **Visualization**: Plotly (interactive charts)
- **Backend**: LangGraph + Groq LLM
- **Data**: Kaggle dataset + pandas
- **Deployment**: Local dev server

### Data Flow
```
Kaggle Dataset (50K records)
    ↓
Data Loader (scales to MW)
    ↓
GridState & Thereostats
    ↓
Streamlit Dashboard
    ↓
(User selects scenario)
    ↓
DR Controller
    ↓
LangGraph Agent (4 nodes)
    ↓
Groq API (LLM reasoning)
    ↓
DR Actions
    ↓
Dashboard displays results
```

---

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Check Streamlit installation
pip install streamlit --upgrade

# Run with verbose logging
streamlit run dashboard.py --logger.level=debug
```

### "GROQ_API_KEY not set"
```bash
# Create .env file in project directory
echo "GROQ_API_KEY=your_key_here" > .env

# Verify
cat .env
```

### Dataset download fails
```bash
# Manually download dataset
python -c "from data_loader import SmartGridDataLoader; SmartGridDataLoader()"

# Check cache location
ls ~/.cache/kagglehub/
```

### Agent returns no actions
- This is normal when grid is stable
- Try selecting a different scenario
- Check grid frequency and demand values
- Verify thermostats have capacity > 0

---

## 📚 Example Workflows

### Monitor Grid Health
1. Open Dashboard tab
2. Set to "Real Kaggle Data"
3. Review all 3+ scenarios
4. Note frequency and demand patterns
5. Go to Analytics tab for historical insights

### Execute DR Program
1. Dashboard tab
2. Identify high-stress scenario (🔴 CRITICAL)
3. Note which devices will be affected
4. Run DR Agent
5. Review action details
6. Click Apply Actions
7. Verify in Devices tab that targets updated

### Analyze Infrastructure
1. Analytics tab
2. Review thermostat capacities
3. Check device distribution
4. Calculate total available load reduction
5. Compare with peak demand scenarios

---

## 🎓 Learning Path

1. **Start**: Run with Synthetic Scenarios
2. **Understand**: Read About tab
3. **Explore**: Switch to Real Kaggle Data
4. **Analyze**: Review Analytics tab
5. **Execute**: Run DR Agent on different scenarios
6. **Optimize**: Check Devices tab for capacity utilization

---

## 🔗 Resources

- **Groq Console**: https://console.groq.com
- **Kaggle Dataset**: https://kaggle.com/datasets/ziya07/smart-grid-real-time-load-monitoring-dataset
- **Streamlit Docs**: https://docs.streamlit.io
- **LangGraph**: https://langchain-ai.github.io/langgraph/

---

**Ready to manage your smart grid? Start the dashboard now!** ⚡
