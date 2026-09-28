from __future__ import annotations

import numpy as np
import pandas as pd


def add_quality_flags(
    df: pd.DataFrame,
    value_column: str = "count_rate",
    z_threshold: float = 5.0,
) -> pd.DataFrame:

    result = df.copy()

    values = result[value_column]

    median = values.median()
    mad = np.median(np.abs(values - median))

    if mad == 0:
        robust_z = pd.Series(
            np.zeros(len(values)),
            index=result.index,
        )
    else:
        robust_z = (
            0.6745 * (values - median) / mad
        )

    result["qc_missing"] = values.isna()

    result["qc_negative"] = values < 0

    result["robust_z"] = robust_z

    result["qc_outlier"] = (
        np.abs(robust_z) > z_threshold
    )

    result["qc_valid"] = ~(
        result["qc_missing"]
        | result["qc_negative"]
        | result["qc_outlier"]
    )

    return result


def remove_invalid(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if "qc_valid" not in df.columns:
        raise ValueError(
            "Run add_quality_flags() first."
        )

    return (
        df[df["qc_valid"]]
        .copy()
        .reset_index(drop=True)
    )
