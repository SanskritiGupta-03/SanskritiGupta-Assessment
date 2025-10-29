from django.urls import path, re_path
from django.http import JsonResponse
from . import views

def api_index(request):
    return JsonResponse({
        "ok": True,
        "message": "Welcome to the Analytics API",
        "available_endpoints": {
            "Financial Summary": "/api/ft/summary?resort=XYZ&date_from=YYYY-MM-DD&date_to=YYYY-MM-DD",
            "Revenue Trends": "/api/trends/revenue?resort=XYZ&grp=month",
            "Booking Rate Trends": "/api/trends/booking_rate?grp=week",
            "Occupancy Trends": "/api/trends/occupancy?grp=month",
            "Cancellations": "/api/trends/cancellations?grp=week",
            "Lead Time": "/api/trends/lead_time?grp=month",
            "Export Year Excel": "/api/export/year_excel?year=2025",
            "Forecast Revenue": "/api/forecast/revenue?horizon=56"
        }
    })

urlpatterns = [
    path("", api_index),
    re_path(r"^ft/summary/?$", views.ft_summary, name="ft_summary"),
    re_path(r"^ft/timeseries/revenue/?$", views.ft_timeseries_revenue, name="ft_timeseries_revenue"),

    re_path(r"^trends/occupancy/?$", views.trends_occupancy, name="trends_occupancy"),
    re_path(r"^trends/booking_rate/?$", views.trends_booking_rate, name="trends_booking_rate"),
    re_path(r"^trends/revenue/?$", views.trends_revenue, name="trends_revenue"),
    re_path(r"^trends/cancellations/?$", views.trends_cancellations, name="trends_cancellations"),
    re_path(r"^trends/lead_time/?$", views.trends_lead_time, name="trends_lead_time"),

    re_path(r"^prep/timeseries/?$", views.prep_timeseries_dataset, name="prep_timeseries_dataset"),
    re_path(r"^export/year_excel/?$", views.export_year_excel, name="export_year_excel"),
    re_path(r"^forecast/revenue/?$", views.forecast_revenue, name="forecast_revenue"),
]
