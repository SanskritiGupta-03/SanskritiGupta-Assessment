import os
from django.shortcuts import render
from collections import defaultdict
from datetime import datetime, date

from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_GET

from .models_ft import FinancialTransaction as FT
from .models import InventoryDay, Booking

from .helpers import parse_dates, ensure_range, export_excel, group_param, period_key
from .services.revenue_service import revenue_series, bookings_series, avg_revenue_per_booking, model_ready_rows
from .services.cancellation_service import canc_noshow_series
from .services.leadtime_service import leadtime_distribution
from .services.forecast_service import arima_forecast_series

@require_GET
def ft_summary(request):
    """
    GET /api/ft/summary?resort=XYZ&date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
    """
    resort = request.GET.get("resort")
    d1 = parse_date(request.GET.get("date_from") or "")
    d2 = parse_date(request.GET.get("date_to") or "")

    qs = FT.objects.all()
    if resort:
        qs = qs.filter(resort=resort)
    if d1:
        qs = qs.filter(business_date__gte=d1)
    if d2:
        qs = qs.filter(business_date__lte=d2)

    agg = qs.aggregate(
        rows=Count("pkid"),
        revenue=Sum("revenue_amt"),
        gross=Sum("gross_amount"),
        net=Sum("net_amount"),
        non_revenue=Sum("non_revenue_amount"),
    )
    out = {k: (float(v) if v is not None else 0.0) for k, v in agg.items()}
    return JsonResponse(out)

@require_GET
def ft_timeseries_revenue(request):
    """
    GET /api/ft/timeseries/revenue?resort=XYZ&date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
    """
    resort = request.GET.get("resort")
    d1 = parse_date(request.GET.get("date_from") or "")
    d2 = parse_date(request.GET.get("date_to") or "")

    qs = FT.objects.values("business_date")
    if resort:
        qs = qs.filter(resort=resort)
    if d1:
        qs = qs.filter(business_date__gte=d1)
    if d2:
        qs = qs.filter(business_date__lte=d2)

    rows = (
        qs.annotate(
            revenue=Sum("revenue_amt"),
            gross=Sum("gross_amount"),
            net=Sum("net_amount"),
        )
        .order_by("business_date")
    )

    data = [
        {
            "date": r["business_date"].isoformat(),
            "revenue": float(r["revenue"] or 0),
            "gross": float(r["gross"] or 0),
            "net": float(r["net"] or 0),
        }
        for r in rows
    ]
    return JsonResponse({"series": data})

@require_GET
def trends_occupancy(request):
    """
    GET /api/trends/occupancy?location_id=<id>&date_from=YYYY-MM-DD&date_to=YYYY-MM-DD&grp=day|week|month
    """
    grp = group_param(request)
    d1, d2 = parse_dates(request)
    location_id = request.GET.get("location_id")

    qs = InventoryDay.objects.all()
    if location_id:
        qs = qs.filter(location_id=location_id)
    if d1:
        qs = qs.filter(date__gte=d1)
    if d2:
        qs = qs.filter(date__lte=d2)

    bucket = defaultdict(lambda: {"capacity": 0, "occupied": 0})
    for row in qs.values("date", "capacity", "occupied"):
        key = period_key(row["date"], grp)
        bucket[key]["capacity"] += int(row["capacity"] or 0)
        bucket[key]["occupied"] += int(row["occupied"] or 0)

    series = []
    for k in sorted(bucket.keys()):
        cap = bucket[k]["capacity"] or 0
        occ = bucket[k]["occupied"] or 0
        rate = (occ / cap) if cap > 0 else 0.0
        series.append({
            "period": k,
            "capacity": cap,
            "occupied": occ,
            "occupancy_rate": round(rate, 4),
        })
    return JsonResponse({"series": series})

@require_GET
def trends_booking_rate(request):
    """
    GET /api/trends/booking_rate?date_from=&date_to=&grp=day|week|month
    - Counts bookings by check-in date (arrival-based).
    - Returns series + weekday/month seasonality averages.
    """
    grp = group_param(request)
    d1, d2 = parse_dates(request)

    qs = Booking.objects.all()
    if d1:
        qs = qs.filter(checkin_date__gte=d1)
    if d2:
        qs = qs.filter(checkin_date__lte=d2)

    bucket = defaultdict(int)
    # Seasonality
    weekday_counts = [0]*7
    weekday_days = [0]*7
    month_counts = [0]*12
    month_days = [0]*12

    for b in qs.values("checkin_date"):
        dt = b["checkin_date"]
        key = period_key(dt, grp)
        bucket[key] += 1

        wd = dt.weekday()  
        weekday_counts[wd] += 1
        weekday_days[wd] += 1

        m = dt.month - 1  
        month_counts[m] += 1
        month_days[m] += 1

    series = [{"period": k, "bookings": bucket[k]} for k in sorted(bucket.keys())]

    # simple average per weekday/month 
    weekday_avg = []
    for i in range(7):
        denom = max(weekday_days[i], 1)
        weekday_avg.append(round(weekday_counts[i] / denom, 4))

    month_avg = []
    for i in range(12):
        denom = max(month_days[i], 1)
        month_avg.append(round(month_counts[i] / denom, 4))

    return JsonResponse({"series": series, "weekday_avg": weekday_avg, "month_avg": month_avg})

