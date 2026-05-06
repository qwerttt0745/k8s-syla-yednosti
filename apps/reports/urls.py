from django.urls import path

from . import views

urlpatterns = [
    path("export/", views.export_report, name="export"),
    path("purchase/<int:request_pk>/", views.purchase_create, name="purchase_create"),
]

app_name = "reports"
