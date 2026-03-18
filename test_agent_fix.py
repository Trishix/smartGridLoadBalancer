#!/usr/bin/env python3
"""Test the fixed DR agent"""
import os
from dotenv import load_dotenv
load_dotenv()
if not os.getenv("GROQ_API_KEY") and os.getenv("api_key"):
    os.environ["GROQ_API_KEY"] = os.getenv("api_key")

from models import GridState, GridStatus, Thermostat, ThermostatMode
from dr_controller import DRController
from datetime import datetime

print("Testing Fixed DR Agent\n" + "="*50)

# Test 1: WARNING scenario (should trigger DR)
print("\n📊 Test 1: WARNING - Frequency 59.71 Hz, 70 MW surplus")
grid1 = GridState(
    timestamp=datetime.now(),
    demand_mw=950,
    generation_mw=880,
    frequency_hz=59.71,  # WARNING
    status=GridStatus.WARNING,
    renewable_pct=30,
    capacity_mw=1000,
)

thermostats1 = [
    Thermostat(f"TH_{i:03d}", f"Building {i}", 22 + i*0.1, 22, 
              ThermostatMode.COOLING, 0.1 + i*0.02, 0.7 + i*0.05)
    for i in range(8)
]

print(f"Grid Status: {grid1.status.value}")
print(f"Frequency: {grid1.frequency_hz} Hz (needs DR if < 59.9)")
print(f"Demand Surplus: {grid1.demand_surplus} MW")

controller1 = DRController()
for t in thermostats1:
    controller1.register_thermostat(t)

result1 = controller1.run_dr(grid1)
print(f"\n✅ Result:")
print(f"Analysis: {result1['analysis']}")
print(f"Actions Generated: {len(result1['actions'])}")
if result1['actions']:
    for action in result1['actions'][:3]:
        print(f"  • {action.device_id}: {action.target_temp}°C (-{22-action.target_temp:.1f}), reduction {action.expected_reduction_mw:.2f}MW")
else:
    print("  ❌ NO ACTIONS (THIS IS THE BUG!)")

# Test 2: CRITICAL scenario (should trigger DR)
print("\n" + "="*50)
print("\n📊 Test 2: CRITICAL - Frequency 59.4 Hz, 130 MW surplus")
grid2 = GridState(
    timestamp=datetime.now(),
    demand_mw=980,
    generation_mw=850,
    frequency_hz=59.4,  # CRITICAL
    status=GridStatus.CRITICAL,
    renewable_pct=25,
    capacity_mw=1000,
)

thermostats2 = [
    Thermostat(f"TH_{i:03d}", f"Building {i}", 22 + i*0.1, 22, 
              ThermostatMode.COOLING, 0.15 + i*0.02, 0.7 + i*0.05)
    for i in range(15)
]

print(f"Grid Status: {grid2.status.value}")
print(f"Frequency: {grid2.frequency_hz} Hz (critical if < 59.5)")
print(f"Demand Surplus: {grid2.demand_surplus} MW")

controller2 = DRController()
for t in thermostats2:
    controller2.register_thermostat(t)

result2 = controller2.run_dr(grid2)
print(f"\n✅ Result:")
print(f"Analysis: {result2['analysis']}")
print(f"Actions Generated: {len(result2['actions'])}")
if result2['actions']:
    total_reduction = sum(a.expected_reduction_mw for a in result2['actions'])
    print(f"Total Reduction: {total_reduction:.2f} MW")
    for action in result2['actions'][:3]:
        print(f"  • {action.device_id}: {action.target_temp}°C (-{22-action.target_temp:.1f}), reduction {action.expected_reduction_mw:.2f}MW")
else:
    print("  ❌ NO ACTIONS (THIS IS THE BUG!)")

# Test 3: NORMAL scenario (should NOT trigger DR)
print("\n" + "="*50)
print("\n📊 Test 3: NORMAL - Frequency 60.0 Hz, balanced")
grid3 = GridState(
    timestamp=datetime.now(),
    demand_mw=800,
    generation_mw=850,
    frequency_hz=60.0,  # NORMAL
    status=GridStatus.NORMAL,
    renewable_pct=45,
    capacity_mw=1000,
)

thermostats3 = [
    Thermostat(f"TH_{i:03d}", f"Building {i}", 22, 22, 
              ThermostatMode.COOLING, 0.1, 0.75)
    for i in range(5)
]

print(f"Grid Status: {grid3.status.value}")
print(f"Frequency: {grid3.frequency_hz} Hz (stable)")
print(f"Demand Surplus: {grid3.demand_surplus} MW")

controller3 = DRController()
for t in thermostats3:
    controller3.register_thermostat(t)

result3 = controller3.run_dr(grid3)
print(f"\n✅ Result:")
print(f"Analysis: {result3['analysis']}")
print(f"Actions Generated: {len(result3['actions'])}")
if result3['actions']:
    print("  ❌ UNEXPECTED ACTIONS (grid is stable!)")
else:
    print("  ✅ Correctly no actions (grid is stable)")

print("\n" + "="*50)
print("\nTest Complete!")
