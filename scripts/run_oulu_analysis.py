from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd

from cr_tomo.anisotropy import first_harmonic
from cr_tomo.config import load_config
from cr_tomo.data.nmdb import load_nmdb_data
from cr_tomo.plotting import (
    plot_count_rate,
    plot_fractional_variation,
)
from cr_tomo.preprocessing import (
    fractional_variation,
)
from cr_tomo.qc import (
    add_quality_flags,
    remove_invalid,
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        default="configs/oulu.yaml",
    )

    parser.add_argument(
        "--start",
        required=True,
        help="Start date: YYYY-MM-DD",
    )

    parser.add_argument(
        "--end",
        required=True,
        help="End date: YYYY-MM-DD",
    )

    args = parser.parse_args()

    config = load_config(args.config)

    station = config["station"]["code"]

    resolution = config["data"]["resolution"]

    figure_dir = Path(
        config["output"]["figure_directory"]
    )

    processed_dir = Path(
        config["output"]["processed_directory"]
    )

    processed_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 60)
    print("CR-TOMO OULU ANALYSIS")
    print("=" * 60)

    print(f"Station    : {station}")
    print(f"Start      : {args.start}")
    print(f"End        : {args.end}")
    print(f"Resolution : {resolution} min")

    start = datetime.fromisoformat(
        args.start
    )

    end = datetime.fromisoformat(
        args.end
    )

    print("\nDownloading NMDB data...")

    df = load_nmdb_data(
        station=station,
        start=start,
        end=end,
        resolution=resolution,
    )

    print(
        f"Downloaded {len(df)} records."
    )

    print("\nRunning quality control...")

    df = add_quality_flags(df)

    n_invalid = (~df["qc_valid"]).sum()

    print(
        f"Invalid records: {n_invalid}"
    )

    clean = remove_invalid(df)

    print(
        f"Valid records: {len(clean)}"
    )

    print("\nCalculating fractional variation...")

    clean[
        "fractional_variation_percent"
    ] = fractional_variation(
        clean["count_rate"],
        method=config["analysis"]["reference_method"],
    )

    print("\nRunning first-harmonic analysis...")

    harmonic = first_harmonic(
        clean["timestamp"],
        clean["fractional_variation_percent"],
        period_hours=config["analysis"][
            "harmonic_period_hours"
        ],
    )

    print("\nHARMONIC RESULT")
    print("-" * 40)

    print(
        f"a1          : {harmonic['a1']:.6f}"
    )

    print(
        f"b1          : {harmonic['b1']:.6f}"
    )

    print(
        f"Amplitude   : {harmonic['amplitude']:.6f} %"
    )

    print(
        f"Phase       : {harmonic['phase_hours']:.3f} h"
    )

    output_csv = (
        processed_dir
        / f"{station}_{args.start}_{args.end}.csv"
    )

    clean.to_csv(
        output_csv,
        index=False,
    )

    print(
        f"\nSaved processed data: {output_csv}"
    )

    plot_count_rate(
        clean,
        figure_dir / "oulu_count_rate.png",
    )

    plot_fractional_variation(
        clean,
        figure_dir / "oulu_fractional_variation.png",
    )

    print("\nFigures written to:")
    print(figure_dir)

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
