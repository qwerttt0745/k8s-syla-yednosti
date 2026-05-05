from django.urls import path

from .views import export_report

urlpatterns = [
    path("", export_report, name="export"),
]

app_name = "reports"
