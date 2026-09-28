from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_count_rate(
    df: pd.DataFrame,
    output_path: str | Path,
) -> None:

    fig, ax = plt.subplots(
        figsize=(11, 5)
    )

    ax.plot(
        df["timestamp"],
        df["count_rate"],
        linewidth=0.9,
    )

    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel(
        "Neutron monitor count rate"
    )

    ax.set_title(
        "Oulu Neutron Monitor Count Rate"
    )

    ax.grid(
        True,
        alpha=0.3,
    )

    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def plot_fractional_variation(
    df: pd.DataFrame,
    output_path: str | Path,
) -> None:

    fig, ax = plt.subplots(
        figsize=(11, 5)
    )

    ax.plot(
        df["timestamp"],
        df["fractional_variation_percent"],
        linewidth=0.9,
    )

    ax.axhline(
        0.0,
        linewidth=0.8,
        linestyle="--",
    )

    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel(
        "Fractional variation (%)"
    )

    ax.set_title(
        "Oulu Cosmic-Ray Relative Variation"
    )

    ax.grid(
        True,
        alpha=0.3,
    )

    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def plot_harmonic(
    result: dict,
    output_path: str | Path,
) -> None:

    amplitude = result["amplitude"]
    phase = result["phase_hours"]
    period = result["period_hours"]

    import numpy as np

    hours = np.linspace(
        0,
        period,
        500,
    )

    omega = 2 * np.pi / period

    model = amplitude * np.cos(
        omega * (hours - phase)
    )

    fig, ax = plt.subplots(
        figsize=(9, 5)
    )

    ax.plot(
        hours,
        model,
        linewidth=1.5,
    )

    ax.axhline(
        0,
        linewidth=0.8,
        linestyle="--",
    )

    ax.set_xlabel(
        "Time within harmonic period (hours)"
    )

    ax.set_ylabel(
        "Relative amplitude (%)"
    )

    ax.set_title(
        "First-Harmonic Cosmic-Ray Variation"
    )

    ax.grid(
        True,
        alpha=0.3,
    )

    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)
