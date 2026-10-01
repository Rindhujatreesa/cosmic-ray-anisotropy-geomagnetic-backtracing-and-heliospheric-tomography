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
    tabchoice: str = "1h"
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
    Parse an NMDB response into a DataFrame with columns:
        timestamp
        count_rate

    Supports:
    - Whitespace-separated ASCII rows:
      YYYY-MM-DD HH:MM:SS value
    - Semicolon-separated NMDB rows:
      YYYY-MM-DD HH:MM:SS;value
    - HTML-wrapped responses containing timestamp/value records.

    Additional metadata columns and non-data lines are ignored.
    """
    import re
    from html import unescape

    # NMDB may return HTML containing data, or an HTML error page.
    # Remove scripts/styles and tags before parsing, but retain the
    # original response for diagnostic messages.
    parse_text = text

    if "<html" in text.lower() or "<!doctype html" in text.lower():
        parse_text = re.sub(
            r"(?is)<(script|style)\b[^>]*>.*?</\1>",
            " ",
            text,
        )
        parse_text = unescape(
            re.sub(r"<[^>]+>", "\n", parse_text)
        )

    rows = []

    # Match a timestamp followed by a numeric value, allowing either
    # whitespace or a semicolon between the timestamp and value.
    # This also handles adjacent records when HTML formatting removes
    # the newline between them.
    record_pattern = re.compile(
        r"(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})"
        r"\s*[;,\s]\s*"
        r"(?P<value>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?)"
    )

    for match in record_pattern.finditer(parse_text):
        timestamp_text = match.group("timestamp")
        value_text = match.group("value")

        try:
            timestamp = pd.to_datetime(
                timestamp_text,
                format="%Y-%m-%d %H:%M:%S",
                utc=True,
                errors="raise",
            )
            value = float(value_text)
        except (ValueError, TypeError, OverflowError):
            continue

        if not pd.notna(timestamp):
            continue

        rows.append(
            {
                "timestamp": timestamp,
                "count_rate": value,
            }
        )

    if not rows:
        # Produce a useful diagnostic for HTML error pages.
        if "<html" in text.lower() or "<!doctype html" in text.lower():
            visible = re.sub(
                r"(?is)<(script|style)\b[^>]*>.*?</\1>",
                " ",
                text,
            )
            visible = unescape(
                re.sub(r"<[^>]+>", " ", visible)
            )
            visible = re.sub(r"\s+", " ", visible).strip()

            title_match = re.search(
                r"(?is)<title\b[^>]*>(.*?)</title>",
                text,
            )
            title = (
                unescape(
                    re.sub(r"<[^>]+>", " ", title_match.group(1))
                ).strip()
                if title_match
                else "(no page title)"
            )

            raise ValueError(
                "NMDB returned HTML without parseable measurement records.\n"
                f"Page title: {title}\n"
                f"Visible response start: {visible[:1500]}\n"
                f"Visible response end: {visible[-1500:]}"
            )

        preview = "\n".join(text.splitlines()[:30])

        raise ValueError(
            "Could not parse NMDB data.\n\n"
            "First lines returned by NMDB:\n"
            f"{preview}"
        )

    df = pd.DataFrame(rows)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
        errors="coerce",
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
        subset=["timestamp"],
        keep="last",
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