from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils.dateparse import parse_date
from .models_ft import FinancialTransaction as FT

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
