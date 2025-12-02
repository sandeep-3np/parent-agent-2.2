# app/utils/date_utils.py
from datetime import datetime
from dateutil import parser
from typing import Optional

def parse_date(s) -> Optional[datetime]:
    if not s:
        return None
    if isinstance(s, datetime):
        return s
    try:
        return parser.parse(str(s))
    except Exception:
        return None

def months_between(d1, d2=None) -> int:
    """
    Returns months difference from d1 to d2. If d2 is None, compares to now.
    Positive if d2 later than d1.
    """
    d1 = parse_date(d1)
    if d1 is None:
        raise ValueError("Invalid d1")
    if d2 is None:
        d2 = datetime.now()
    d2 = parse_date(d2)
    if d2 is None:
        raise ValueError("Invalid d2")
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)

def days_between(d1, d2=None) -> int:
    d1 = parse_date(d1)
    if d1 is None:
        raise ValueError("Invalid d1")
    if d2 is None:
        d2 = datetime.now()
    d2 = parse_date(d2)
    delta = d2 - d1
    return delta.days
