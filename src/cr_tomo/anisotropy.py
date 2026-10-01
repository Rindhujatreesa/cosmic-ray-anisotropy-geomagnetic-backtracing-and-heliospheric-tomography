from __future__ import annotations

import numpy as np
import pandas as pd


def first_harmonic(timestamps, values, period_hours=24.0):
    """Fit a first harmonic using elapsed hours, with a linear trend."""
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

    residuals = y - design @ coefficients
    dof = len(y) - design.shape[1]
    residual_std = (
        float(np.sqrt(np.sum(residuals**2) / dof))
        if dof > 0 else float("nan")
    )

    return {
        "mean_level": float(intercept),
        "trend": float(trend),
        "a1": float(a1),
        "b1": float(b1),
        "amplitude": amplitude,
        "phase_hours": phase_hours,
        "residual_std": residual_std,
        "period_hours": float(period_hours),
    }