@require_GET
def trends_revenue(request):
    """
    GET /api/trends/revenue?resort=XYZ&date_from=&date_to=&grp=day|week|month
    - Uses FinancialTransaction.revenue_amt (fallback to net_amount).
    - Computes avg_rev_per_booking and (if available) per_customer.
    """
    grp = group_param(request)
    d1, d2 = parse_dates(request)
    resort = request.GET.get("resort")

    ft = FT.objects.all()
    if resort:
        ft = ft.filter(resort=resort)
    if d1:
        ft = ft.filter(business_date__gte=d1)
    if d2:
        ft = ft.filter(business_date__lte=d2)

    revenue_by_day = defaultdict(float)
    for r in ft.values("business_date", "revenue_amt", "net_amount"):
        dt = r["business_date"]
        key = period_key(dt, grp)
        rev = r["revenue_amt"] if r["revenue_amt"] is not None else r["net_amount"]
        revenue_by_day[key] += float(rev or 0.0)

    # bookings per same period (arrival-based)
    bk = Booking.objects.all()
    if d1:
        bk = bk.filter(checkin_date__gte=d1)
    if d2:
        bk = bk.filter(checkin_date__lte=d2)
    bookings_by_day = defaultdict(int)
    customers_by_day = defaultdict(set)

    has_customer = "customer_id" in [f.name for f in Booking._meta.get_fields()]
    fields = ["checkin_date", "id"]
    if has_customer:
        fields.append("customer_id")

    for b in bk.values(*fields):
        dt = b["checkin_date"]
        key = period_key(dt, grp)
        bookings_by_day[key] += 1
        if has_customer:
            cid = b.get("customer_id")
            if cid:
                customers_by_day[key].add(cid)

    
    keys = sorted(set(revenue_by_day.keys()) | set(bookings_by_day.keys()))
    series = []
    for k in keys:
        rev = revenue_by_day.get(k, 0.0)
        bks = bookings_by_day.get(k, 0)
        arb = (rev / bks) if bks > 0 else 0.0  
        if has_customer:
            uniq = len(customers_by_day.get(k, set()))
            arc = (rev / uniq) if uniq > 0 else 0.0
        else:
            arc = None
        series.append({
            "period": k,
            "revenue": round(rev, 2),
            "bookings": bks,
            "avg_rev_per_booking": round(arb, 2),
            "avg_rev_per_customer": (round(arc, 2) if arc is not None else None),
        })

    return JsonResponse({"series": series})

@require_GET
def trends_cancellations(request):
    """
    GET /api/trends/cancellations?date_from=&date_to=&grp=day|week|month&basis=created|confirmed|all
    - Counts cancellations and no-shows by check-in date.
    - Rates computed vs denominator basis:
        created   -> number of bookings created in that period
        confirmed -> number of bookings with status in (CONFIRMED, COMPLETED)
        all       -> total bookings
    """
    grp = group_param(request)
    d1, d2 = parse_dates(request)
    basis = (request.GET.get("basis") or "all").lower()
    if basis not in ("created", "confirmed", "all"):
        basis = "all"

    qs = Booking.objects.all()
    if d1:
        qs = qs.filter(checkin_date__gte=d1)
    if d2:
        qs = qs.filter(checkin_date__lte=d2)

    canc_by = defaultdict(int)
    noshow_by = defaultdict(int)
    denom_by = defaultdict(int)

    for b in qs.values("checkin_date", "status", "cancellation_flag", "no_show_flag", "created_ts"):
        dt = b["checkin_date"]
        key = period_key(dt, grp)

        is_cancel = (b["status"] == "CANCELLED") or bool(b["cancellation_flag"])
        is_noshow = (b["status"] == "NO_SHOW") or bool(b["no_show_flag"])

        if is_cancel:
            canc_by[key] += 1
        if is_noshow:
            noshow_by[key] += 1

        if basis == "created":
            denom_by[key] += 1
        elif basis == "confirmed":
            denom_by[key] += 1 if b["status"] in ("CONFIRMED", "COMPLETED") else 0
        else:
            denom_by[key] += 1

    keys = sorted(set(denom_by.keys()) | set(canc_by.keys()) | set(noshow_by.keys()))
    series = []
    for k in keys:
        denom = denom_by.get(k, 0)
        c = canc_by.get(k, 0)
        n = noshow_by.get(k, 0)
        series.append({
            "period": k,
            "denominator": denom,
            "cancelled": c,
            "no_show": n,
            "cancel_rate": round(c/denom, 4) if denom else 0.0,
            "no_show_rate": round(n/denom, 4) if denom else 0.0,
        })
    return JsonResponse({"series": series, "basis": basis})

