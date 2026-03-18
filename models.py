"""
Core models for Demand Response Agent
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class GridStatus(Enum):
    """Grid status levels"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


class ThermostatMode(Enum):
    """Thermostat operation modes"""
    HEATING = "heating"
    COOLING = "cooling"
    OFF = "off"


@dataclass
class Thermostat:
    """Smart Thermostat device"""
    device_id: str
    location: str
    current_temp: float
    target_temp: float
    mode: ThermostatMode
    capacity_mw: float  # Load reduction capacity
    flexibility: float  # 0-1: how easily it responds (0.7=good, 0.9=excellent)
    is_online: bool = True
    
    def can_respond(self) -> bool:
        """Check if thermostat can participate in DR"""
        return (
            self.is_online 
            and self.capacity_mw > 0
            and self.mode in [ThermostatMode.HEATING, ThermostatMode.COOLING]
        )


@dataclass
class GridState:
    """Current grid state"""
    timestamp: datetime
    demand_mw: float
    generation_mw: float
    frequency_hz: float
    status: GridStatus
    renewable_pct: float
    capacity_mw: float
    
    @property
    def demand_surplus(self) -> float:
        """MW of excess demand over generation"""
        return max(0, self.demand_mw - self.generation_mw)
    
    @property
    def stress_level(self) -> float:
        """0-1 scale of grid stress"""
        if self.capacity_mw == 0:
            return 0.0
        return min(1.0, self.demand_surplus / self.capacity_mw)


@dataclass
class DRAction:
    """Demand Response action"""
    device_id: str
    action: str  # "reduce_temp", "increase_temp"
    target_temp: float
    duration_min: int = 30
    priority: int = 1
    expected_reduction_mw: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
