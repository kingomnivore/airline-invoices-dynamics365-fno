"""Constants for the analysis."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "Dataset" / "P-5.2"

# Rows below this quarterly spend are dropped. Amounts are in $000.
MIN_AMOUNT = 100.0

# Quarters a carrier and aircraft type needs before it has an established rate.
MIN_QUARTERS = 4

# Automation threshold drawn on the rate spread figure. Chosen, not derived.
USABLE = 0.15

ENTITY = ["UNIQUE_CARRIER", "AIRCRAFT_TYPE"]

BENCHMARKS = ["industry", "indexed", "contract"]

BENCHMARK_LABELS = {
    "industry": "vs industry",
    "indexed": "vs same quarter",
    "contract": "vs own rate",
}

# Fuel, engine repair and airframe repair are third-party spend. Pilot pay is
# account 51230, salaries, and is carried as a reference case only.
CHARGES = {
    "Aircraft fuel": {
        "amount": "FUEL_FLY_OPS",
        "driver": "AIR_FUELS_ISSUED",
        "account": "51451",
        "rate_unit": "$/gallon",
        "driver_label": "Fuel issued, thousand gallons",
        "amount_label": "Fuel cost, $000",
    },
    "Pilot pay": {
        "amount": "PILOT_FLY_OPS",
        "driver": "TOTAL_AIR_HOURS",
        "account": "51230",
        "rate_unit": "$/hour",
        "driver_label": "Aircraft air hours, thousands",
        "amount_label": "Pilot and copilot pay, $000",
    },
    "Engine repair": {
        "amount": "ENGINE_REPAIRS",
        "driver": "TOTAL_AIR_HOURS",
        "account": "52432",
        "rate_unit": "$/hour",
        "driver_label": "Aircraft air hours, thousands",
        "amount_label": "Engine repairs, $000",
    },
    "Airframe repair": {
        "amount": "AIRFRAME_REPAIR",
        "driver": "TOTAL_AIR_HOURS",
        "account": "52431",
        "rate_unit": "$/hour",
        "driver_label": "Aircraft air hours, thousands",
        "amount_label": "Airframe repairs, $000",
    },
}

# Detection test parameters. Not used to support any article claim; see README.
BURDEN = 0.05
OVERCHARGE = 0.08
SHARE = 0.05
SEED = 0
