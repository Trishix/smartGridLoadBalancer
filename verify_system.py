#!/usr/bin/env python3
"""
Comprehensive test of Smart Grid Load-Balancer with Groq API
Validates all modules and functionality
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime

print("=" * 80)
print("SMART GRID LOAD-BALANCER - COMPREHENSIVE VALIDATION TEST")
print("=" * 80)

# ============================================================================
# STEP 1: Check environment
# ============================================================================
print("\n[1/6] Checking Environment Configuration...")
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ GROQ_API_KEY not found in .env file")
    sys.exit(1)

print(f"✓ GROQ_API_KEY configured: {api_key[:20]}...{api_key[-10:]}")

# ============================================================================
# STEP 2: Test Groq API Connection
# ============================================================================
print("\n[2/6] Testing Groq API Connection...")
try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage
    
    llm = ChatGroq(
        model="llama-3.1-70b-versatile",
        temperature=0.3,
        groq_api_key=api_key,
        max_tokens=100,
    )
    
    response = llm.invoke([HumanMessage(content="Say 'Ready' in one word.")])
    print(f"✓ Groq API connection successful")
    print(f"✓ LLM Response: '{response.content.strip()}'")
    
except Exception as e:
    print(f"❌ Groq API Connection Failed: {e}")
    sys.exit(1)

# ============================================================================
# STEP 3: Test Core Models
# ============================================================================
print("\n[3/6] Testing Core Models...")
try:
    from models import (
        GridState, GridStatus, SmartThermostat, ThermostatMode,
        DemandResponseAction, StorageTriggerAction
    )
    
    # Create test objects
    grid = GridState(
        timestamp=datetime.now(),
        total_demand_mw=950.0,
        total_generation_mw=880.0,
        grid_frequency_hz=59.8,
        status=GridStatus.WARNING,
        renewable_generation_pct=40,
        storage_available_mw=120.0,
        storage_capacity_mw=200.0,
        peak_load_threshold_mw=1100.0,
    )
    
    thermostat = SmartThermostat(
        device_id="TEST_001",
        location="Test Building",
        current_temperature=22.0,
        target_temperature=22.0,
        mode=ThermostatMode.COOLING,
        max_reduction_capacity=0.15,
        flexibility_score=0.85,
    )
    
    print(f"✓ GridState created: {grid.status.value} status, {grid.demand_stress_level:.1%} stress")
    print(f"✓ SmartThermostat created: {thermostat.device_id}, responsive={thermostat.can_accept_demand_response()}")
    
except Exception as e:
    print(f"❌ Models Test Failed: {e}")
    sys.exit(1)

# ============================================================================
# STEP 4: Test Demand Response Agent
# ============================================================================
print("\n[4/6] Testing Demand Response Agent...")
try:
    from demand_response_agent import DemandResponseAgent
    
    dr_agent = DemandResponseAgent(groq_api_key=api_key)
    print(f"✓ DemandResponseAgent initialized")
    print(f"✓ Workflow compiled with {len(dr_agent.app.get_graph().nodes)} nodes")
    
    # Test with simple scenario
    thermostats = [thermostat]
    dr_result = dr_agent.run(grid, thermostats)
    
    actions_count = len(dr_result.get("actions", []))
    print(f"✓ DR Agent executed: generated {actions_count} actions")
    if dr_result.get("analysis"):
        print(f"  Analysis: {dr_result['analysis'][:80]}...")
    
except Exception as e:
    print(f"❌ Demand Response Agent Test Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 5: Test Storage Trigger Agent
# ============================================================================
print("\n[5/6] Testing Storage Trigger Agent...")
try:
    from storage_trigger_agent import StorageTriggerAgent
    
    storage_agent = StorageTriggerAgent(groq_api_key=api_key)
    print(f"✓ StorageTriggerAgent initialized")
    print(f"✓ Workflow compiled with {len(storage_agent.app.get_graph().nodes)} nodes")
    
    # Test with peak pricing scenario
    spot_price = 145.0
    storage_result = storage_agent.run(grid, spot_price)
    
    decision = storage_result.get("decision", "UNKNOWN")
    action = storage_result.get("current_action")
    print(f"✓ Storage Agent executed: decision={decision}")
    if action:
        print(f"  Action: {action.action_type} at {action.intensity:.0%} intensity")
    
except Exception as e:
    print(f"❌ Storage Trigger Agent Test Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 6: Test Grid Manager (Full System)
# ============================================================================
print("\n[6/6] Testing Smart Grid Manager (Full System)...")
try:
    from grid_manager import SmartGridManager
    
    manager = SmartGridManager(groq_api_key=api_key)
    print(f"✓ SmartGridManager initialized")
    
    # Register thermostats
    manager.register_thermostat(thermostat)
    for i in range(1, 4):
        t = SmartThermostat(
            device_id=f"THERMO_{i:03d}",
            location=f"Building {i+1}",
            current_temperature=22.0,
            target_temperature=22.0,
            mode=ThermostatMode.COOLING,
            max_reduction_capacity=0.12,
            flexibility_score=0.75,
        )
        manager.register_thermostat(t)
    
    print(f"✓ Registered {len(manager.thermostats)} thermostats")
    
    # Make grid decision
    decision = manager.make_grid_decision(grid, spot_price=95.0)
    
    print(f"✓ Grid decision made:")
    print(f"  - DR Actions: {len(decision.demand_response_actions)}")
    print(f"  - Load Reduction: {decision.total_load_reduction_mw:.2f} MW")
    print(f"  - Storage Action: {decision.storage_action.action_type if decision.storage_action else 'None'}")
    print(f"  - Confidence: {decision.confidence_score:.1%}")
    
    # Execute decision
    results = manager.execute_decision(decision)
    print(f"✓ Decision executed:")
    print(f"  - DR actions sent: {results['dr_actions_sent']}")
    print(f"  - Failed: {results['dr_failed']}")
    print(f"  - Storage action sent: {results['storage_action_sent']}")
    
except Exception as e:
    print(f"❌ Grid Manager Test Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# SUCCESS
# ============================================================================
print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED - SYSTEM IS FULLY OPERATIONAL")
print("=" * 80)
print("\nSystem Status:")
print("  ✓ Environment configured")
print("  ✓ Groq API connected")
print("  ✓ Core models working")
print("  ✓ Demand Response Agent functional")
print("  ✓ Storage Trigger Agent functional")
print("  ✓ Grid Manager orchestrating both agents")
print("\nYou can now run: python main.py")
print("=" * 80)
