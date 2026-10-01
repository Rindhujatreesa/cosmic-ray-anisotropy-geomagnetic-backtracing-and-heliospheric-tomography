
import numpy as np
import pandas as pd
import pytest

from cr_tomo.multistation import (
    align_stations,
    calculate_differential_residuals,
    calculate_fractional_variation,
    fit_first_harmonic,
)


def test_fractional_variation_uses_median():
    df = pd.DataFrame({"count_rate": [99.0, 100.0, 101.0]})

    result = calculate_fractional_variation(df)

    assert result["fractional_variation_percent"].iloc[1] == 0.0


def test_alignment_uses_common_timestamps():
    timestamps = pd.date_range(
        "2025-01-01", periods=4, freq="1h", tz="UTC"
    )

    station_data = {
        "OULU": pd.DataFrame({
            "timestamp": timestamps,
            "fractional_variation_percent": [0.0, 1.0, 2.0, 3.0],
        }),
        "KIEL": pd.DataFrame({
            "timestamp": timestamps[1:],
            "fractional_variation_percent": [1.0, 2.0, 3.0],
        }),
    }

    result = align_stations(station_data)

    assert len(result) == 3
    assert result["timestamp"].iloc[0] == timestamps[1]


def test_alignment_rejects_single_station():
    with pytest.raises(ValueError):
        align_stations({
            "OULU": pd.DataFrame({
                "timestamp": pd.date_range(
                    "2025-01-01", periods=5, freq="1h", tz="UTC"
                ),
                "fractional_variation_percent": np.zeros(5),
            })
        })


def test_harmonic_fit_recovers_synthetic_signal():
    timestamps = pd.date_range(
        "2025-01-01", periods=240, freq="1h", tz="UTC"
    )
    elapsed_hours = np.arange(len(timestamps))
    expected_amplitude = 0.2

    values = (
        0.03
        + 0.0001 * elapsed_hours
        + expected_amplitude * np.cos(
            2 * np.pi * elapsed_hours / 24
        )
    )

    result = fit_first_harmonic(
        pd.Series(timestamps),
        pd.Series(values),
        period_hours=24,
    )

    assert result["amplitude_percent"] == pytest.approx(
        expected_amplitude, abs=1e-8
    )
    assert result["phase_hours_from_start"] == pytest.approx(
        0.0, abs=1e-7
    )


def test_differential_residuals():
    aligned = pd.DataFrame({
        "timestamp": pd.date_range(
            "2025-01-01", periods=2, freq="1h", tz="UTC"
        ),
        "OULU": [1.0, 2.0],
        "KIEL": [3.0, 4.0],
        "ROME": [2.0, 3.0],
    })

    result = calculate_differential_residuals(
        aligned, ["OULU", "KIEL", "ROME"]
    )

    assert result["network_median_percent"].tolist() == [2.0, 3.0]
    assert result["OULU_differential_percent"].tolist() == [-1.0, -1.0]