"""
Load real smart grid data from Kaggle dataset
"""
import pandas as pd
import kagglehub
from datetime import datetime
from pathlib import Path
from models import Thermostat, ThermostatMode, GridState, GridStatus


class SmartGridDataLoader:
    """Load and process real smart grid data from Kaggle"""
    
    def __init__(self):
        """Download and cache the dataset"""
        self.dataset_path = kagglehub.dataset_download(
            "ziya07/smart-grid-real-time-load-monitoring-dataset"
        )
        self.csv_file = Path(self.dataset_path) / "smart_grid_dataset.csv"
        self.df = None
    
    def load_data(self):
        """Load CSV into DataFrame"""
        if self.df is None:
            self.df = pd.read_csv(self.csv_file)
            print(f"Loaded {len(self.df)} records from dataset")
        return self.df
    
    def get_data_info(self):
        """Display dataset structure"""
        df = self.load_data()
        print("\n📊 Dataset Info:")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {list(df.columns)}")
        print(f"\n  Sample row:")
        print(f"  {df.iloc[0]}\n")
    
    def create_grid_state_from_row(self, row):
        """Convert CSV row to GridState"""
        # Map dataset columns to grid metrics
        demand_kw = float(row.get('Power Consumption (kW)', 0))
        solar_kw = float(row.get('Solar Power (kW)', 0))
        wind_kw = float(row.get('Wind Power (kW)', 0))
        grid_supply_kw = float(row.get('Grid Supply (kW)', 0))
        
        # Calculate generation (renewable + grid supply)
        generation_kw = solar_kw + wind_kw + grid_supply_kw
        
        # SCALE UP to realistic grid level (this dataset is residential, we're simulating regional grid)
        # Scale factor: 100,000 to convert residential kW to regional MW
        scale_factor = 100000
        demand_mw = (demand_kw * scale_factor) / 1000
        generation_mw = (generation_kw * scale_factor) / 1000
        
        # Calculate renewable percentage
        total_gen = solar_kw + wind_kw + grid_supply_kw
        renewable_pct = (solar_kw + wind_kw) / total_gen * 100 if total_gen > 0 else 0
        
        # Derive frequency from power factor and voltage fluctuation
        voltage_fluctuation = float(row.get('Voltage Fluctuation (%)', 0))
        power_factor = float(row.get('Power Factor', 0.95))
        
        # Frequency: 60 Hz nominal, varies with load/generation balance
        frequency = 60 - (voltage_fluctuation * 0.1) - (1 - power_factor) * 2
        frequency = max(58.5, min(61.5, frequency))
        
        # Determine status based on frequency and load balance
        load_balance = abs(demand_mw - generation_mw)
        if frequency < 59.5 or load_balance > 500:
            status = GridStatus.CRITICAL
        elif frequency < 59.9 or load_balance > 200:
            status = GridStatus.WARNING
        else:
            status = GridStatus.NORMAL
        
        return GridState(
            timestamp=datetime.now(),
            demand_mw=demand_mw,
            generation_mw=generation_mw,
            frequency_hz=frequency,
            status=status,
            renewable_pct=min(100, renewable_pct),
            capacity_mw=10000,  # Increased capacity
        )
    
    def create_thermostats(self, count=10):
        """Generate synthetic thermostats based on dataset"""
        df = self.load_data()
        thermostats = []
        
        for i in range(count):
            # Use dataset rows to seed thermostat parameters
            row_idx = (i * len(df)) // count
            row = df.iloc[row_idx]
            
            # Use ambient temperature from dataset
            ambient_temp = float(row.get('Temperature (°C)', 20))
            base_temp = 20 + (i % 5)
            current_temp = ambient_temp + (i % 3) - 1
            
            # Scale capacity based on power consumption in dataset
            # Scale factor: 100,000 (same as grid state scaling)
            power_consumption_kw = float(row.get('Power Consumption (kW)', 1))
            capacity_mw = (power_consumption_kw * 100000 / 1000) * (0.5 + i * 0.1)
            
            t = Thermostat(
                device_id=f"TH_{i:03d}",
                location=f"Building {i+1}",
                current_temp=round(current_temp, 1),
                target_temp=base_temp,
                mode=ThermostatMode.COOLING if current_temp > base_temp else ThermostatMode.HEATING,
                capacity_mw=max(5, capacity_mw),  # Increased minimum capacity
                flexibility=0.7 + (i % 3) * 0.1,
            )
            thermostats.append(t)
        
        return thermostats
    
    def get_dataset_scenarios(self, samples=3):
        """Extract multiple grid scenarios from dataset"""
        df = self.load_data()
        scenarios = []
        
        step = len(df) // samples
        for i in range(samples):
            row = df.iloc[i * step]
            grid = self.create_grid_state_from_row(row)
            scenarios.append({
                'grid': grid,
                'thermostats': self.create_thermostats(5 + i * 3),
                'description': f"Scenario {i+1}"
            })
        
        return scenarios


def demo_data_loading():
    """Demo: Load and display real data"""
    print("\n" + "="*60)
    print("Loading Real Smart Grid Data from Kaggle")
    print("="*60)
    
    loader = SmartGridDataLoader()
    loader.get_data_info()
    
    # Get scenarios
    scenarios = loader.get_dataset_scenarios(samples=3)
    
    for scenario in scenarios:
        grid = scenario['grid']
        thermostats = scenario['thermostats']
        
        print(f"\n{scenario['description']}:")
        print(f"  Grid Status: {grid.status.value.upper()}")
        print(f"  Demand: {grid.demand_mw:.1f} MW")
        print(f"  Generation: {grid.generation_mw:.1f} MW")
        print(f"  Frequency: {grid.frequency_hz:.2f} Hz")
        print(f"  Thermostats: {len(thermostats)}")
        for t in thermostats[:2]:
            print(f"    - {t.device_id}: {t.current_temp}°C → {t.target_temp}°C (capacity: {t.capacity_mw:.2f} MW)")


if __name__ == "__main__":
    demo_data_loading()
