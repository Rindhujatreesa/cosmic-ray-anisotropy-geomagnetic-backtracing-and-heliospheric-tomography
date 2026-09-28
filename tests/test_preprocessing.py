import pandas as pd

from cr_tomo.preprocessing import (
    fractional_variation,
)


def test_fractional_variation_zero_at_reference():

    values = pd.Series(
        [100.0, 100.0, 110.0]
    )

    result = fractional_variation(
        values,
        method="median",
    )

    assert result.iloc[0] == 0.0
    assert result.iloc[1] == 0.0
