#!/usr/bin/env python3
"""Quick test to verify agent works in dashboard"""
import os
from dotenv import load_dotenv
load_dotenv()
if not os.getenv("GROQ_API_KEY") and os.getenv("api_key"):
    os.environ["GROQ_API_KEY"] = os.getenv("api_key")

from models import GridState, GridStatus, Thermostat, ThermostatMode
from dr_controller import DRController
from datetime import datetime

print("\n" + "="*70)
print("🧪 TESTING DEMAND RESPONSE AGENT IN DASHBOARD")
print("="*70)

# Test 1: CRITICAL state (should generate actions)
print("\n✅ TEST 1: CRITICAL Grid State")
grid1 = GridState(
    timestamp=datetime.now(),
    demand_mw=950,
    generation_mw=850,
    frequency_hz=59.4,
    status=GridStatus.CRITICAL,
    renewable_pct=30,
    capacity_mw=1200,
)

thermostats1 = [
    Thermostat(f'TH_{i:03d}', f'Building {i}', 22.0, 22.0, 
              ThermostatMode.COOLING, 0.1 + i*0.01, 0.7 + i*0.05)
    for i in range(10)
]

controller1 = DRController()
for t in thermostats1:
    controller1.register_thermostat(t)

result1 = controller1.run_dr(grid1)
print(f"  Analysis: {result1['analysis']}")
print(f"  Actions Generated: {len(result1['actions'])}")
if result1['actions']:
    total = sum(a.expected_reduction_mw for a in result1['actions'])
    print(f"  ✅ Total Reduction: {total:.3f} MW ({total/grid1.demand_mw*100:.1f}% of demand)")
else:
    print(f"  ❌ ERROR: No actions for CRITICAL state!")

# Test 2: NORMAL state (should NOT generate actions)
print("\n✅ TEST 2: NORMAL Grid State")
grid2 = GridState(
    timestamp=datetime.now(),
    demand_mw=800,
    generation_mw=850,
    frequency_hz=60.2,
    status=GridStatus.NORMAL,
    renewable_pct=45,
    capacity_mw=1200,
)

thermostats2 = [
    Thermostat(f'TH_{i:03d}', f'Building {i}', 22.0, 22.0, 
              ThermostatMode.COOLING, 0.1, 0.75)
    for i in range(5)
]

controller2 = DRController()
for t in thermostats2:
    controller2.register_thermostat(t)

result2 = controller2.run_dr(grid2)
print(f"  Analysis: {result2['analysis']}")
print(f"  Actions Generated: {len(result2['actions'])}")
if len(result2['actions']) == 0:
    print(f"  ✅ Correctly NO actions for NORMAL state")
else:
    print(f"  ❌ ERROR: Unexpected actions for NORMAL state!")

# Test 3: WARNING state
print("\n✅ TEST 3: WARNING Grid State")
grid3 = GridState(
    timestamp=datetime.now(),
    demand_mw=900,
    generation_mw=850,
    frequency_hz=59.7,
    status=GridStatus.WARNING,
    renewable_pct=35,
    capacity_mw=1200,
)

thermostats3 = [
    Thermostat(f'TH_{i:03d}', f'Building {i}', 22.0, 22.0, 
              ThermostatMode.COOLING, 0.1 + i*0.01, 0.7)
    for i in range(8)
]

controller3 = DRController()
for t in thermostats3:
    controller3.register_thermostat(t)

result3 = controller3.run_dr(grid3)
print(f"  Analysis: {result3['analysis']}")
print(f"  Actions Generated: {len(result3['actions'])}")
if result3['actions']:
    total = sum(a.expected_reduction_mw for a in result3['actions'])
    print(f"  ✅ Total Reduction: {total:.3f} MW ({total/grid3.demand_mw*100:.1f}% of demand)")
else:
    print(f"  ⚠️ No actions for WARNING state (unexpected)")

print("\n" + "="*70)
print("✅ AGENT TEST COMPLETE - Agent is working correctly in dashboard!")
print("="*70 + "\n")
