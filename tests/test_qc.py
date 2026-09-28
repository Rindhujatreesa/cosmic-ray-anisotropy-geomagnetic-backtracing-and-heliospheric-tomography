import pandas as pd

from cr_tomo.qc import (
    add_quality_flags,
    remove_invalid,
)


def test_qc_adds_flags():

    df = pd.DataFrame(
        {
            "count_rate": [
                100,
                101,
                99,
                100,
            ]
        }
    )

    result = add_quality_flags(df)

    assert "qc_valid" in result.columns
    assert result["qc_valid"].all()


def test_remove_invalid():

    df = pd.DataFrame(
        {
            "count_rate": [
                100,
                -1,
                101,
            ]
        }
    )

    result = remove_invalid(
        add_quality_flags(df)
    )

    assert len(result) == 2
