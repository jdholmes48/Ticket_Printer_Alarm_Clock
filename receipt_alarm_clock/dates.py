from __future__ import annotations

from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python 3.8 can run without timezone conversion in preview mode.
    ZoneInfo = None  # type: ignore


def now_in_timezone(timezone_name: str) -> datetime:
    if ZoneInfo is None:
        return datetime.now()
    return datetime.now(ZoneInfo(timezone_name))
