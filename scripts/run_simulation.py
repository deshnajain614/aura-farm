"""
AURA-Farm Simulation Runner CLI
===============================
Runs automated ticks of the 27-step closed-loop lifecycle and prints real-time status.
"""
import argparse
import time
import sys

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from aura_farm.orchestrator import orchestrator

def run_simulation(ticks: int = 25, delay: float = 0.5):
    print("=" * 75)
    print("  [AURA-Farm] Autonomous Unified Robotic Agriculture Farm OS")
    print(f"  Executing {ticks} autonomous orchestration ticks...")
    print("=" * 75)

    for i in range(1, ticks + 1):
        snapshot = orchestrator.tick()
        lifecycle = snapshot["lifecycle"]
        water = snapshot["water"]
        climate = snapshot["climate"]
        safety = snapshot["safety"]

        print(f"[{i:02d}/{ticks:02d}] State: {lifecycle['state']:<24} | Crop: {lifecycle['crop']} | Cycle #{lifecycle['cycle']} (Day {lifecycle['cycle_day']})")
        print(f"     Water: pH {water['ph']:.2f} | EC {water['ec_ms_cm']:.2f} mS/cm | DO {water['dissolved_oxygen_mg_l']:.1f} mg/L | Res {water['reservoir_level_pct']:.0f}%")
        print(f"     Climate: {climate['air_temp_c']:.1f}°C | RH {climate['relative_humidity_pct']:.0f}% | VPD {climate['vpd_kpa']:.2f} kPa | CO2 {climate['co2_ppm']:.0f} ppm")

        if safety["recent_decisions"]:
            latest = safety["recent_decisions"][-1]
            gate_val = latest['gate'].value if hasattr(latest['gate'], 'value') else latest['gate']
            print(f"     Safety Gate: [{gate_val}] {latest['proposed_action']} - {latest['reason']}")
        print("-" * 75)

        if delay > 0:
            time.sleep(delay)

    print("\n[SUCCESS] Simulation run completed.")
    print(f"Total Packages Sealed: {snapshot['total_packages_sealed']}")
    print(f"Total Biomass Composted: {snapshot['total_compost_kg']} kg")
    print(f"Cold Storage Inventory: {snapshot['storage_inventory_count']} batches")
    print("=" * 75)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AURA-Farm autonomous simulation.")
    parser.add_argument("--ticks", type=int, default=22, help="Number of ticks to run")
    parser.add_argument("--fast", action="store_true", help="Run without delays")
    args = parser.parse_args()

    delay = 0.0 if args.fast else 0.4
    run_simulation(ticks=args.ticks, delay=delay)
