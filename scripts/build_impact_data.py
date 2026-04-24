"""
Build the complete asset_impacts.json by merging curated data with generated estimates.
Run this after updating events or curated data.

Usage: python scripts/build_impact_data.py
"""
import json
import sys
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import load_events
from src.impact_generator import generate_full_impact_data, override_with_curated_data


def main():
    data_dir = Path(__file__).parent.parent / "data"
    
    # Load events
    print("📊 Loading events...")
    events = load_events()
    print(f"   Found {len(events)} events")
    
    # Generate baseline impact data
    print("\n⚙️  Generating baseline impact data from asset characteristics...")
    generated = generate_full_impact_data(events)
    total_cells = sum(
        sum(1 for h in asset_data.values() if h is not None)
        for event_data in generated.values()
        for asset_data in event_data.values()
    )
    print(f"   Generated {total_cells} data points")
    
    # Load curated overrides
    curated_path = data_dir / "curated_impacts.json"
    if curated_path.exists():
        print("\n🎯 Loading curated historical data...")
        with open(curated_path, "r") as f:
            curated = json.load(f)["impacts"]
        
        overrides = sum(
            sum(1 for h in asset_data.values() if h is not None)
            for event_data in curated.values()
            for asset_data in event_data.values()
        )
        print(f"   Found {overrides} curated data points")
        
        print("\n🔄 Merging curated data over generated baseline...")
        final = override_with_curated_data(generated, curated)
    else:
        print("\n⚠️  No curated data file found, using generated data only")
        final = generated
    
    # Save
    output_path = data_dir / "asset_impacts.json"
    with open(output_path, "w") as f:
        json.dump({"impacts": final}, f, indent=2)
    
    print(f"\n✅ Built {output_path}")
    print(f"   Total events: {len(final)}")
    print(f"   Total data points: {sum(sum(1 for h in a.values() if h is not None) for e in final.values() for a in e.values())}")


if __name__ == "__main__":
    main()