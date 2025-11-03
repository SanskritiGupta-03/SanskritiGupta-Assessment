from django.urls import path, re_path
from . import views

urlpatterns = [
    # UI pages
    path("", views.ui_home, name="ui_home"),
    path("app/task1-revenue-booking/", views.ui_task1_revenue_booking, name="ui_task1_revenue_booking"),
    path("app/task2-service-ops/", views.ui_task2_service_ops, name="ui_task2_service_ops"),

    # API endpoints
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
