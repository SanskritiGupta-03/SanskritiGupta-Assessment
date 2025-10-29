from __future__ import annotations
from datetime import date
from collections import defaultdict
from typing import Dict, List, Tuple

from django.db.models import Sum
from core.models_ft import FinancialTransaction as FT
from core.models import Booking
from core.helpers import ensure_range, fill_missing_dates, clamp_outliers_iqr

def revenue_series(resort:str|None, d1:date|None, d2:date|None) -> Dict[date, float]:
    d1, d2 = ensure_range(d1, d2, default_days=365)
    qs = FT.objects.filter(business_date__gte=d1, business_date__lte=d2)
    if resort:
        qs = qs.filter(resort=resort)
    bucket: Dict[date, float] = defaultdict(float)
    for r in qs.values("business_date").annotate(
        revenue=Sum("revenue_amt"),
        net=Sum("net_amount"),
    ):
        dt = r["business_date"]
        rev = r["revenue"] if r["revenue"] is not None else r["net"]
        bucket[dt] += float(rev or 0.0)
    return fill_missing_dates(bucket, d1, d2)

def bookings_series(d1:date|None, d2:date|None) -> Dict[date, int]:
    d1, d2 = ensure_range(d1, d2, default_days=365)
    qs = Booking.objects.filter(checkin_date__gte=d1, checkin_date__lte=d2)
    bucket: Dict[date, int] = defaultdict(int)
    for r in qs.values_list("checkin_date", flat=True):
        bucket[r] += 1
    return fill_missing_dates(bucket, d1, d2)

def avg_revenue_per_booking(rev:Dict[date,float], bks:Dict[date,int]) -> Dict[date, float]:
    out = {}
    for dt, r in rev.items():
        denom = bks.get(dt, 0)
        out[dt] = (r / denom) if denom > 0 else 0.0

    clamped = clamp_outliers_iqr(list(out.values()))
    return {k: clamped[i] for i, k in enumerate(out.keys())}

def model_ready_rows(rev:Dict[date,float], bks:Dict[date,int]) -> List[dict]:
    """Return rows ready for graph or feed to model."""
    rows = []
    for dt in sorted(rev.keys()):
        rows.append({
            "date": dt.isoformat(),
            "revenue": round(rev[dt], 2),
            "bookings": int(bks.get(dt, 0)),
            "avg_rev_per_booking": round(rev[dt]/max(bks.get(dt,0),1), 2)
        })
    return rows
