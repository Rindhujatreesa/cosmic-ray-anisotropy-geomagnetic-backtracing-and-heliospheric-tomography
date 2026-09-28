from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from urllib.parse import urlencode

import pandas as pd
import requests


@dataclass
class NMDBRequest:
    station: str
    start: datetime
    end: datetime
    resolution: int = 60

    # NMDB data product
    tabchoice: str = "revori"
    dtype: str = "corr_for_efficiency"

    # 0 = counts/s
    yunits: int = 0


def build_nest_url(request: NMDBRequest) -> str:
    """
    Build a valid NMDB NEST historical-data query.

    NMDB requires formchk=1 for HTTPS queries.
    Historical queries use date_choice=bydate and
    explicit start/end date fields.
    """

    params = [
        ("formchk", "1"),
        ("stations[]", request.station),
        ("output", "ascii"),
        ("tabchoice", request.tabchoice),
        ("dtype", request.dtype),
        ("tresolution", str(request.resolution)),
        ("yunits", str(request.yunits)),
        ("yscale", "0"),
        ("date_choice", "bydate"),

        ("start_day", f"{request.start.day:02d}"),
        ("start_month", f"{request.start.month:02d}"),
        ("start_year", str(request.start.year)),
        ("start_hour", f"{request.start.hour:02d}"),
        ("start_min", f"{request.start.minute:02d}"),

        ("end_day", f"{request.end.day:02d}"),
        ("end_month", f"{request.end.month:02d}"),
        ("end_year", str(request.end.year)),
        ("end_hour", f"{request.end.hour:02d}"),
        ("end_min", f"{request.end.minute:02d}"),
    ]

    query = urlencode(params)

    return (
        "https://www.nmdb.eu/nest/draw_graph.php?"
        + query
    )


def download_text(
    request: NMDBRequest,
    timeout: int = 60,
) -> str:

    url = build_nest_url(request)

    print(f"NMDB URL:\n{url}\n")

    response = requests.get(
        url,
        timeout=timeout,
        headers={
            "User-Agent": (
                "CR-TOMO/0.1 "
                "scientific research project"
            )
        },
    )

    response.raise_for_status()

    text = response.text

    if not text.strip():
        raise ValueError(
            "NMDB returned an empty response."
        )

    return text


def _is_data_line(line: str) -> bool:
    """
    Determine whether a line looks like an NMDB
    numerical data row.
    """

    line = line.strip()

    if not line:
        return False

    if line.startswith("#"):
        return False

    # Ignore HTML
    if "<html" in line.lower():
        return False

    if "<!doctype" in line.lower():
        return False

    parts = line.replace(",", " ").split()

    if len(parts) < 2:
        return False

    # A valid row normally starts with a date/time.
    try:
        pd.to_datetime(
            f"{parts[0]} {parts[1]}"
        )
    except Exception:
        return False

    return True


def parse_nmdb_ascii(text: str) -> pd.DataFrame:
    """
    Parse an NMDB ASCII response.

    The parser accepts whitespace-separated rows
    containing:

        YYYY-MM-DD HH:MM:SS value

    and tolerates additional metadata columns.
    """

    rows = []

    for line in text.splitlines():

        if not _is_data_line(line):
            continue

        parts = line.strip().replace(
            ",", " "
        ).split()

        if len(parts) < 3:
            continue

        timestamp_text = (
            f"{parts[0]} {parts[1]}"
        )

        try:
            timestamp = pd.to_datetime(
                timestamp_text,
                utc=True,
            )
        except Exception:
            continue

        # NMDB ASCII output may contain additional
        # fields. Find the first numeric value after
        # the timestamp.
        value = None

        for token in parts[2:]:

            try:
                value = float(token)
                break
            except ValueError:
                continue

        if value is None:
            continue

        rows.append(
            {
                "timestamp": timestamp,
                "count_rate": value,
            }
        )

    if not rows:
        # Preserve the server response to make debugging
        # much easier.
        preview = "\n".join(
            text.splitlines()[:30]
        )

        raise ValueError(
            "Could not parse NMDB data.\n\n"
            "First lines returned by NMDB:\n"
            f"{preview}"
        )

    df = pd.DataFrame(rows)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
    )

    df["count_rate"] = pd.to_numeric(
        df["count_rate"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "timestamp",
            "count_rate",
        ]
    )

    df = df.sort_values(
        "timestamp"
    )

    df = df.drop_duplicates(
        subset=["timestamp"]
    )

    return df.reset_index(drop=True)


def load_nmdb_data(
    station: str,
    start: datetime,
    end: datetime,
    resolution: int = 60,
) -> pd.DataFrame:

    request = NMDBRequest(
        station=station,
        start=start,
        end=end,
        resolution=resolution,
    )

    text = download_text(request)

    return parse_nmdb_ascii(text)