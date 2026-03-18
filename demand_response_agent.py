"""
Demand Response Agent - Uses LangGraph + Groq LLM to manage thermostat load reduction
"""
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import json
import os

from models import Thermostat, GridState, DRAction


class DRState(TypedDict):
    """Agent state"""
    grid: GridState
    thermostats: List[Thermostat]
    actions: List[DRAction]
    analysis: str
    error: Optional[str]


class DemandResponseAgent:
    """
    Demand Response Agent that:
    1. Analyzes grid conditions
    2. Selects responsive thermostats
    3. Plans specific temperature adjustments
    4. Validates actions before execution
    """

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Set GROQ_API_KEY environment variable")
        
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            groq_api_key=api_key,
        )
        
        # Build workflow
        workflow = StateGraph(DRState)
        workflow.add_node("analyze", self.analyze_grid)
        workflow.add_node("select", self.select_thermostats)
        workflow.add_node("plan", self.plan_actions)
        workflow.add_node("validate", self.validate_actions)
        
        workflow.add_edge("analyze", "select")
        workflow.add_edge("select", "plan")
        workflow.add_edge("plan", "validate")
        workflow.add_edge("validate", END)
        workflow.set_entry_point("analyze")
        
        self.app = workflow.compile()

    def analyze_grid(self, state: DRState) -> DRState:
        """Analyze grid stress and need for DR"""
        grid = state["grid"]
        
        # HARD CHECK: Is DR actually needed?
        needs_dr = (
            grid.frequency_hz < 59.9 or  # Frequency dropping (WARNING or worse)
            grid.demand_surplus > 50     # Large demand surplus (>50 MW)
        )
        
        if not needs_dr:
            # Grid is stable - no DR needed
            state["analysis"] = f"Grid stable: {grid.frequency_hz:.2f}Hz, surplus {grid.demand_surplus:.1f}MW"
            state["thermostats"] = []  # Clear devices, skip rest of pipeline
            state["actions"] = []
            return state
        
        # Grid needs help - analyze details
        prompt = f"""Analyze this grid stress:
Status: {grid.status.value} (CRITICAL)
Demand: {grid.demand_mw:.1f} MW | Generation: {grid.generation_mw:.1f} MW
Frequency: {grid.frequency_hz:.2f} Hz (normal = 60 Hz, critical < 59.5)
Surplus Demand: {grid.demand_surplus:.1f} MW
Stress Level: {grid.stress_level:.0%}

This grid needs IMMEDIATE demand reduction!
Estimate the MW reduction needed: {min(grid.demand_surplus * 1.5, 200):.0f} MW

Return JSON with analysis:
{{"needed": true, "reason": "frequency dropping + high demand", "mw_to_reduce": 75}}"""
        
        messages = [
            SystemMessage(content="You're a grid operator. The grid is in CRISIS. Respond immediately!"),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        try:
            data = json.loads(response.content)
            state["analysis"] = data.get("reason", "Grid stabilization needed")
        except Exception as e:
            state["analysis"] = f"Grid stress detected: {grid.status.value}"
        
        return state

    def select_thermostats(self, state: DRState) -> DRState:
        """Select thermostats that can respond to DR"""
        # Skip if no DR needed (analysis already cleared devices)
        if not state["thermostats"]:
            return state
        
        thermostats = state["thermostats"]
        responsive = [t for t in thermostats if t.can_respond()]
        
        if not responsive:
            state["thermostats"] = []
            return state
        
        # Calculate how many devices we need
        demand_surplus = state["grid"].demand_surplus
        total_capacity = sum(t.capacity_mw for t in responsive)
        
        # Select by flexibility score first, then capacity
        sorted_devices = sorted(responsive, key=lambda t: (t.flexibility, t.capacity_mw), reverse=True)
        
        # Take top devices needed to cover ~80% of demand surplus
        capacity_needed = demand_surplus * 0.8
        cumulative = 0
        selected = []
        for device in sorted_devices:
            selected.append(device)
            cumulative += device.capacity_mw
            if cumulative >= capacity_needed:
                break
        
        # Always select at least 3 devices for distributed response
        if len(selected) < 3 and len(sorted_devices) >= 3:
            selected = sorted_devices[:3]
        
        state["thermostats"] = selected
        return state

    def plan_actions(self, state: DRState) -> DRState:
        """Generate specific temperature adjustment actions"""
        thermostats = state["thermostats"]
        
        if not thermostats:
            return state
        
        grid = state["grid"]
        actions = []
        
        # Calculate required reduction per device
        total_demand_surplus = grid.demand_surplus
        num_devices = len(thermostats)
        
        # Each device should reduce by roughly equal share
        target_reduction_per_device = max(total_demand_surplus / num_devices, 0.5)
        
        # Temperature reduction strategy
        # Frequency < 59.5: CRITICAL - reduce by 3-4°C
        # Frequency 59.5-59.9: WARNING - reduce by 2-3°C
        # Frequency >= 59.9: NORMAL - shouldn't happen (we filtered these out)
        
        if grid.frequency_hz < 59.5:
            temp_reduction = 4.0  # Emergency
            priority = 3  # Critical priority
        elif grid.frequency_hz < 59.9:
            temp_reduction = 2.5  # Warning
            priority = 2  # High priority
        else:
            temp_reduction = 2.0  # Low (shouldn't reach here)
            priority = 1  # Medium
        
        # Create action for each thermostat
        for thermostat in thermostats:
            new_target = max(16.0, thermostat.target_temp - temp_reduction)  # Min 16°C
            
            action = DRAction(
                device_id=thermostat.device_id,
                action="reduce_temp",
                target_temp=round(new_target, 1),
                expected_reduction_mw=target_reduction_per_device,
                priority=priority,
            )
            actions.append(action)
        
        state["actions"] = actions
        return state

    def validate_actions(self, state: DRState) -> DRState:
        """Validate actions are safe"""
        valid = []
        for action in state["actions"]:
            # Safety checks
            if 16 <= action.target_temp <= 28:  # reasonable temperature range
                if action.expected_reduction_mw > 0:  # must reduce load
                    valid.append(action)
        
        state["actions"] = valid
        return state

    def execute(self, grid: GridState, thermostats: List[Thermostat]) -> DRState:
        """Run the agent"""
        initial_state: DRState = {
            "grid": grid,
            "thermostats": thermostats,
            "actions": [],
            "analysis": "",
            "error": None,
        }
        return self.app.invoke(initial_state)
