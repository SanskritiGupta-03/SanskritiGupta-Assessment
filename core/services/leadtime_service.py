from __future__ import annotations
from datetime import date, datetime
from collections import defaultdict
from typing import Dict, List

from core.models import Booking
from core.helpers import ensure_range, fill_missing_dates

BUCKETS = ("early","standard","last_minute","very_late")

def bucket_for_lead(days:int) -> str:
    if days >= 30: return "early"
    if 7 <= days <= 29: return "standard"
    if 0 <= days <= 6: return "last_minute"
    return "very_late"

def leadtime_distribution(d1:date|None, d2:date|None) -> List[dict]:
    d1, d2 = ensure_range(d1, d2, default_days=365)

    qs = Booking.objects.filter(checkin_date__gte=d1, checkin_date__lte=d2)\
                        .values("created_ts", "checkin_date")

    dist = defaultdict(lambda: {b:0 for b in BUCKETS} | {"total":0})
    for r in qs:
        created = r["created_ts"].date() if isinstance(r["created_ts"], datetime) else r["created_ts"]
        checkin = r["checkin_date"]
        if not created or not checkin:
            continue
        lead = (checkin - created).days
        bucket = bucket_for_lead(lead)
        dist[checkin][bucket] += 1
        dist[checkin]["total"] += 1

    _ = fill_missing_dates({k:v["total"] for k,v in dist.items()}, d1, d2)  
    for dt in _:
        dist.setdefault(dt, {b:0 for b in BUCKETS} | {"total":0})

    out = []
    for dt in sorted(dist.keys()):
        row = dist[dt]
        tot = row["total"] or 1
        out.append({
            "date": dt.isoformat(),
            "counts": {b: row[b] for b in BUCKETS},
            "share": {b: round(row[b]/tot, 4) for b in BUCKETS}
        })
    return out
