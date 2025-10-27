from django.urls import path
from . import views

urlpatterns = [
    path("api/ft/summary", views.ft_summary, name="ft_summary"),
    path("api/ft/timeseries/revenue", views.ft_timeseries_revenue, name="ft_timeseries_revenue"),
]
