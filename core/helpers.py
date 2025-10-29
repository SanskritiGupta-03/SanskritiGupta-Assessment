from __future__ import annotations
from datetime import date, timedelta
from typing import List, Dict, Tuple, Optional
import math

from django.utils.dateparse import parse_date

try:
    import pandas as pd
except Exception:
    pd = None  


def parse_dates(request) -> Tuple[Optional[date], Optional[date]]:
    d1 = parse_date(request.GET.get("date_from") or "")
    d2 = parse_date(request.GET.get("date_to") or "")
    return d1, d2

def group_param(request) -> str:
    grp = (request.GET.get("grp") or "day").lower()
    return grp if grp in ("day", "week", "month") else "day"

def period_key(dt: date, grp: str) -> str:
    """YYYY-MM-DD / YYYY-Www / YYYY-MM."""
    if grp == "day":
        return dt.strftime("%Y-%m-%d")
    if grp == "week":
        y, w, _ = dt.isocalendar()
        return f"{y}-W{w:02d}"
    if grp == "month":
        return dt.strftime("%Y-%m")
    return dt.strftime("%Y-%m-%d")

def ensure_range(d1: Optional[date], d2: Optional[date], default_days: int = 365) -> Tuple[date, date]:
    """Guarantee a date range; default to last N days if not provided."""
    today = date.today()
    if not d2:
        d2 = today
    if not d1:
        d1 = d2 - timedelta(days=default_days)
    if d1 > d2:
        d1, d2 = d2, d1
    return d1, d2

def clamp_outliers_iqr(values: List[float]) -> List[float]:
    """Clamp to [Q1-1.5*IQR, Q3+1.5*IQR] to reduce spikes for plots/models."""
    xs = [v for v in values if v is not None and not math.isnan(v)]
    if len(xs) < 4:
        return values
    xs_sorted = sorted(xs)
    q1 = xs_sorted[len(xs_sorted)//4]
    q3 = xs_sorted[(len(xs_sorted)*3)//4]
    iqr = max(q3 - q1, 1e-9)
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return [min(max(v, lo), hi) if v is not None else None for v in values]

def fill_missing_dates(series: Dict[date, float], d1: date, d2: date, fill: float = 0.0) -> Dict[date, float]:
    cur = d1
    out: Dict[date, float] = {}
    while cur <= d2:
        out[cur] = series.get(cur, fill)
        cur += timedelta(days=1)
    return out

def to_dataframe(rows: List[dict], order: List[str] | None = None):
    if pd is None:
        raise RuntimeError("pandas not installed. pip install pandas openpyxl")
    df = pd.DataFrame(rows)
    if order:
        df = df[[c for c in order if c in df.columns]]
    return df

def export_excel(path: str, sheets: Dict[str, List[dict]], orders: Dict[str, List[str]] | None = None) -> str:
    """Write multiple sheets to an xlsx file. `sheets` is {sheet_name: list_of_dicts}."""
    if pd is None:
        raise RuntimeError("pandas/openpyxl required to export Excel.")
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, data in sheets.items():
            df = to_dataframe(data, (orders or {}).get(name))
            df.to_excel(writer, index=False, sheet_name=name[:31])  # Excel sheet name limit
    return path
