from __future__ import annotations
from datetime import date
from collections import defaultdict
from typing import Dict, List

from core.models import Booking
from core.helpers import ensure_range, fill_missing_dates

def canc_noshow_series(d1:date|None, d2:date|None, basis:str="all") -> List[dict]:
    d1, d2 = ensure_range(d1, d2, default_days=365)
    qs = Booking.objects.filter(checkin_date__gte=d1, checkin_date__lte=d2)\
                        .values("checkin_date", "status", "cancellation_flag", "no_show_flag")

    canc = defaultdict(int)
    nosh = defaultdict(int)
    denom = defaultdict(int)

    for r in qs:
        dt = r["checkin_date"]
        is_cancel = (r["status"] == "CANCELLED") or bool(r["cancellation_flag"])
        is_noshow = (r["status"] == "NO_SHOW") or bool(r["no_show_flag"])
        if is_cancel: canc[dt] += 1
        if is_noshow: nosh[dt] += 1
        if basis == "confirmed":
            denom[dt] += 1 if r["status"] in ("CONFIRMED","COMPLETED") else 0
        else:
            denom[dt] += 1

    canc = fill_missing_dates(canc, d1, d2)
    nosh = fill_missing_dates(nosh, d1, d2)
    denom = fill_missing_dates(denom, d1, d2)

    out = []
    for dt in sorted(denom.keys()):
        d = denom[dt] or 1
        out.append({
            "date": dt.isoformat(),
            "denominator": int(denom[dt]),
            "cancelled": int(canc[dt]),
            "no_show": int(nosh[dt]),
            "cancel_rate": round(canc[dt]/d, 4),
            "no_show_rate": round(nosh[dt]/d, 4),
        })
    return out
