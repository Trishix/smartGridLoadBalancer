"""
Simple example of Demand Response Agent in action
"""
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Map api_key to GROQ_API_KEY if needed
if not os.getenv("GROQ_API_KEY") and os.getenv("api_key"):
    os.environ["GROQ_API_KEY"] = os.getenv("api_key")

from models import Thermostat, ThermostatMode, GridState, GridStatus
from dr_controller import DRController


def example_normal_conditions():
    """Example 1: Normal grid conditions"""
    print("\n" + "="*60)
    print("Example 1: Normal Grid Conditions")
    print("="*60)
    
    # Create controller
    controller = DRController()
    
    # Register 5 thermostats
    for i in range(5):
        t = Thermostat(
            device_id=f"TH_{i:03d}",
            location=f"Building {i+1}",
            current_temp=22.0 + i*0.2,
            target_temp=22.0,
            mode=ThermostatMode.COOLING,
            capacity_mw=0.1 + i*0.02,  # 0.1 to 0.18 MW
            flexibility=0.7 + i*0.05,   # 0.7 to 0.9
        )
        controller.register_thermostat(t)
    
    # Create grid state
    grid = GridState(
        timestamp=datetime.now(),
        demand_mw=800,
        generation_mw=850,
        frequency_hz=60.0,
        status=GridStatus.NORMAL,
        renewable_pct=45,
        capacity_mw=1000,
    )
    
    print(f"Grid: {grid.status.value.upper()}")
    print(f"  Demand: {grid.demand_mw} MW")
    print(f"  Generation: {grid.generation_mw} MW")
    print(f"  Frequency: {grid.frequency_hz} Hz")
    
    # Run DR
    result = controller.run_dr(grid)
    print(f"\nDR Run Results:")
    print(f"  Analysis: {result['analysis']}")
    print(f"  Actions Generated: {len(result['actions'])}")
    print(f"  Total Reduction: {sum(a.expected_reduction_mw for a in result['actions']):.2f} MW")


def example_peak_stress():
    """Example 2: Peak demand stress - DR is needed"""
    print("\n" + "="*60)
    print("Example 2: Peak Demand Stress (DR Activated)")
    print("="*60)
    
    controller = DRController()
    
    # Register 10 thermostats
    for i in range(10):
        t = Thermostat(
            device_id=f"TH_{i:03d}",
            location=f"Building {i+1}",
            current_temp=23.0,
            target_temp=23.0,
            mode=ThermostatMode.COOLING,
            capacity_mw=0.15,
            flexibility=0.8,
        )
        controller.register_thermostat(t)
    
    # Peak demand: generation can't keep up
    grid = GridState(
        timestamp=datetime.now(),
        demand_mw=950,      # High demand
        generation_mw=880,  # Supply gap
        frequency_hz=59.7,  # Dropping
        status=GridStatus.WARNING,
        renewable_pct=30,
        capacity_mw=1000,
    )
    
    print(f"Grid: {grid.status.value.upper()}")
    print(f"  Demand: {grid.demand_mw} MW")
    print(f"  Generation: {grid.generation_mw} MW")
    print(f"  Surplus: {grid.demand_surplus} MW")
    print(f"  Frequency: {grid.frequency_hz} Hz (FALLING)")
    print(f"  Stress: {grid.stress_level:.0%}")
    
    # Run DR
    result = controller.run_dr(grid)
    print(f"\nDR Run Results:")
    print(f"  Analysis: {result['analysis']}")
    print(f"  Actions: {len(result['actions'])}")
    if result['actions']:
        for action in result['actions']:
            print(f"    - {action.device_id}: {action.action} to {action.target_temp}°C")
    print(f"  Total Reduction: {sum(a.expected_reduction_mw for a in result['actions']):.2f} MW")
    
    # Apply actions
    controller.apply_all_actions(result['actions'])
    print(f"\nActions Applied ✓")
    
    # Show updated status
    print(f"\nDevice Status After DR:")
    for status in controller.device_status()[:3]:
        print(f"  {status['device_id']}: {status['target']} (from 23.0°C)")


def example_emergency():
    """Example 3: Emergency - frequency critical"""
    print("\n" + "="*60)
    print("Example 3: Emergency - Frequency Critical")
    print("="*60)
    
    controller = DRController()
    
    # Register 20 thermostats
    for i in range(20):
        t = Thermostat(
            device_id=f"TH_{i:03d}",
            location=f"Building {i+1}",
            current_temp=22.5,
            target_temp=22.5,
            mode=ThermostatMode.COOLING,
            capacity_mw=0.1,
            flexibility=0.85,
        )
        controller.register_thermostat(t)
    
    # Emergency: severe generation shortfall
    grid = GridState(
        timestamp=datetime.now(),
        demand_mw=980,      # Very high
        generation_mw=850,  # Large gap
        frequency_hz=59.4,  # Critical
        status=GridStatus.CRITICAL,
        renewable_pct=25,
        capacity_mw=1000,
    )
    
    print(f"Grid: {grid.status.value.upper()}")
    print(f"  Demand: {grid.demand_mw} MW")
    print(f"  Generation: {grid.generation_mw} MW")
    print(f"  Surplus: {grid.demand_surplus} MW ⚠️")
    print(f"  Frequency: {grid.frequency_hz} Hz 🚨")
    print(f"  Stress: {grid.stress_level:.0%}")
    
    # Run DR at full strength
    result = controller.run_dr(grid)
    print(f"\nDR Run Results:")
    print(f"  Analysis: {result['analysis']}")
    print(f"  Actions: {len(result['actions'])}")
    total_reduction = sum(a.expected_reduction_mw for a in result['actions'])
    print(f"  Total Reduction: {total_reduction:.2f} MW")
    print(f"  Impact: Grid can now balance with {grid.generation_mw + total_reduction:.0f} MW available")
    
    # Apply all actions
    if result['actions']:
        controller.apply_all_actions(result['actions'])
        print(f"  Status: ACTIVATED ✓")


def main():
    print("\n╔" + "="*58 + "╗")
    print("║" + " "*15 + "DEMAND RESPONSE AGENT EXAMPLES" + " "*13 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        example_normal_conditions()
        example_peak_stress()
        example_emergency()
        
        print("\n" + "="*60)
        print("✓ All examples completed successfully")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. GROQ_API_KEY is set in .env")
        print("  2. pip install -r requirements.txt")


if __name__ == "__main__":
    main()
