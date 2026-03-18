"""
Smart Grid Demand Response Agent - Interactive Dashboard
Run: streamlit run dashboard.py
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
if not os.getenv("GROQ_API_KEY") and os.getenv("api_key"):
    os.environ["GROQ_API_KEY"] = os.getenv("api_key")

from models import Thermostat, ThermostatMode, GridState, GridStatus
from dr_controller import DRController
from data_loader import SmartGridDataLoader

# Page config
st.set_page_config(
    page_title="Smart Grid DR Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
    }
    .status-critical { color: #ff4444; font-weight: bold; }
    .status-warning { color: #ffaa00; font-weight: bold; }
    .status-normal { color: #44aa44; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Title
st.title("⚡ Smart Grid Demand Response Agent")
st.markdown("*Real-time Demand Response Management with AI-powered Load Balancing*")

# Sidebar
with st.sidebar:
    st.header("🎛️ Configuration")
    scenario_choice = st.selectbox(
        "Select Data Source",
        ["Real Kaggle Data", "Synthetic Scenarios"]
    )
    
    if scenario_choice == "Real Kaggle Data":
        num_scenarios = st.slider("Number of Scenarios", 1, 5, 3)
    else:
        num_scenarios = 3

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🌡️ Devices", "📈 Analytics", "ℹ️ About"])

# ============ TAB 1: DASHBOARD ============
with tab1:
    st.header("Real-Time Grid Status")
    
    # Load data
    with st.spinner("Loading dataset..."):
        if scenario_choice == "Real Kaggle Data":
            loader = SmartGridDataLoader()
            scenarios = loader.get_dataset_scenarios(samples=num_scenarios)
        else:
            # Create synthetic scenarios
            scenarios = []
            grid_states = [
                GridState(datetime.now(), 800, 850, 60.0, GridStatus.NORMAL, 45, 1000),
                GridState(datetime.now(), 950, 880, 59.7, GridStatus.WARNING, 30, 1000),
                GridState(datetime.now(), 980, 850, 59.4, GridStatus.CRITICAL, 25, 1000),
            ]
            for i, grid in enumerate(grid_states[:num_scenarios]):
                thermostats = [
                    Thermostat(f"TH_{j:03d}", f"Building {j}", 22 + j*0.1, 22,
                             ThermostatMode.COOLING, 0.1 + j*0.02, 0.7 + j*0.05)
                    for j in range(5 + i*3)
                ]
                scenarios.append({
                    'grid': grid,
                    'thermostats': thermostats,
                    'description': f"Scenario {i+1}"
                })
    
    # Initialize session state for scenario selection
    if 'selected_scenario' not in st.session_state:
        st.session_state.selected_scenario = 0
    
    # Scenario selector
    col_scenario = st.columns(num_scenarios)
    
    for idx, (col, scenario) in enumerate(zip(col_scenario, scenarios)):
        with col:
            grid = scenario['grid']
            status_color = "🟢" if grid.status == GridStatus.NORMAL else "🟡" if grid.status == GridStatus.WARNING else "🔴"
            freq_display = f"{grid.frequency_hz:.2f} Hz"
            
            if st.button(f"{status_color} {scenario['description']}\n{freq_display}", key=f"btn_{idx}"):
                st.session_state.selected_scenario = idx
    
    # Display selected scenario
    scenario = scenarios[st.session_state.selected_scenario]
    grid = scenario['grid']
    thermostats = scenario['thermostats']
    
    st.divider()
    
    # Grid metrics - 4 columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "⚡ Demand",
            f"{grid.demand_mw:.1f} MW",
            f"{grid.stress_level:.0%} stress",
            delta_color="off"
        )
    
    with col2:
        st.metric(
            "🔋 Generation",
            f"{grid.generation_mw:.1f} MW",
            f"{grid.renewable_pct:.0f}% renewable"
        )
    
    with col3:
        freq_color = "inverse" if grid.frequency_hz < 59.9 else "off"
        st.metric(
            "📡 Frequency",
            f"{grid.frequency_hz:.2f} Hz",
            "Normal" if grid.frequency_hz >= 59.9 else "Low",
            delta_color=freq_color
        )
    
    with col4:
        status_emoji = "🟢" if grid.status == GridStatus.NORMAL else "🟡" if grid.status == GridStatus.WARNING else "🔴"
        st.metric(
            "Status",
            f"{status_emoji} {grid.status.value.upper()}",
            f"{len(thermostats)} devices ready"
        )
    
    st.divider()
    
    # Grid visualization - Supply vs Demand
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        st.subheader("📊 Supply vs Demand")
        fig = go.Figure(data=[
            go.Bar(name='Demand', x=['Current'], y=[grid.demand_mw], marker_color='#ff6b6b'),
            go.Bar(name='Generation', x=['Current'], y=[grid.generation_mw], marker_color='#51cf66'),
        ])
        fig.update_layout(
            barmode='group',
            height=350,
            showlegend=True,
            yaxis_title="MW",
            title_font_size=16
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_viz2:
        st.subheader("🌍 Energy Mix")
        renewable = grid.renewable_pct
        non_renewable = 100 - renewable
        fig = go.Figure(data=[
            go.Pie(
                labels=['Renewable', 'Traditional'],
                values=[renewable, non_renewable],
                marker=dict(colors=['#51cf66', '#a5d6ff']),
                hole=0.4
            )
        ])
        fig.update_layout(height=350, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Run DR Agent
    st.subheader("🤖 Demand Response Agent")
    
    if st.button("▶️ Run DR Agent", key="run_dr"):
        with st.spinner("Running demand response analysis..."):
            try:
                controller = DRController()
                for t in thermostats:
                    controller.register_thermostat(t)
                
                result = controller.run_dr(grid)
                actions = result.get('actions', [])
                analysis = result.get('analysis', 'No analysis')
                
                # Results
                if actions:
                    st.success(f"✅ {len(actions)} DR Actions Generated!")
                    total_reduction = sum(a.expected_reduction_mw for a in actions)
                    
                    col_res1, col_res2, col_res3 = st.columns(3)
                    with col_res1:
                        st.metric("Actions", len(actions))
                    with col_res2:
                        st.metric("Reduction", f"{total_reduction:.3f} MW")
                    with col_res3:
                        pct = (total_reduction / grid.demand_mw * 100) if grid.demand_mw > 0 else 0
                        st.metric("Impact", f"{pct:.1f}%")
                    
                    # Apply actions
                    if st.button("✅ Apply All Actions"):
                        controller.apply_all_actions(actions)
                        st.success("Actions applied to thermostats!")
                    
                    # Show action details
                    st.markdown("**Action Details:**")
                    for action in actions[:10]:
                        with st.expander(f"{action.device_id} - {action.action}"):
                            col_a1, col_a2, col_a3 = st.columns(3)
                            with col_a1:
                                st.write(f"**Target Temp:** {action.target_temp}°C")
                            with col_a2:
                                st.write(f"**Expected Reduction:** {action.expected_reduction_mw:.4f} MW")
                            with col_a3:
                                st.write(f"**Priority:** {action.priority}")
                else:
                    st.info("No DR actions needed - grid is stable")
                
                st.markdown(f"**Agent Analysis:** {analysis}")
            
            except Exception as e:
                st.error(f"Error running agent: {str(e)}")
                st.info("Make sure GROQ_API_KEY is set in .env file")


# ============ TAB 2: DEVICES ============
with tab2:
    st.header("🌡️ Thermostat Pool")
    
    scenario = scenarios[st.session_state.selected_scenario]
    thermostats = scenario['thermostats']
    
    # Statistics
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.metric("Total Devices", len(thermostats))
    with col_stat2:
        total_capacity = sum(t.capacity_mw for t in thermostats)
        st.metric("Total Capacity", f"{total_capacity:.1f} MW")
    with col_stat3:
        avg_temp = sum(t.current_temp for t in thermostats) / len(thermostats)
        st.metric("Avg Temperature", f"{avg_temp:.1f}°C")
    with col_stat4:
        avg_flexibility = sum(t.flexibility for t in thermostats) / len(thermostats)
        st.metric("Avg Flexibility", f"{avg_flexibility:.2f}")
    
    st.divider()
    
    # Device table
    st.subheader("Device Status")
    device_data = []
    for t in thermostats:
        device_data.append({
            "Device ID": t.device_id,
            "Location": t.location,
            "Current (°C)": f"{t.current_temp:.1f}",
            "Target (°C)": f"{t.target_temp:.1f}",
            "Mode": t.mode.value.upper(),
            "Capacity (MW)": f"{t.capacity_mw:.3f}",
            "Flexibility": f"{t.flexibility:.2f}",
            "Status": "🟢 Online" if t.is_online else "🔴 Offline"
        })
    
    st.dataframe(device_data, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Capacity visualization
    st.subheader("📊 Device Capacity Distribution")
    cap_data = {
        'device': [t.device_id for t in thermostats],
        'capacity': [t.capacity_mw for t in thermostats],
        'flexibility': [t.flexibility for t in thermostats]
    }
    
    fig = px.bar(
        cap_data,
        x='device',
        y='capacity',
        title='Thermostat Capacity by Device',
        labels={'capacity': 'Capacity (MW)', 'device': 'Device ID'},
        color='flexibility',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


# ============ TAB 3: ANALYTICS ============
with tab3:
    st.header("📈 Grid Analytics")
    
    if scenario_choice == "Real Kaggle Data":
        with st.spinner("Analyzing dataset..."):
            loader = SmartGridDataLoader()
            df = loader.load_data()
            
            # Data overview
            st.subheader("Dataset Overview")
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("Records", len(df))
            with col_info2:
                st.metric("Time Period", "Jan 1 - Dec 31, 2024")
            with col_info3:
                st.metric("Features", len(df.columns))
            
            st.divider()
            
            # Power consumption trend
            st.subheader("⚡ Power Metrics Distribution")
            col_a1, col_a2 = st.columns(2)
            
            with col_a1:
                fig_power = px.histogram(
                    df,
                    x='Power Consumption (kW)',
                    nbins=50,
                    title='Power Consumption Distribution',
                    labels={'Power Consumption (kW)': 'Power (kW)', 'count': 'Frequency'}
                )
                fig_power.update_layout(height=350)
                st.plotly_chart(fig_power, use_container_width=True)
            
            with col_a2:
                fig_freq = px.histogram(
                    df,
                    x='Power Factor',
                    nbins=50,
                    title='Power Factor Distribution',
                    labels={'Power Factor': 'Power Factor', 'count': 'Frequency'}
                )
                fig_freq.update_layout(height=350)
                st.plotly_chart(fig_freq, use_container_width=True)
            
            st.divider()
            
            # Renewable generation
            st.subheader("🌱 Renewable Energy Generation")
            col_b1, col_b2 = st.columns(2)
            
            with col_b1:
                fig_solar = px.box(
                    df,
                    y='Solar Power (kW)',
                    title='Solar Power Distribution',
                    labels={'Solar Power (kW)': 'Power (kW)'}
                )
                fig_solar.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig_solar, use_container_width=True)
            
            with col_b2:
                fig_wind = px.box(
                    df,
                    y='Wind Power (kW)',
                    title='Wind Power Distribution',
                    labels={'Wind Power (kW)': 'Power (kW)'}
                )
                fig_wind.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig_wind, use_container_width=True)
            
            st.divider()
            
            # Environment correlation
            st.subheader("🌡️ Environmental Factors")
            col_c1, col_c2, col_c3, col_c3 = st.columns(4)
            with col_c1:
                st.metric("Avg Temperature", f"{df['Temperature (°C)'].mean():.1f}°C")
            with col_c2:
                st.metric("Avg Humidity", f"{df['Humidity (%)'].mean():.0f}%")
            with col_c3:
                st.metric("Avg Voltage", f"{df['Voltage (V)'].mean():.1f}V")
            with col_c3:
                st.metric("Avg Current", f"{df['Current (A)'].mean():.2f}A")
    else:
        st.info("Load real Kaggle data from the sidebar to see analytics")


# ============ TAB 4: ABOUT ============
with tab4:
    st.header("ℹ️ About This System")
    
    st.markdown("""
    ## Smart Grid Demand Response Agent
    
    ### 🎯 Purpose
    This system uses **AI and LangGraph** to intelligently manage electricity demand during peak load periods
    by coordinating smart thermostats to reduce consumption without compromising user comfort.
    
    ### 🏗️ Architecture
    
    1. **Data Layer**
       - Real Kaggle dataset: 50,000 smart grid measurements
       - Features: Power consumption, renewable generation, voltage, frequency, temperature
       - Scaled to regional grid levels for realistic scenarios
    
    2. **Agent Layer (4-Node LangGraph Workflow)**
       - **Analyze**: Evaluates grid stress using LLM
       - **Select**: Identifies responsive thermostats
       - **Plan**: Generates specific temperature adjustments
       - **Validate**: Ensures safety constraints
    
    3. **Control Layer**
       - Thermostat pool management
       - Load reduction orchestration
       - Real-time action tracking
    
    ### 📊 Key Metrics
    
    | Metric | Value | Notes |
    |--------|-------|-------|
    | Grid Demand | 100-980 MW | Scaled from residential data |
    | Device Capacity | 50-700 MW | Individual thermostat impact |
    | Pool Capacity | 2000-7500 MW | Total coordinated load |
    | Frequency Nominal | 60 Hz | Critical @ <59.5 Hz |
    | Renewable Integration | 25-100% | From solar & wind generation |
    
    ### 🤖 LLM Model
    - **Provider**: Groq API
    - **Model**: llama-3.1-8b-instant
    - **Temperature**: 0.3 (deterministic decisions)
    
    ### 💾 Dependencies
    """)
    
    deps = """
    - **langgraph** - Workflow orchestration
    - **langchain** - LLM integration
    - **langchain-groq** - Groq API connector
    - **pandas** - Data manipulation
    - **kagglehub** - Dataset access
    - **streamlit** - Dashboard
    - **plotly** - Visualizations
    """
    st.code(deps.strip(), language="text")
    
    st.markdown("""
    ### 📚 Files
    - `models.py` - Data structures
    - `demand_response_agent.py` - AI agent
    - `dr_controller.py` - Control logic
    - `data_loader.py` - Kaggle integration
    - `example.py` - Synthetic scenarios
    - `example_with_real_data.py` - Real data demo
    - `dashboard.py` - This interface
    
    ### 🚀 Usage
    
    **Run Dashboard:**
    ```bash
    streamlit run dashboard.py
    ```
    
    **Run Examples:**
    ```bash
    python example.py
    python example_with_real_data.py
    ```
    
    ### 🔐 Setup
    1. Get free Groq API key from https://console.groq.com
    2. Add to `.env` file: `GROQ_API_KEY=your_key_here`
    3. Install dependencies: `pip install -r requirements.txt`
    4. Run: `streamlit run dashboard.py`
    
    ---
    
    **Built with** ⚡ **LangGraph** + **Groq** + **Real Grid Data**
    """)
    
    # Footer
    st.divider()
    col_footer1, col_footer2, col_footer3 = st.columns(3)
    with col_footer1:
        st.caption("🌍 Real Kaggle Dataset Integration")
    with col_footer2:
        st.caption("🤖 AI-Powered Load Management")
    with col_footer3:
        st.caption("📊 Real-Time Monitoring & Control")
