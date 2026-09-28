from __future__ import annotations

import numpy as np
import pandas as pd


def first_harmonic(
    timestamps: pd.Series,
    values: pd.Series,
    period_hours: float = 24.0,
) -> dict:

    time_hours = (
        timestamps.astype("int64")
        / 3.6e12
    )

    omega = 2.0 * np.pi / period_hours

    phase_argument = omega * time_hours

    x = values.to_numpy(dtype=float)

    cos_term = np.cos(phase_argument)
    sin_term = np.sin(phase_argument)

    a1 = (
        2.0
        / len(x)
        * np.sum(x * cos_term)
    )

    b1 = (
        2.0
        / len(x)
        * np.sum(x * sin_term)
    )

    amplitude = np.sqrt(
        a1**2 + b1**2
    )

    phase_rad = np.arctan2(
        b1,
        a1,
    )

    phase_hours = (
        phase_rad
        / omega
    ) % period_hours

    return {
        "a1": float(a1),
        "b1": float(b1),
        "amplitude": float(amplitude),
        "phase_rad": float(phase_rad),
        "phase_hours": float(phase_hours),
        "period_hours": period_hours,
    }
