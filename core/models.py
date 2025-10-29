from django.db import models


class InventoryDay(models.Model):
    """Represents per-day capacity & occupancy data for a given location."""
    date = models.DateField()
    location_id = models.CharField(max_length=100, blank=True, null=True)
    capacity = models.IntegerField(default=0)
    occupied = models.IntegerField(default=0)

    class Meta:
        db_table = "inventory_day"
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["location_id"]),
        ]

    def __str__(self):
        return f"{self.date} - {self.location_id or 'N/A'}"


class Booking(models.Model):
    """Basic booking/reservation data."""
    checkin_date = models.DateField()
    created_ts = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, default="CONFIRMED")
    cancellation_flag = models.BooleanField(default=False)
    no_show_flag = models.BooleanField(default=False)
    customer_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "booking"
        indexes = [
            models.Index(fields=["checkin_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Booking {self.id} on {self.checkin_date}"
