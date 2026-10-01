
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from cr_tomo.config import load_config
from cr_tomo.data.nmdb import load_nmdb_data
from cr_tomo.multistation import (
    align_stations,
    calculate_differential_residuals,
    calculate_fractional_variation,
    fit_first_harmonic,
)
from cr_tomo.plotting_multistation import (
    plot_differential_residuals,
    plot_station_variations,
)
from cr_tomo.qc import add_quality_flags, remove_invalid


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CR-TOMO multi-station analysis"
    )
    parser.add_argument("--config", default="configs/oulu.yaml")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    args = parser.parse_args()

    config = load_config(args.config)
    stations = config["stations"]
    resolution = config["data"]["resolution"]
    period = config["analysis"]["harmonic_period_hours"]
    reference_method = config["analysis"]["reference_method"]
    threshold = config["analysis"].get("outlier_threshold", 5.0)

    start = datetime.fromisoformat(args.start)
    end = (
        datetime.fromisoformat(args.end)
        + timedelta(days=1)
        - timedelta(minutes=1)
    )

    processed_dir = Path(config["output"]["processed_directory"])
    figure_dir = Path(config["output"]["figure_directory"])
    processed_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("CR-TOMO MULTI-STATION ANALYSIS")
    print("=" * 60)
    print(f"Stations   : {', '.join(stations)}")
    print(f"Start      : {start}")
    print(f"End        : {end}")
    print(f"Resolution : {resolution} minutes")

    fractional_data = {}
    summary_rows = []

    for station in stations:
        print(f"\nDownloading {station}...")

        raw = load_nmdb_data(
            station=station,
            start=start,
            end=end,
            resolution=resolution,
        )

        print(f"  Downloaded records: {len(raw)}")

        flagged = add_quality_flags(
            raw,
            value_column="count_rate",
            z_threshold=threshold,
        )
        clean = remove_invalid(flagged)

        print(
            f"  Valid: {len(clean)}; "
            f"flagged: {len(raw) - len(clean)}"
        )

        if clean.empty:
            raise RuntimeError(
                f"No valid data remain for station {station}."
            )

        clean = calculate_fractional_variation(
            clean,
            reference_method=reference_method,
        )

        clean["station"] = station

        clean_path = processed_dir / (
            f"{station}_{args.start}_{args.end}_processed.csv"
        )
        clean.to_csv(clean_path, index=False)

        fractional_data[station] = clean[
            ["timestamp", "fractional_variation_percent"]
        ].copy()

        harmonic = fit_first_harmonic(
            clean["timestamp"],
            clean["fractional_variation_percent"],
            period_hours=period,
        )

        summary_rows.append(
            {
                "station": station,
                "cutoff_rigidity_gv": stations[station].get(
                    "cutoff_rigidity_gv"
                ),
                **harmonic,
                "records_downloaded": len(raw),
                "records_valid": len(clean),
                "records_flagged": len(raw) - len(clean),
            }
        )

    print("\nAligning timestamps shared by all stations...")
    aligned = align_stations(fractional_data)
    station_columns = list(stations.keys())

    aligned_path = processed_dir / (
        f"multistation_aligned_{args.start}_{args.end}.csv"
    )
    aligned.to_csv(aligned_path, index=False)

    print(f"Shared timestamps: {len(aligned)}")

    if len(aligned) < 5:
        raise RuntimeError(
            "Too few shared timestamps for comparison."
        )

    differential = calculate_differential_residuals(
        aligned,
        station_columns,
    )

    differential_path = processed_dir / (
        f"multistation_differential_{args.start}_{args.end}.csv"
    )
    differential.to_csv(differential_path, index=False)

    summary = pd.DataFrame(summary_rows)
    summary_path = processed_dir / (
        f"multistation_harmonics_{args.start}_{args.end}.csv"
    )
    summary.to_csv(summary_path, index=False)

    metadata = {
        "start_utc": start.isoformat(),
        "end_utc": end.isoformat(),
        "stations": station_columns,
        "resolution_minutes": resolution,
        "data_product": config["data"].get(
            "data_type", "corr_for_efficiency"
        ),
        "table": config["data"].get("table", "revori"),
        "reference_method": reference_method,
        "harmonic_period_hours": period,
        "shared_timestamp_count": len(aligned),
        "interpretation_note": (
            "Differential residuals are comparative diagnostics, "
            "not a physical anisotropy reconstruction."
        ),
    }

    metadata_path = processed_dir / (
        f"multistation_metadata_{args.start}_{args.end}.json"
    )
    metadata_path.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    plot_station_variations(
        aligned,
        station_columns,
        figure_dir / "multistation_variations.png",
    )

    plot_differential_residuals(
        differential,
        station_columns,
        figure_dir / "multistation_differential.png",
    )

    print("\nHARMONIC SUMMARY")
    print(summary.to_string(index=False))

    print("\nSaved outputs:")
    print(f"  {summary_path}")
    print(f"  {aligned_path}")
    print(f"  {differential_path}")
    print(f"  {metadata_path}")
    print(f"  Figures: {figure_dir}")
    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()