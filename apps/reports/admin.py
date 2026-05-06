from django.contrib import admin

from .models import Purchase


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("request", "actual_cost", "funding_source", "purchase_date", "created_at")
    search_fields = ("request__unit_name", "funding_source")
