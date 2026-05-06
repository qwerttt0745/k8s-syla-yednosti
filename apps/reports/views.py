from datetime import date

from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.applications.models import Request
from apps.applications.services.status_service import StatusService
from .forms import PurchaseForm
from .models import Purchase
from .services.excel_export import generate_report


@login_required
def export_report(request):
    purchases = Purchase.objects.all().order_by("-created_at")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if date_from:
        purchases = purchases.filter(purchase_date__gte=date_from)
    if date_to:
        purchases = purchases.filter(purchase_date__lte=date_to)

    if date_from and date_to:
        output = generate_report(purchases, date_from, date_to)
        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = "attachment; filename=report.xlsx"
        return response

    return render(request, "reports/report_form.html", {"today": date.today().isoformat()})


@login_required
def purchase_create(request, request_pk):
    """
    UC-02 step 7: volunteer enters purchase data after buying (IN-BUY).
    After saving Purchase, status auto-transitions to DONE.
    """
    req = get_object_or_404(Request, pk=request_pk)

    if hasattr(req, "purchase"):
        django_messages.warning(request, "Дані закупівлі вже внесені для цієї заявки.")
        return redirect("applications:request_detail", pk=request_pk)

    if req.status != Request.Status.IN_PROGRESS:
        django_messages.error(
            request,
            "Дані можна вносити тільки для заявок зі статусом «В обробці».",
        )
        return redirect("applications:request_detail", pk=request_pk)

    if req.assigned_to and req.assigned_to != request.user:
        django_messages.error(request, "Цю заявку обробляє інший волонтер.")
        return redirect("applications:request_detail", pk=request_pk)

    form = PurchaseForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        purchase = form.save(commit=False)
        purchase.request = req
        purchase.created_by = request.user
        purchase.save()

        StatusService.transition(req, Request.Status.DONE, request.user)

        django_messages.success(
            request,
            "✅ Дані закупівлі збережено. Заявку позначено як виконану.",
        )
        return redirect("applications:request_detail", pk=request_pk)

    return render(
        request,
        "reports/purchase_form.html",
        {
            "form": form,
            "req": req,
        },
    )
