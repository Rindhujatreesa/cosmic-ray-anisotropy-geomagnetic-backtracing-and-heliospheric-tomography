from __future__ import annotations

import numpy as np
import pandas as pd


def pressure_correct(
    count_rate: pd.Series,
    pressure_mbar: pd.Series,
    reference_pressure_mbar: float,
    coefficient_percent_per_mbar: float,
) -> pd.Series:
    """
    Apply exponential atmospheric-pressure correction.

    coefficient is expressed in percent per mbar.

    The sign convention follows the NMDB station coefficient
    convention used for the correction implemented here.
    """

    beta = coefficient_percent_per_mbar / 100.0

    correction = np.exp(
        beta * (
            pressure_mbar
            - reference_pressure_mbar
        )
    )

    return count_rate * correction


def fractional_variation(
    values: pd.Series,
    method: str = "median",
) -> pd.Series:

    if method == "median":
        reference = values.median()

    elif method == "mean":
        reference = values.mean()

    else:
        raise ValueError(
            "method must be 'median' or 'mean'"
        )

    if reference == 0:
        raise ValueError(
            "Reference intensity cannot be zero."
        )

    return (
        (values - reference)
        / reference
        * 100.0
    )


def normalize(
    values: pd.Series,
) -> pd.Series:

    mean = values.mean()

    if mean == 0:
        raise ValueError(
            "Cannot normalize by zero."
        )

    return values / mean
