"""
DR Controller - Manages thermostats and runs the agent
"""
from typing import List, Dict
from datetime import datetime
from models import Thermostat, GridState, DRAction
from demand_response_agent import DemandResponseAgent


class DRController:
    """Manages demand response operations"""

    def __init__(self):
        self.agent = DemandResponseAgent()
        self.thermostats: Dict[str, Thermostat] = {}
        self.action_history: List[Dict] = []

    def register_thermostat(self, thermostat: Thermostat):
        """Add a thermostat to the pool"""
        self.thermostats[thermostat.device_id] = thermostat

    def register_thermostats(self, thermostats: List[Thermostat]):
        """Add multiple thermostats"""
        for t in thermostats:
            self.register_thermostat(t)

    def run_dr(self, grid: GridState) -> Dict:
        """Run demand response and return actions"""
        devices = list(self.thermostats.values())
        
        # Run agent
        result = self.agent.execute(grid, devices)
        
        # Track results
        actions = result.get("actions", [])
        history_entry = {
            "timestamp": datetime.now(),
            "grid_status": grid.status.value,
            "actions_count": len(actions),
            "total_reduction_mw": sum(a.expected_reduction_mw for a in actions),
            "analysis": result.get("analysis", ""),
        }
        self.action_history.append(history_entry)
        
        return {
            "actions": actions,
            "analysis": result.get("analysis"),
            "error": result.get("error"),
        }

    def apply_action(self, action: DRAction):
        """Apply DR action to a thermostat"""
        thermostat = self.thermostats.get(action.device_id)
        if not thermostat:
            return False
        
        if action.action == "reduce_temp":
            thermostat.target_temp = action.target_temp
        
        return True

    def apply_all_actions(self, actions: List[DRAction]):
        """Apply all DR actions"""
        for action in actions:
            self.apply_action(action)

    def get_summary(self) -> Dict:
        """Get summary of current state"""
        return {
            "registered_devices": len(self.thermostats),
            "online_devices": sum(1 for t in self.thermostats.values() if t.is_online),
            "recent_actions": len(self.action_history),
            "total_reduction_mw": sum(
                h.get("total_reduction_mw", 0) for h in self.action_history[-10:]
            ),
        }

    def device_status(self) -> List[Dict]:
        """Get status of all thermostats"""
        return [
            {
                "device_id": t.device_id,
                "location": t.location,
                "current": f"{t.current_temp}°C",
                "target": f"{t.target_temp}°C",
                "mode": t.mode.value,
                "online": t.is_online,
                "capacity_mw": t.capacity_mw,
            }
            for t in self.thermostats.values()
        ]
