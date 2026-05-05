from datetime import date
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .models import Purchase
from .services.excel_export import build_workbook


@login_required
def export_report(request):
    purchases = Purchase.objects.all().order_by("-created_at")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if date_from:
        purchases = purchases.filter(created_at__date__gte=date_from)
    if date_to:
        purchases = purchases.filter(created_at__date__lte=date_to)

    if date_from and date_to:
        wb = build_workbook(purchases)
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = "attachment; filename=report.xlsx"
        return response

    return render(request, "reports/report_form.html", {"today": date.today().isoformat()})
