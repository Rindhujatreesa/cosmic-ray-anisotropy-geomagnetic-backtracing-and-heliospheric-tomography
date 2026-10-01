
from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_fractional_variation(
    df: pd.DataFrame,
    reference_method: str = "median",
) -> pd.DataFrame:
    """Calculate fractional variation in percent."""

    result = df.copy()
    values = result["count_rate"]

    if reference_method == "median":
        reference = values.median()
    elif reference_method == "mean":
        reference = values.mean()
    else:
        raise ValueError(
            "reference_method must be 'median' or 'mean'"
        )

    if not np.isfinite(reference) or reference == 0:
        raise ValueError("Invalid reference intensity.")

    result["fractional_variation_percent"] = (
        100.0 * (values - reference) / reference
    )

    return result


def align_stations(
    station_data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Align station fractional variations on exact UTC timestamps.

    The returned dataframe contains only timestamps shared by
    every supplied station. Missing data are not interpolated.
    """

    if len(station_data) < 2:
        raise ValueError("At least two stations are required.")

    merged = None

    for station, df in station_data.items():
        required = {
            "timestamp",
            "fractional_variation_percent",
        }
        missing = required - set(df.columns)

        if missing:
            raise ValueError(
                f"{station} is missing columns: {sorted(missing)}"
            )

        part = df[
            ["timestamp", "fractional_variation_percent"]
        ].copy()

        part["timestamp"] = pd.to_datetime(
            part["timestamp"], utc=True
        )

        part = part.rename(
            columns={
                "fractional_variation_percent": station
            }
        )

        if part["timestamp"].duplicated().any():
            raise ValueError(
                f"{station} contains duplicate timestamps."
            )

        if merged is None:
            merged = part
        else:
            merged = merged.merge(
                part,
                on="timestamp",
                how="inner",
                validate="one_to_one",
            )

    if merged is None or merged.empty:
        raise ValueError(
            "No timestamps are shared by all stations."
        )

    return merged.sort_values("timestamp").reset_index(drop=True)


def fit_first_harmonic(timestamps, values, period_hours=24.0):
    """Fit a sinusoid plus linear trend to a time series."""
    import numpy as np
    import pandas as pd

    if period_hours <= 0:
        raise ValueError("period_hours must be positive")

    times = pd.Series(pd.to_datetime(timestamps, utc=True))
    y = np.asarray(values, dtype=float)

    if len(times) != len(y):
        raise ValueError("timestamps and values must have equal lengths")

    valid = times.notna().to_numpy() & np.isfinite(y)
    times = times[valid].reset_index(drop=True)
    y = y[valid]

    if len(y) < 5:
        raise ValueError("At least five valid observations are required")

    elapsed_hours = (
        (times - times.iloc[0]).dt.total_seconds().to_numpy() / 3600.0
    )

    omega = 2.0 * np.pi / period_hours
    span = max(float(np.ptp(elapsed_hours)), 1.0)
    trend_time = (elapsed_hours - elapsed_hours.mean()) / span

    design = np.column_stack([
        np.ones(len(y)),
        trend_time,
        np.cos(omega * elapsed_hours),
        np.sin(omega * elapsed_hours),
    ])

    coefficients, _, rank, _ = np.linalg.lstsq(design, y, rcond=None)

    if rank < design.shape[1]:
        raise ValueError("Harmonic fit is rank-deficient")

    intercept, trend, a1, b1 = coefficients
    amplitude = float(np.hypot(a1, b1))
    phase_rad = float(np.arctan2(b1, a1))
    phase_hours = float((phase_rad / omega) % period_hours)

    # Normalize floating-point values near the period boundary to zero.
    if np.isclose(phase_hours, period_hours, atol=1e-10):
        phase_hours = 0.0

    residuals = y - design @ coefficients
    dof = len(y) - design.shape[1]
    residual_std = (
        float(np.sqrt(np.sum(residuals**2) / dof))
        if dof > 0 else float("nan")
    )

    return {
        "n_observations": int(len(y)),
        "mean_level_percent": float(intercept),
        "trend_coefficient": float(trend),
        "a1_percent": float(a1),
        "b1_percent": float(b1),
        "amplitude_percent": amplitude,
        "phase_hours_from_start": phase_hours,
        "residual_std_percent": residual_std,
        "period_hours": float(period_hours),
    }


def calculate_differential_residuals(
    aligned: pd.DataFrame,
    station_columns: list[str],
) -> pd.DataFrame:
    """
    Subtract the cross-station median at each timestamp.

    This is a comparative diagnostic, not a physical anisotropy
    reconstruction. It can remove genuine common cosmic-ray signals.
    """

    result = aligned.copy()

    network_median = result[station_columns].median(axis=1)
    result["network_median_percent"] = network_median

    for station in station_columns:
        result[f"{station}_differential_percent"] = (
            result[station] - network_median
        )

    return result