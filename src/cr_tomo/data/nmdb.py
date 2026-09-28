from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from io import StringIO

import pandas as pd
import requests


@dataclass
class NMDBRequest:
    station: str
    start: datetime
    end: datetime
    resolution: int = 60


def build_nest_url(request: NMDBRequest) -> str:
    """
    Build an NMDB NEST query URL.

    The exact NEST query interface can evolve, so this function
    is isolated from the rest of the analysis pipeline.
    """

    start = request.start.strftime("%Y-%m-%d")
    end = request.end.strftime("%Y-%m-%d")

    return (
        "https://www.nmdb.eu/nest/draw_graph.php"
        f"?stations[]={request.station}"
        "&output=ascii"
        "&tabchoice=revori"
        "&dtype=corr_for_efficiency"
        f"&tresolution={request.resolution}"
        f"&start_date={start}"
        f"&end_date={end}"
    )


def download_text(
    request: NMDBRequest,
    timeout: int = 60,
) -> str:

    url = build_nest_url(request)

    response = requests.get(
        url,
        timeout=timeout,
        headers={
            "User-Agent": "CR-TOMO/0.1 scientific research project"
        },
    )

    response.raise_for_status()

    return response.text


def parse_nmdb_ascii(text: str) -> pd.DataFrame:
    """
    Parse a simple NMDB ASCII response.

    The parser is intentionally conservative because NMDB
    output formats may contain comments and metadata.
    """

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        lines.append(line)

    if not lines:
        raise ValueError("No data found in NMDB response.")

    rows = []

    for line in lines:

        parts = line.replace(",", " ").split()

        if len(parts) < 2:
            continue

        timestamp = f"{parts[0]} {parts[1]}"

        try:
            value = float(parts[-1])
        except ValueError:
            continue

        rows.append(
            {
                "timestamp": timestamp,
                "count_rate": value,
            }
        )

    if not rows:
        raise ValueError("Could not parse NMDB data.")

    df = pd.DataFrame(rows)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
        utc=True,
    )

    df["count_rate"] = pd.to_numeric(
        df["count_rate"],
        errors="coerce",
    )

    df = df.dropna(
        subset=["timestamp", "count_rate"]
    )

    df = df.sort_values("timestamp")

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
