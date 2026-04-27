"""
Build asset_impacts.json from real Yahoo Finance data + fallbacks.
Verbose logging so failures are visible.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import load_events, get_asset_classes
from src.historical_fetcher import fetch_event_returns
from src.impact_generator import generate_full_impact_data, override_with_curated_data


def build_with_real_data(events, asset_ids, verbose=False):
    """Fetch real returns for every event-asset combination."""
    print("=" * 70)
    print("FETCHING REAL HISTORICAL DATA FROM YAHOO FINANCE")
    print("=" * 70)
    print(f"  Events: {len(events)}  |  Assets per event: {len(asset_ids)}")
    print(f"  Total API calls: ~{len(events) * len(asset_ids)}")
    print(f"  Estimated time: {len(events) * len(asset_ids) * 0.4 / 60:.1f} minutes")
    print()

    real_impacts = {}
    data_quality = {}

    for i, event in enumerate(events, 1):
        print(f"[{i}/{len(events)}] {event['name']} ({event['year']})")
        results, ok, fail = fetch_event_returns(event, asset_ids, verbose=verbose)
        real_impacts[event["id"]] = results

        data_quality[event["id"]] = {}
        for asset_id, horizons in results.items():
            data_quality[event["id"]][asset_id] = {
                h: ("real" if v is not None else "missing")
                for h, v in horizons.items()
            }

        real_count = sum(
            1 for asset_data in results.values()
            for v in asset_data.values() if v is not None
        )
        total = len(asset_ids) * 5
        pct = (real_count / total) * 100 if total else 0
        print(f"   {real_count}/{total} cells ({pct:.0f}%)  |  Assets OK: {ok}/{len(asset_ids)}")

    return real_impacts, data_quality


def merge_real_and_generated(real_impacts, generated_impacts, data_quality):
    final_impacts = {}
    for event_id in real_impacts:
        final_impacts[event_id] = {}
        for asset_id in real_impacts[event_id]:
            final_impacts[event_id][asset_id] = {}
            for horizon in real_impacts[event_id][asset_id]:
                real_val = real_impacts[event_id][asset_id][horizon]
                if real_val is not None:
                    final_impacts[event_id][asset_id][horizon] = real_val
                else:
                    gen_val = (
                        generated_impacts.get(event_id, {})
                        .get(asset_id, {})
                        .get(horizon)
                    )
                    final_impacts[event_id][asset_id][horizon] = gen_val
                    if gen_val is not None:
                        data_quality[event_id][asset_id][horizon] = "estimated"
    return final_impacts, data_quality


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", help="Show every asset fetch")
    parser.add_argument("--test", action="store_true", help="Only fetch first 3 events")
    args = parser.parse_args()

    data_dir = Path(__file__).parent.parent / "data"
    events = load_events()
    if args.test:
        events = events[:3]
        print(f"TEST MODE: only processing first 3 events\n")
    assets = get_asset_classes()

    print(f"Loaded {len(events)} events and {len(assets)} asset classes\n")

    print("Step 1: Generating rule-based fallback baseline...")
    generated = generate_full_impact_data(events)
    print(f"   Done.\n")

    real_impacts, data_quality = build_with_real_data(events, assets, verbose=args.verbose)

    print("\nMerging real data over generated baseline...")
    final, data_quality = merge_real_and_generated(real_impacts, generated, data_quality)

    curated_path = data_dir / "curated_impacts.json"
    if curated_path.exists():
        print("Applying curated overrides...")
        with open(curated_path, "r") as f:
            curated = json.load(f)["impacts"]
        final = override_with_curated_data(final, curated)
        for event_id, assets_data in curated.items():
            if event_id not in data_quality:
                data_quality[event_id] = {}
            for asset_id, horizons in assets_data.items():
                if asset_id not in data_quality[event_id]:
                    data_quality[event_id][asset_id] = {}
                for h, v in horizons.items():
                    if v is not None:
                        data_quality[event_id][asset_id][h] = "curated"

    output_path = data_dir / "asset_impacts.json"
    with open(output_path, "w") as f:
        json.dump({
            "impacts": final,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "events_count": len(final),
            }
        }, f, indent=2)

    quality_path = data_dir / "data_quality.json"
    with open(quality_path, "w") as f:
        json.dump(data_quality, f, indent=2)

    total = real = curated_n = estimated = missing = 0
    for event_id in data_quality:
        for asset_id in data_quality[event_id]:
            for h, q in data_quality[event_id][asset_id].items():
                total += 1
                if q == "real": real += 1
                elif q == "curated": curated_n += 1
                elif q == "estimated": estimated += 1
                elif q == "missing": missing += 1

    print()
    print("=" * 70)
    print("BUILD COMPLETE")
    print("=" * 70)
    print(f"  Total cells:     {total}")
    print(f"  Real data:       {real} ({real/total*100:.1f}%)")
    print(f"  Curated:         {curated_n} ({curated_n/total*100:.1f}%)")
    print(f"  Estimated:       {estimated} ({estimated/total*100:.1f}%)")
    print(f"  Missing:         {missing} ({missing/total*100:.1f}%)")


if __name__ == "__main__":
    main()