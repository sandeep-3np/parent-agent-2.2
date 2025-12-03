# app/utils/date_utils.py

from datetime import datetime
from typing import Optional
from dateutil import parser

# Explicit formats we want to support (priority order)
SUPPORTED_FORMATS = [
    "%m-%d-%Y",   # MM-DD-YYYY  ← Your LOS format
    "%Y-%m-%d",   # ISO (2025-05-01)
    "%d-%m-%Y",   # DD-MM-YYYY
    "%m/%d/%Y",   # MM/DD/YYYY
    "%Y/%m/%d",   # ISO with slashes
]


def parse_date(value) -> Optional[datetime]:
    """
    Robust date parser supporting multiple formats.
    Explicit MM-DD-YYYY support added to ensure LOS & credit report parsing.
    Falls back to dateutil parser for any other formats.
    Returns None if parsing fails.
    """
    if not value:
        return None

    # Already a datetime object
    if isinstance(value, datetime):
        return value

    value = str(value).strip()

    # Try explicit formats first (strict)
    for fmt in SUPPORTED_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except:
            pass

    # Fallback — flexible parser
    try:
        return parser.parse(value)
    except:
        return None


def months_between(d1, d2=None) -> int:
    """
    Returns the absolute number of full months between two dates.
    Used for seasoning calculations (Rule 19).
    """
    d1 = parse_date(d1)
    if d1 is None:
        raise ValueError(f"Invalid date: {d1}")

    d2 = datetime.now() if d2 is None else parse_date(d2)
    if d2 is None:
        raise ValueError(f"Invalid date: {d2}")

    # Full month difference
    return abs((d2.year - d1.year) * 12 + (d2.month - d1.month))


def days_between(d1, d2=None) -> int:
    """
    Returns the absolute day difference.
    Used for fraud / title checks (Rules 20, 21, 22).
    """
    d1 = parse_date(d1)
    if d1 is None:
        raise ValueError("Invalid d1")

    d2 = datetime.now() if d2 is None else parse_date(d2)
    if d2 is None:
        raise ValueError("Invalid d2")

    return abs((d2 - d1).days)
