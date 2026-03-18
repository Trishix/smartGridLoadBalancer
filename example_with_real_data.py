"""
Demand Response Agent with Real Kaggle Smart Grid Data
"""
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
if not os.getenv("GROQ_API_KEY") and os.getenv("api_key"):
    os.environ["GROQ_API_KEY"] = os.getenv("api_key")

from models import Thermostat, ThermostatMode, GridState, GridStatus
from dr_controller import DRController
from data_loader import SmartGridDataLoader


def run_dr_with_real_data():
    """Run Demand Response Agent with real smart grid data"""
    print("\n" + "="*70)
    print("DEMAND RESPONSE AGENT - REAL KAGGLE SMART GRID DATA")
    print("="*70)
    
    # Load real data
    loader = SmartGridDataLoader()
    loader.get_data_info()
    
    # Get scenarios from dataset
    num_scenarios = 3
    scenarios = loader.get_dataset_scenarios(samples=num_scenarios)
    
    for idx, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*70}")
        print(f"SCENARIO {idx}: {scenario['description']}")
        print(f"{'='*70}")
        
        grid = scenario['grid']
        thermostats = scenario['thermostats']
        
        # Create FRESH controller for this scenario (not reused!)
        controller = DRController()
        
        # Register thermostats for THIS scenario only
        for t in thermostats:
            controller.register_thermostat(t)
        
        # Display grid conditions
        print(f"\n📊 GRID CONDITIONS:")
        print(f"  Status: {grid.status.value.upper()}")
        print(f"  Demand: {grid.demand_mw:.3f} MW")
        print(f"  Generation: {grid.generation_mw:.3f} MW")
        print(f"  Surplus: {grid.demand_surplus:.3f} MW")
        print(f"  Frequency: {grid.frequency_hz:.3f} Hz")
        print(f"  Stress Level: {grid.stress_level:.1%}")
        print(f"  Renewable: {grid.renewable_pct:.1f}%")
        
        # Display thermostat pool
        print(f"\n🌡️  THERMOSTAT POOL ({len(thermostats)} devices):")
        total_capacity = sum(t.capacity_mw for t in thermostats)
        total_flexibility = sum(t.flexibility for t in thermostats) / len(thermostats)
        print(f"  Total Capacity: {total_capacity:.3f} MW")
        print(f"  Average Flexibility: {total_flexibility:.2f}")
        for t in thermostats[:3]:
            print(f"    • {t.device_id} ({t.location}): {t.current_temp}°C → {t.target_temp}°C")
            print(f"      Capacity: {t.capacity_mw:.3f} MW | Flexibility: {t.flexibility:.2f} | Mode: {t.mode.value}")
        if len(thermostats) > 3:
            print(f"    ... and {len(thermostats) - 3} more")
        
        # Run DR Agent
        print(f"\n⚡ RUNNING DEMAND RESPONSE AGENT...")
        try:
            result = controller.run_dr(grid)
            
            print(f"\n✅ AGENT ANALYSIS:")
            print(f"  {result['analysis']}")
            
            print(f"\n📋 DR ACTIONS:")
            print(f"  Actions Generated: {len(result['actions'])}")
            
            if result['actions']:
                total_reduction = sum(a.expected_reduction_mw for a in result['actions'])
                print(f"  Expected Reduction: {total_reduction:.4f} MW")
                print(f"  Impact: {(total_reduction / grid.demand_mw * 100):.2f}% of demand" if grid.demand_mw > 0 else "  Impact: N/A (no demand)")
                
                print(f"\n  Selected Devices:")
                for action in result['actions'][:5]:
                    print(f"    • {action.device_id}")
                    print(f"      Action: {action.action}")
                    print(f"      Target: {action.target_temp}°C")
                    print(f"      Expected Reduction: {action.expected_reduction_mw:.4f} MW")
                
                if len(result['actions']) > 5:
                    print(f"    ... and {len(result['actions']) - 5} more devices")
                
                # Apply actions
                print(f"\n📌 Applying actions to thermostats...")
                controller.apply_all_actions(result['actions'])
                print(f"  ✓ All actions applied")
            else:
                print(f"  No actions needed - grid is stable")
        
        except Exception as e:
            print(f"  ❌ Error running agent: {e}")
            print(f"     Make sure GROQ_API_KEY is set and dependencies are installed")
    
    # Final summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    if controller:
        summary = controller.get_summary()
        print(f"\nRegistered Devices: {summary['registered_devices']}")
        print(f"Recent Actions: {summary['recent_actions']}")
        print(f"Total Reduction: {summary['total_reduction_mw']:.4f} MW")
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    try:
        run_dr_with_real_data()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
