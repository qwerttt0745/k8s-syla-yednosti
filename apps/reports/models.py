from django.conf import settings
from django.db import models

from apps.applications.models import Request


class Purchase(models.Model):
    request = models.OneToOneField(Request, on_delete=models.CASCADE, related_name="purchase")
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()
    funding_source = models.CharField(max_length=255)
    receipt_photo = models.ImageField(upload_to="receipts/", blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchases",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.request_id} - {self.actual_cost}"
