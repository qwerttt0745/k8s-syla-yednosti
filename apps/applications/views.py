from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, RequestForm
from .models import AuditLog, Category, Request
from .services.filter_service import FilterService
from .services.status_service import StatusService


def create_request(request):
    form = RequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("applications:request_success")
    return render(request, "applications/create_request.html", {"form": form})


def request_success(request):
    return render(request, "applications/request_success.html")


@login_required
def dashboard(request):
    queryset = Request.objects.select_related("category", "assigned_to").order_by("-created_at")
    queryset = FilterService.apply(
        queryset,
        status=request.GET.get("status") or None,
        category_slug=request.GET.get("category") or None,
        unit_name=request.GET.get("unit_name") or None,
        search=request.GET.get("search") or None,
    )
    categories = Category.objects.all().order_by("name")
    statuses = Request.Status.choices
    return render(
        request,
        "applications/dashboard.html",
        {"requests": queryset, "categories": categories, "statuses": statuses},
    )


@login_required
def request_detail(request, pk: int):
    req = get_object_or_404(Request.objects.select_related("category", "assigned_to"), pk=pk)
    comment_form = CommentForm(request.POST or None)

    if request.method == "POST" and request.POST.get("new_status"):
        try:
            StatusService.update_status(req, request.POST["new_status"], user=request.user)
            messages.success(request, "Статус оновлено")
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect("applications:request_detail", pk=req.pk)

    if request.method == "POST" and comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.request = req
        comment.author = request.user
        comment.save()
        messages.success(request, "Нотатку додано")
        return redirect("applications:request_detail", pk=req.pk)

    audit_logs = AuditLog.objects.filter(request=req).order_by("-changed_at")
    allowed_transitions = StatusService.allowed_transitions(req)

    return render(
        request,
        "applications/request_detail.html",
        {
            "req": req,
            "comment_form": comment_form,
            "allowed_transitions": allowed_transitions,
            "audit_logs": audit_logs,
        },
    )
