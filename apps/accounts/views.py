from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, VolunteerCreateForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("applications:dashboard")

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        if user is not None:
            login(request, user)
            return redirect("applications:dashboard")
        messages.error(request, "Невірний email або пароль")

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


def director_required(view_func):
    """Only allow directors to access a view."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_director:
            messages.error(request, "Доступ тільки для директора фонду.")
            return redirect("applications:dashboard")
        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
@director_required
def volunteer_list(request):
    from .models import CustomUser

    volunteers = CustomUser.objects.all().order_by("role", "email")
    return render(request, "accounts/volunteer_list.html", {"volunteers": volunteers})


@login_required
@director_required
def volunteer_create(request):
    form = VolunteerCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        from .models import CustomUser

        user = CustomUser.objects.create_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
            role=form.cleaned_data["role"],
        )
        messages.success(request, f"Користувача {user.email} створено успішно.")
        return redirect("accounts:volunteer_list")
    return render(request, "accounts/volunteer_form.html", {"form": form, "action": "Додати"})


@login_required
@director_required
def volunteer_toggle(request, pk):
    from .models import CustomUser

    user = get_object_or_404(CustomUser, pk=pk)
    if user == request.user:
        messages.error(request, "Не можна заблокувати самого себе.")
    else:
        user.is_active = not user.is_active
        user.save()
        status = "активовано" if user.is_active else "заблоковано"
        messages.success(request, f"Користувача {user.email} {status}.")
    return redirect("accounts:volunteer_list")
