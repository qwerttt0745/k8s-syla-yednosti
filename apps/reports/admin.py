from django.contrib import admin

from .models import Purchase


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("title", "amount", "source", "created_at")
    search_fields = ("title", "source")
