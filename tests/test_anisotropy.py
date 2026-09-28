import numpy as np
import pandas as pd

from cr_tomo.anisotropy import (
    first_harmonic,
)


def test_first_harmonic():

    timestamps = pd.date_range(
        "2025-01-01",
        periods=240,
        freq="1h",
    )

    hours = np.arange(
        len(timestamps)
    )

    values = np.cos(
        2 * np.pi * hours / 24
    )

    result = first_harmonic(
        pd.Series(timestamps),
        pd.Series(values),
        period_hours=24,
    )

    assert result["amplitude"] > 0.9
