"""
Smart Grid Demand Response - Minimalistic Dashboard
Run: streamlit run dashboard_v2.py
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
if not os.getenv("GROQ_API_KEY") and os.getenv("api_key"):
    os.environ["GROQ_API_KEY"] = os.getenv("api_key")

from models import Thermostat, ThermostatMode, GridState, GridStatus
from dr_controller import DRController

# Page config
st.set_page_config(
    page_title="Smart Grid DR",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("⚡ Smart Grid Demand Response Agent")

# Initialize session state
if 'selected_scenario' not in st.session_state:
    st.session_state.selected_scenario = 0
if 'custom_scenarios' not in st.session_state:
    st.session_state.custom_scenarios = []
    # Add default sample scenarios
    st.session_state.custom_scenarios = [
        {
            'name': 'Normal Day',
            'grid': GridState(
                timestamp=datetime.now(),
                demand_mw=800,
                generation_mw=850,
                frequency_hz=60.0,
                status=GridStatus.NORMAL,
                renewable_pct=45,
                capacity_mw=1200,
            ),
            'thermostats': [
                Thermostat(f'TH_{i:04d}', f'Zone_{chr(65 + i)}', 22.0, 22.0,
                          ThermostatMode.COOLING, 0.1, 0.75)
                for i in range(5)
            ],
            'description': 'Normal Day - Balanced supply and demand'
        },
        {
            'name': 'Peak Demand',
            'grid': GridState(
                timestamp=datetime.now(),
                demand_mw=950,
                generation_mw=880,
                frequency_hz=59.7,
                status=GridStatus.WARNING,
                renewable_pct=30,
                capacity_mw=1200,
            ),
            'thermostats': [
                Thermostat(f'TH_{i:04d}', f'Zone_{chr(65 + (i % 26))}', 22.0, 22.0,
                          ThermostatMode.COOLING, 0.12, 0.7)
                for i in range(8)
            ],
            'description': 'Peak Demand - WARNING - Increased frequency control needed'
        },
        {
            'name': 'Emergency',
            'grid': GridState(
                timestamp=datetime.now(),
                demand_mw=980,
                generation_mw=850,
                frequency_hz=59.3,
                status=GridStatus.CRITICAL,
                renewable_pct=25,
                capacity_mw=1200,
            ),
            'thermostats': [
                Thermostat(f'TH_{i:04d}', f'Zone_{chr(65 + (i % 26))}', 22.0, 22.0,
                          ThermostatMode.COOLING, 0.15, 0.75)
                for i in range(15)
            ],
            'description': 'Emergency - CRITICAL - Severe frequency deviation'
        }
    ]

# Tabs
tab1, tab2 = st.tabs(["Dashboard", "Create Scenario"])

# ============ TAB 1: DASHBOARD ============
with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Available Scenarios")
    
    st.divider()
    
    scenarios = st.session_state.custom_scenarios
    scenario_names = [s['name'] for s in scenarios]
    
    if not scenarios:
        st.error("❌ No scenarios available. Create one in the 'Create Scenario' tab.")
        st.stop()
    
    # Scenario buttons
    cols = st.columns(len(scenarios))
    for idx, (col, name) in enumerate(zip(cols, scenario_names)):
        with col:
            if st.button(name, key=f"scenario_{idx}", use_container_width=False):
                st.session_state.selected_scenario = idx
    
    # Display selected scenario
    scenario = scenarios[st.session_state.selected_scenario]
    grid = scenario['grid']
    thermostats = scenario['thermostats']
    
    # Grid Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📡 Frequency", f"{grid.frequency_hz:.2f} Hz", 
                 "Stress" if grid.frequency_hz < 59.9 else "Stable")
    
    with col2:
        st.metric("⚡ Demand", f"{grid.demand_mw:.1f} MW")
    
    with col3:
        st.metric("🔋 Generation", f"{grid.generation_mw:.1f} MW")
    
    with col4:
        status_emoji = "🔴" if grid.status == GridStatus.CRITICAL else "🟡" if grid.status == GridStatus.WARNING else "🟢"
        st.metric("Status", f"{status_emoji} {grid.status.value.upper()}")
    
    st.divider()
    
    # Visualization
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        fig = go.Figure(data=[
            go.Bar(name='Demand', x=['Load'], y=[grid.demand_mw], marker_color='#ff6b6b'),
            go.Bar(name='Generation', x=['Load'], y=[grid.generation_mw], marker_color='#51cf66'),
        ])
        fig.update_layout(height=250, showlegend=True, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=False)
    
    with col_graph2:
        fig = go.Figure(data=[
            go.Pie(labels=['Renewable', 'Traditional'],
                   values=[grid.renewable_pct, 100-grid.renewable_pct],
                   marker=dict(colors=['#51cf66', '#a5d6ff']),
                   hole=0.4)
        ])
        fig.update_layout(height=250, showlegend=True, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=False)
    
    st.divider()
    
    # Thermostat Info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Devices", len(thermostats))
    with col2:
        total_capacity = sum(t.capacity_mw for t in thermostats)
        st.metric("Capacity", f"{total_capacity:.1f} MW")
    with col3:
        avg_flex = sum(t.flexibility for t in thermostats) / len(thermostats)
        st.metric("Avg Flexibility", f"{avg_flex:.2f}")
    
    st.divider()
    
    # Run DR Agent
    col_button, col_info = st.columns([1, 3])
    
    with col_button:
        run_agent = st.button("▶️ Run DR Agent", use_container_width=False, key="run_dr")
    
    with col_info:
        st.caption("Click to execute demand response analysis")
    
    if run_agent:
        with st.spinner("Running agent..."):
            try:
                controller = DRController()
                for t in thermostats:
                    controller.register_thermostat(t)
                
                result = controller.run_dr(grid)
                actions = result.get('actions', [])
                analysis = result.get('analysis', '')
                
                # Show results
                st.success(f"✅ Analysis: {analysis}")
                
                if actions:
                    st.write(f"**{len(actions)} DR Actions Generated**")
                    total_reduction = sum(a.expected_reduction_mw for a in actions)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Expected Reduction:** {total_reduction:.2f} MW")
                    with col2:
                        impact = (total_reduction / grid.demand_mw * 100) if grid.demand_mw > 0 else 0
                        st.write(f"**Impact:** {impact:.1f}% of demand")
                    
                    # Show actions table
                    st.write("**Actions:**")
                    action_data = []
                    for a in actions[:10]:
                        action_data.append({
                            "Device": a.device_id,
                            "Action": a.action,
                            "Target (°C)": a.target_temp,
                            "Reduction (MW)": f"{a.expected_reduction_mw:.3f}"
                        })
                    st.dataframe(action_data, use_container_width=False, hide_index=True)
                    
                    if len(actions) > 10:
                        st.caption(f"... and {len(actions)-10} more")
                else:
                    st.info("✅ No DR actions needed - grid is stable")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.caption("Ensure GROQ_API_KEY is set in .env")


# ============ TAB 2: CREATE SCENARIO ============
with tab2:
    st.subheader("� Create New Scenario")
    st.caption("Design custom grid conditions and thermostat configurations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        scenario_name = st.text_input("Scenario Name", placeholder="e.g., Summer Heatwave")
        st.caption("📊 Demand Range: 200-1000 MW")
        demand = st.slider("Grid Demand (MW)", 200, 1000, 600, 50)
    
    with col2:
        st.caption("📊 Generation Range: 200-1000 MW")
        generation = st.slider("Generation (MW)", 200, 1000, 650, 50)
    
    col1, col2 = st.columns(2)
    with col1:
        st.caption("📊 Frequency Range: 58.5-61.5 Hz (Normal: 60 Hz)")
        frequency = st.slider("Grid Frequency (Hz)", 58.5, 61.5, 60.0, 0.05)
    
    with col2:
        st.caption("📊 Renewable Range: 0-100%")
        renewable_pct = st.slider("Renewable Generation %", 0, 100, 40)
    
    st.divider()
    
    # Simple device count slider
    st.caption("⚙️ Thermostat Configuration")
    num_devices = st.slider("Number of Controllable Devices", 3, 50, 10)
    
    st.divider()
    
    # Determine grid status
    imbalance = generation - demand
    if frequency < 59.5 or imbalance < -200:
        grid_status = GridStatus.CRITICAL
        status_text = "🔴 CRITICAL"
        status_color = "🔴"
    elif frequency < 59.9 or imbalance < -50:
        grid_status = GridStatus.WARNING
        status_text = "🟡 WARNING"
        status_color = "🟡"
    else:
        grid_status = GridStatus.NORMAL
        status_text = "🟢 NORMAL"
        status_color = "🟢"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Predicted Status", status_text)
    with col2:
        st.metric("Imbalance", f"{imbalance:.0f} MW", "Deficit" if imbalance < 0 else "Surplus")
    with col3:
        st.metric("Renewable %", f"{renewable_pct}%")
    
    st.divider()
    
    if st.button("✨ Create This Scenario", use_container_width=False):
        if not scenario_name:
            st.error("❌ Please enter a scenario name")
        else:
            with st.spinner("Creating scenario..."):
                # Create grid state
                capacity_mw = max(demand, generation) * 1.3
                
                grid = GridState(
                    timestamp=datetime.now(),
                    demand_mw=demand,
                    generation_mw=generation,
                    frequency_hz=frequency,
                    status=grid_status,
                    renewable_pct=renewable_pct,
                    capacity_mw=capacity_mw
                )
                
                # Create thermostats with varied properties
                thermostats = []
                for i in range(num_devices):
                    # Vary properties across device pool
                    current_temp = 20 + (i % 5) * 0.8  # 20-23.2°C
                    flexibility = 0.6 + (i / num_devices) * 0.35  # 0.6-0.95
                    capacity = 0.08 + (i % 10) * 0.02  # 0.08-0.26 MW
                    
                    thermostats.append(Thermostat(
                        device_id=f"TH_{i:04d}",
                        location=f"Zone_{chr(65 + (i % 26))}_{i // 26 + 1}",
                        current_temp=current_temp,
                        target_temp=22.0,
                        mode=ThermostatMode.COOLING if current_temp > 22 else ThermostatMode.HEATING,
                        capacity_mw=capacity,
                        flexibility=flexibility
                    ))
                
                # Save scenario
                custom_scenario = {
                    'name': scenario_name,
                    'grid': grid,
                    'thermostats': thermostats,
                    'description': f"Custom scenario - {status_text}"
                }
                
                st.session_state.custom_scenarios.append(custom_scenario)
                st.success(f"✅ Scenario '{scenario_name}' created successfully!")
                st.info(f"📊 Status: {status_text} | Devices: {num_devices} | Demand: {demand} MW")
                st.caption("Switch to 'Dashboard' tab to launch the DR Agent")
