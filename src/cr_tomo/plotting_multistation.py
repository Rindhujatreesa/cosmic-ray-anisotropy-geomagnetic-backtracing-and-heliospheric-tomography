
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_station_variations(
    aligned: pd.DataFrame,
    station_columns: list[str],
    output_path: str | Path,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))

    for station in station_columns:
        ax.plot(
            aligned["timestamp"],
            aligned[station],
            linewidth=0.9,
            label=station,
        )

    ax.axhline(0, linestyle="--", linewidth=0.8)
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Fractional variation (%)")
    ax.set_title("Multi-station Cosmic-Ray Variability")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_differential_residuals(
    differential: pd.DataFrame,
    station_columns: list[str],
    output_path: str | Path,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))

    for station in station_columns:
        column = f"{station}_differential_percent"
        ax.plot(
            differential["timestamp"],
            differential[column],
            linewidth=0.9,
            label=station,
        )

    ax.axhline(0, linestyle="--", linewidth=0.8)
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Deviation from network median (%)")
    ax.set_title("Inter-Station Differential Variations")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)