@require_GET
def trends_lead_time(request):
    """
    GET /api/trends/lead_time?date_from=&date_to=&grp=day|week|month
    Buckets:
      early >= 30 days
      standard 7-29
      last_minute 0-6
      very_late <0 (created after checkin; data quality)
    """
    grp = group_param(request)
    d1, d2 = parse_dates(request)

    qs = Booking.objects.all().values("created_ts", "checkin_date")
    if d1:
        qs = qs.filter(checkin_date__gte=d1)
    if d2:
        qs = qs.filter(checkin_date__lte=d2)

    dist = defaultdict(lambda: {"early":0, "standard":0, "last_minute":0, "very_late":0, "total":0})
    for b in qs:
        created = b["created_ts"].date() if isinstance(b["created_ts"], datetime) else b["created_ts"]
        checkin = b["checkin_date"]
        if not created or not checkin:
            continue
        lead = (checkin - created).days
        key = period_key(checkin, grp)

        if lead >= 30:
            bucket = "early"
        elif 7 <= lead <= 29:
            bucket = "standard"
        elif 0 <= lead <= 6:
            bucket = "last_minute"
        else:
            bucket = "very_late"

        dist[key][bucket] += 1
        dist[key]["total"] += 1

    series = []
    for k in sorted(dist.keys()):
        row = dist[k]
        tot = row["total"] or 1
        series.append({
            "period": k,
            "counts": {x: row[x] for x in ("early","standard","last_minute","very_late")},
            "share": {
                "early": round(row["early"]/tot, 4),
                "standard": round(row["standard"]/tot, 4),
                "last_minute": round(row["last_minute"]/tot, 4),
                "very_late": round(row["very_late"]/tot, 4),
            }
        })
    return JsonResponse({"series": series})

@require_GET
def prep_timeseries_dataset(request):
    """
    GET /api/prep/timeseries?resort=XYZ&months=6|12
    Returns cleaned, continuous daily rows for revenue/bookings/avg_rev.
    """
    resort = request.GET.get("resort")
    months = int(request.GET.get("months") or 12)
    days = max(28, min(370, months*30))

    d1, d2 = ensure_range(None, None, default_days=days)
    rev = revenue_series(resort, d1, d2)
    bks = bookings_series(d1, d2)
    rows = model_ready_rows(rev, bks)
    return JsonResponse({"rows": rows, "params": {"resort": resort, "date_from": d1.isoformat(), "date_to": d2.isoformat()}})

@require_GET
def export_year_excel(request):
    """
    GET /api/export/year_excel?resort=XYZ&year=2025
    Creates a multi-sheet xlsx branched across dates for a year.
    """
    resort = request.GET.get("resort")
    year = int(request.GET.get("year") or date.today().year)

    d1 = date(year, 1, 1)
    d2 = date(year, 12, 31)

    rev = revenue_series(resort, d1, d2)
    bks = bookings_series(d1, d2)
    rows = model_ready_rows(rev, bks)
    canc = canc_noshow_series(d1, d2, basis="all")
    lead = leadtime_distribution(d1, d2)

    sheets = {
        "RevenueDaily": rows,
        "Cancellations": canc,
        "LeadTime": lead,
    }
    orders = {
        "RevenueDaily": ["date","revenue","bookings","avg_rev_per_booking"],
        "Cancellations": ["date","denominator","cancelled","no_show","cancel_rate","no_show_rate"],
        "LeadTime": ["date","counts","share"],
    }

    path = f"/tmp/Trends_{resort or 'ALL'}_{year}.xlsx"
    url_path = export_excel(path, sheets, orders)  

    with open(url_path, "rb") as f:
        data = f.read()
    resp = HttpResponse(data, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = f'attachment; filename="{os.path.basename(url_path)}"'
    return resp

@require_GET
def forecast_revenue(request):
    """
    GET /api/forecast/revenue?resort=XYZ&months=12&horizon=56
    Clean last N months and run a simple ARIMA forecast.
    """
    resort = request.GET.get("resort")
    months = int(request.GET.get("months") or 12)
    horizon = int(request.GET.get("horizon") or 56)
    days = max(28, min(370, months*30))

    d1, d2 = ensure_range(None, None, default_days=days)
    res = arima_forecast_series(resort, d1, d2, horizon=horizon)
    return JsonResponse(res)

def ui_home(request):
    return render(request, "core/home.html")

def ui_task1_revenue_booking(request):
    return render(request, "core/task1_revenue_booking.html")

def ui_task2_service_ops(request):
    return render(request, "core/task2_service_ops.html")
