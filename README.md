# Архітектура ІС «Сила Єдності»

> Стек: **Python 3.12 · Django 5.x · PostgreSQL 16 · Bootstrap 5 · Docker · Git**
> Режим: **локально** (Docker Compose), опційно — AWS через Terraform

---

## 🗂 Дерево папок і файлів

```
syla-yednosti/                          ← корінь репозиторію
│
├── .git/
├── .gitignore
├── .env.example                        ← шаблон змінних оточення
├── .env                                ← (у .gitignore!) реальні секрети
├── README.md
├── Makefile                            ← зручні команди: make run, make migrate…
│
├── docker-compose.yml                  ← локальний запуск (web + db)
├── docker-compose.prod.yml             ← продакшн-конфіг (для AWS)
├── Dockerfile                          ← образ Django-додатку
│
├── manage.py
│
├── config/                             ── Django-проєкт (налаштування)
│   ├── __init__.py
│   ├── urls.py                         ← головний роутер
│   ├── wsgi.py
│   ├── asgi.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py                     ← спільні налаштування
│       ├── local.py                    ← локальна розробка (DEBUG=True)
│       └── production.py               ← продакшн (AWS)
│
├── apps/                               ── Django-застосунки
│   ├── __init__.py
│   │
│   ├── accounts/                       ── Auth Module (UC-03, FR-03, NFR-07)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── admin.py
│   │   ├── managers.py                 ← CustomUserManager
│   │   ├── models.py                   ← CustomUser (roles: VOLUNTEER / DIRECTOR)
│   │   ├── forms.py                    ← LoginForm
│   │   ├── views.py                    ← login_view, logout_view
│   │   ├── urls.py                     ← /login/, /logout/
│   │   └── migrations/
│   │       └── __init__.py
│   │
│   ├── applications/                   ── Ядро системи — заявки (UC-01, UC-02)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── admin.py
│   │   ├── models.py                   ← Request, Category, AuditLog, Comment
│   │   ├── forms.py                    ← RequestForm (IN-REQ), CommentForm
│   │   ├── views.py                    ← RequestController, DashboardView
│   │   ├── signals.py                  ← автозапис AuditLog при зміні статусу
│   │   ├── urls.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── filter_service.py       ← FilterService (FR-05): статус, категорія, бригада
│   │   │   ├── status_service.py       ← StatusService (FR-06): New→InProgress→Done→Canceled
│   │   │   └── validator.py            ← RequestValidator (FR-02): телефон, обов'язкові поля
│   │   └── migrations/
│   │       └── __init__.py
│   │
│   └── reports/                        ── Report Engine (FR-08, BG-03)
│       ├── __init__.py
│       ├── apps.py
│       ├── admin.py
│       ├── models.py                   ← Purchase (IN-BUY): вартість, чек, джерело
│       ├── forms.py                    ← PurchaseForm, ReportFilterForm
│       ├── views.py                    ← ReportEngine: генерація OUT-REP
│       ├── urls.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── excel_export.py         ← openpyxl: вигрузка в .xlsx (OUT-REP)
│       └── migrations/
│           └── __init__.py
│
├── templates/                          ── HTML-шаблони (Bootstrap 5)
│   ├── base.html                       ← базовий макет, підключення Bootstrap
│   ├── partials/
│   │   ├── _navbar.html
│   │   ├── _messages.html              ← flash-повідомлення Django
│   │   └── _footer.html
│   │
│   ├── accounts/
│   │   └── login.html                  ← /login/ (UC-03)
│   │
│   ├── applications/
│   │   ├── create_request.html         ← публічна форма (UC-01, FR-01) — БЕЗ авторизації
│   │   ├── request_success.html        ← підтвердження після відправки
│   │   ├── dashboard.html              ← дашборд волонтера (FR-04, FR-05)
│   │   ├── request_detail.html         ← деталі заявки + коментарі (FR-07)
│   │   └── request_list.html           ← повний список із фільтрами (FR-05, FR-09)
│   │
│   └── reports/
│       └── report_form.html            ← форма вибору діапазону дат (OUT-REP)
│
├── static/
│   ├── css/
│   │   └── main.css                    ← кастомні стилі поверх Bootstrap
│   ├── js/
│   │   └── main.js                     ← валідація форм на фронті (FR-02)
│   └── img/
│       └── .gitkeep
│
├── media/                              ← завантажені файли (фото чеків, документи)
│   └── .gitkeep
│
├── requirements/
│   ├── base.txt                        ← Django, psycopg2, openpyxl, pillow…
│   ├── local.txt                       ← + django-debug-toolbar
│   └── production.txt                  ← + gunicorn, whitenoise
│
└── terraform/                          ── AWS (піднімаємо за потребою)
    ├── main.tf                         ← EC2 + RDS + Security Groups
    ├── variables.tf
    ├── outputs.tf
    └── README.md
```

---

## ⚙️ Конфіг-файли

---

### `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python

# Django
*.log
local_settings.py
db.sqlite3
media/
staticfiles/

# Env
.env
.env.*
!.env.example

# Docker
*.env

# IDEs
.vscode/
.idea/
*.swp
*.swo

# macOS
.DS_Store

# Terraform
terraform/.terraform/
terraform/*.tfstate
terraform/*.tfstate.backup
terraform/.terraform.lock.hcl
```

---

### `.env.example`

```dotenv
# Django
DJANGO_SECRET_KEY=your-very-secret-key-change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=syla_yednosti
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Django settings module
DJANGO_SETTINGS_MODULE=config.settings.local
```

---

### `docker-compose.yml`

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: .
    restart: unless-stopped
    command: >
      sh -c "python manage.py migrate --noinput &&
             python manage.py collectstatic --noinput &&
             python manage.py runserver 0.0.0.0:8000"
    volumes:
      - .:/app
      - media_data:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
  media_data:
```

---

### `Dockerfile`

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Системні залежності
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python залежності
COPY requirements/base.txt requirements/base.txt
COPY requirements/local.txt requirements/local.txt
RUN pip install --no-cache-dir -r requirements/local.txt

COPY . .

EXPOSE 8000
```

---

### `Makefile`

```makefile
.PHONY: run stop build migrate superuser shell logs restart

run:
	docker compose up

build:
	docker compose up --build

stop:
	docker compose down

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

superuser:
	docker compose exec web python manage.py createsuperuser

shell:
	docker compose exec web python manage.py shell

logs:
	docker compose logs -f web

restart:
	docker compose restart web

test:
	docker compose exec web python manage.py test
```

---

### `requirements/base.txt`

```txt
Django>=5.0,<5.2
psycopg2-binary>=2.9
python-decouple>=3.8
Pillow>=10.0          # завантаження фото чеків (Purchase.receipt_photo)
openpyxl>=3.1         # генерація Excel-звіту (ReportEngine, OUT-REP)
```

---

### `requirements/local.txt`

```txt
-r base.txt
django-debug-toolbar>=4.0
```

---

### `requirements/production.txt`

```txt
-r base.txt
gunicorn>=21.0
whitenoise>=6.6       # роздача статики без nginx
```

---

### `config/settings/base.py`

```python
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY")
DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="localhost").split(",")

# Застосунки
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Власні
    "apps.accounts",
    "apps.applications",
    "apps.reports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",       # NFR-09: CSRF-захист
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# База даних — PostgreSQL (NFR-05, NFR-06)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="db"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# Кастомна модель користувача (Auth Module)
AUTH_USER_MODEL = "accounts.CustomUser"
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/login/"

# Паролі (NFR-07: хешування)
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uk"
TIME_ZONE = "Europe/Kyiv"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

---

### `config/settings/local.py`

```python
from .base import *  # noqa

DEBUG = True

INSTALLED_APPS += ["debug_toolbar"]  # noqa

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa

INTERNAL_IPS = ["127.0.0.1"]
```

---

### `config/settings/production.py`

```python
from .base import *  # noqa

DEBUG = False

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# NFR-07: HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
```

---

### `config/urls.py`

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.accounts.urls")),       # /login/, /logout/
    path("", include("apps.applications.urls")),   # /, /dashboard/, /requests/
    path("reports/", include("apps.reports.urls")),# /reports/export/
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

### `manage.py`

```python
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
```

---

### `apps/accounts/models.py`

```python
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Auth Module. Ролі: VOLUNTEER (волонтер), DIRECTOR (директор).
    Логін — email (унікальний індекс, NFR-08 / FR-03).
    Паролі — хешовані Django (NFR-07).
    """

    class Role(models.TextChoices):
        VOLUNTEER = "VOLUNTEER", "Волонтер"
        DIRECTOR  = "DIRECTOR",  "Директор"

    email    = models.EmailField(unique=True)
    role     = models.CharField(max_length=10, choices=Role.choices, default=Role.VOLUNTEER)
    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"

    def __str__(self):
        return self.email

    @property
    def is_director(self):
        return self.role == self.Role.DIRECTOR
```

---

### `apps/accounts/managers.py`

```python
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email є обов'язковим")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "DIRECTOR")
        return self.create_user(email, password, **extra_fields)
```

---

### `apps/accounts/views.py`

```python
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import LoginForm


def login_view(request):
    """UC-03: Авторизація. Хешування + сесія."""
    if request.user.is_authenticated:
        return redirect("applications:dashboard")

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        if user:
            login(request, user)
            return redirect("applications:dashboard")
        form.add_error(None, "Невірний email або пароль")

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("accounts:login")
```

---

### `apps/accounts/urls.py`

```python
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/",  views.login_view,  name="login"),
    path("logout/", views.logout_view, name="logout"),
]
```

---

### `apps/accounts/forms.py`

```python
from django import forms


class LoginForm(forms.Form):
    email    = forms.EmailField(label="Email", widget=forms.EmailInput(
        attrs={"class": "form-control", "placeholder": "volunteer@example.com"}
    ))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(
        attrs={"class": "form-control"}
    ))
```

---

### `apps/applications/models.py`

```python
from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    """Категорія потреби: Дрони, Медицина, Авто тощо."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Request(models.Model):
    """
    Центральна сутність системи — заявка (IN-REQ).
    Відповідає таблиці 2.2 курсової роботи.
    """

    class Status(models.TextChoices):
        NEW         = "NEW",         "Нова"
        IN_PROGRESS = "IN_PROGRESS", "В обробці"
        DONE        = "DONE",        "Виконано"
        CANCELED    = "CANCELED",    "Скасовано"

    class Priority(models.TextChoices):
        LOW      = "LOW",      "Низький"
        MEDIUM   = "MEDIUM",   "Середній"
        CRITICAL = "CRITICAL", "Критичний"

    # Дані заявника (IN-REQ)
    user_name  = models.CharField(max_length=100, verbose_name="ПІБ")
    phone      = models.CharField(max_length=13,  verbose_name="Телефон")       # +380...
    unit_name  = models.CharField(max_length=150, verbose_name="Підрозділ")
    category   = models.ForeignKey(Category, on_delete=models.PROTECT,
                                   verbose_name="Категорія")
    item_name  = models.TextField(max_length=500, verbose_name="Що потрібно")
    quantity   = models.PositiveIntegerField(verbose_name="Кількість")
    priority   = models.CharField(max_length=10,  choices=Priority.choices,
                                   default=Priority.MEDIUM, verbose_name="Терміновість")
    location   = models.CharField(max_length=100, verbose_name="Населений пункт")
    post_dept  = models.PositiveIntegerField(verbose_name="Відділення НП")

    # Статус і відповідальний
    status       = models.CharField(max_length=15, choices=Status.choices,
                                     default=Status.NEW, db_index=True)
    assigned_to  = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      null=True, blank=True,
                                      on_delete=models.SET_NULL,
                                      related_name="assigned_requests")

    # Часові мітки (з урахуванням часового поясу, NFR per 3.3.3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]   # нові зверху (FR-04)
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"#{self.pk} — {self.unit_name} ({self.get_status_display()})"


class Comment(models.Model):
    """
    FR-07: Внутрішні нотатки волонтера.
    Військовий їх НЕ бачить.
    """
    request    = models.ForeignKey(Request, on_delete=models.CASCADE,
                                   related_name="comments")
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class AuditLog(models.Model):
    """
    Журнал аудиту — автоматично через signals.py.
    Фіксує: хто, коли, який статус змінив (розділ 3.3.4 курсової).
    """
    request     = models.ForeignKey(Request, on_delete=models.CASCADE,
                                     related_name="audit_logs")
    changed_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                     null=True)
    old_status  = models.CharField(max_length=15)
    new_status  = models.CharField(max_length=15)
    changed_at  = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-changed_at"]
```

---

### `apps/applications/signals.py`

```python
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Request, AuditLog


@receiver(pre_save, sender=Request)
def log_status_change(sender, instance, **kwargs):
    """Автоматичний запис в AuditLog при зміні статусу (розділ 3.3.4)."""
    if not instance.pk:
        return
    try:
        old = Request.objects.get(pk=instance.pk)
    except Request.DoesNotExist:
        return
    if old.status != instance.status:
        AuditLog.objects.create(
            request=instance,
            changed_by=getattr(instance, "_changed_by", None),
            old_status=old.status,
            new_status=instance.status,
        )
```

---

### `apps/applications/forms.py`

```python
from django import forms
from .models import Request, Comment


class RequestForm(forms.ModelForm):
    """
    FR-01 / FR-02: Публічна форма подачі заявки (IN-REQ).
    Валідація телефону +380... на фронті (main.js) і бекенді.
    """

    class Meta:
        model = Request
        fields = [
            "user_name", "phone", "unit_name", "category",
            "item_name", "quantity", "priority", "location", "post_dept",
        ]
        widgets = {
            "user_name":  forms.TextInput(attrs={"class": "form-control", "placeholder": "Іванченко І.В."}),
            "phone":      forms.TextInput(attrs={"class": "form-control", "placeholder": "+380XXXXXXXXX", "type": "tel"}),
            "unit_name":  forms.TextInput(attrs={"class": "form-control", "placeholder": "72 ОМБр, 2 бат"}),
            "category":   forms.Select(attrs={"class": "form-select"}),
            "item_name":  forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "quantity":   forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "priority":   forms.Select(attrs={"class": "form-select"}),
            "location":   forms.TextInput(attrs={"class": "form-control"}),
            "post_dept":  forms.NumberInput(attrs={"class": "form-control"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if not phone.startswith("+380") or len(phone) != 13:
            raise forms.ValidationError("Формат: +380XXXXXXXXX (13 символів)")
        if not phone[1:].isdigit():
            raise forms.ValidationError("Телефон може містити лише цифри після +")
        return phone


class CommentForm(forms.ModelForm):
    """FR-07: Внутрішня нотатка волонтера."""

    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {"text": forms.Textarea(attrs={"class": "form-control", "rows": 2,
                                                  "placeholder": "Внутрішня нотатка..."})}
```

---

### `apps/applications/services/status_service.py`

```python
from apps.applications.models import Request


# FR-06: Дозволені переходи статусу
ALLOWED_TRANSITIONS = {
    Request.Status.NEW:         [Request.Status.IN_PROGRESS, Request.Status.CANCELED],
    Request.Status.IN_PROGRESS: [Request.Status.DONE, Request.Status.CANCELED],
    Request.Status.DONE:        [],
    Request.Status.CANCELED:    [],
}


class StatusService:
    @staticmethod
    def can_transition(request_obj: Request, new_status: str) -> bool:
        return new_status in ALLOWED_TRANSITIONS.get(request_obj.status, [])

    @staticmethod
    def transition(request_obj: Request, new_status: str, changed_by) -> bool:
        if not StatusService.can_transition(request_obj, new_status):
            return False
        request_obj._changed_by = changed_by   # для AuditLog сигналу
        request_obj.status = new_status
        if new_status == Request.Status.IN_PROGRESS and not request_obj.assigned_to:
            request_obj.assigned_to = changed_by
        request_obj.save()
        return True
```

---

### `apps/applications/services/filter_service.py`

```python
from apps.applications.models import Request


class FilterService:
    """FR-05: Фільтрація заявок за статусом, категорією, бригадою."""

    @staticmethod
    def apply(queryset, params: dict):
        status    = params.get("status")
        category  = params.get("category")
        unit_name = params.get("unit_name")
        search    = params.get("search")      # FR-09: глобальний пошук

        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(category__slug=category)
        if unit_name:
            queryset = queryset.filter(unit_name__icontains=unit_name)
        if search:
            queryset = queryset.filter(
                user_name__icontains=search
            ) | queryset.filter(
                phone__icontains=search
            )
        return queryset
```

---

### `apps/applications/services/validator.py`

```python
import re


class RequestValidator:
    """FR-02: Серверна валідація (доповнює Django forms)."""

    PHONE_RE = re.compile(r"^\+380\d{9}$")

    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        return bool(cls.PHONE_RE.match(phone))

    @staticmethod
    def validate_quantity(qty) -> bool:
        try:
            return int(qty) > 0
        except (TypeError, ValueError):
            return False
```

---

### `apps/applications/views.py`

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Request, Category
from .forms import RequestForm, CommentForm
from .services.filter_service import FilterService
from .services.status_service import StatusService


def create_request(request):
    """UC-01 / FR-01: Публічна форма — авторизація НЕ потрібна."""
    form = RequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("applications:request_success")
    return render(request, "applications/create_request.html", {"form": form})


def request_success(request):
    return render(request, "applications/request_success.html")


@login_required
def dashboard(request):
    """UC-02 / FR-04: Дашборд волонтера — тільки для авторизованих."""
    qs = Request.objects.select_related("category", "assigned_to").all()
    qs = FilterService.apply(qs, request.GET)
    categories = Category.objects.all()
    return render(request, "applications/dashboard.html", {
        "requests": qs,
        "categories": categories,
        "statuses": Request.Status.choices,
    })


@login_required
def request_detail(request, pk):
    """Деталі заявки + коментарі (FR-07) + зміна статусу (FR-06)."""
    req = get_object_or_404(Request, pk=pk)
    comment_form = CommentForm(request.POST or None)

    if request.method == "POST":
        # Зміна статусу
        if "new_status" in request.POST:
            new_status = request.POST["new_status"]
            if StatusService.transition(req, new_status, request.user):
                messages.success(request, "Статус змінено")
            else:
                messages.error(request, "Недозволений перехід статусу")

        # Додавання коментаря
        elif comment_form.is_valid():
            c = comment_form.save(commit=False)
            c.request = req
            c.author = request.user
            c.save()

        return redirect("applications:request_detail", pk=pk)

    return render(request, "applications/request_detail.html", {
        "req": req,
        "comment_form": comment_form,
        "audit_logs": req.audit_logs.all(),
        "allowed_transitions": StatusService.ALLOWED_TRANSITIONS.get(req.status, []),
    })
```

---

### `apps/applications/urls.py`

```python
from django.urls import path
from . import views

app_name = "applications"

urlpatterns = [
    path("",               views.create_request, name="create_request"),   # UC-01
    path("success/",       views.request_success, name="request_success"),
    path("dashboard/",     views.dashboard,       name="dashboard"),        # UC-02
    path("requests/<int:pk>/", views.request_detail, name="request_detail"),
]
```

---

### `apps/reports/models.py`

```python
from django.db import models
from django.conf import settings
from apps.applications.models import Request


class Purchase(models.Model):
    """
    IN-BUY: Звіт про закупівлю (розділ 2.2.2 курсової).
    Прив'язується до заявки через FK.
    """
    request         = models.OneToOneField(Request, on_delete=models.CASCADE,
                                            related_name="purchase")
    actual_cost     = models.DecimalField(max_digits=12, decimal_places=2,
                                           verbose_name="Фактична вартість (грн)")
    purchase_date   = models.DateField(verbose_name="Дата чеку")
    funding_source  = models.CharField(max_length=200,
                                        verbose_name="Джерело фінансування")
    receipt_photo   = models.ImageField(upload_to="receipts/%Y/%m/",
                                         verbose_name="Фото чеку")
    created_by      = models.ForeignKey(settings.AUTH_USER_MODEL,
                                         on_delete=models.SET_NULL, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Закупівля"
        verbose_name_plural = "Закупівлі"
        ordering = ["-purchase_date"]
```

---

### `apps/reports/services/excel_export.py`

```python
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment


def generate_report(purchases, date_from, date_to) -> bytes:
    """
    FR-08 / OUT-REP: Генерація Excel-звіту для донорів.
    Структура відповідає розділу 2.2.3 курсової роботи.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Звіт"

    # Заголовок
    ws.merge_cells("A1:E1")
    ws["A1"] = f"Звіт БФ «Сила Єдності» за період {date_from} — {date_to}"
    ws["A1"].font = Font(bold=True, size=13)
    ws["A1"].alignment = Alignment(horizontal="center")

    # Шапка таблиці
    headers = ["Дата", "Підрозділ", "Що передано", "Категорія", "Сума (грн)"]
    header_fill = PatternFill(fill_type="solid", fgColor="1F497D")
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=3, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    # Дані
    total = 0
    for row_idx, p in enumerate(purchases, start=4):
        ws.cell(row=row_idx, column=1, value=p.purchase_date)
        ws.cell(row=row_idx, column=2, value=p.request.unit_name)
        ws.cell(row=row_idx, column=3, value=p.request.item_name[:100])
        ws.cell(row=row_idx, column=4, value=p.request.category.name)
        ws.cell(row=row_idx, column=5, value=float(p.actual_cost))
        total += p.actual_cost

    # Підсумки (Footer, розділ 2.2.3)
    last_row = len(list(purchases)) + 4
    ws.cell(row=last_row, column=4, value="Загальна сума:").font = Font(bold=True)
    ws.cell(row=last_row, column=5, value=float(total)).font = Font(bold=True)

    # Ширина колонок
    for col, width in zip(["A", "B", "C", "D", "E"], [14, 30, 50, 20, 16]):
        ws.column_dimensions[col].width = width

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
```

---

### `apps/reports/views.py`

```python
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .models import Purchase
from .services.excel_export import generate_report


@login_required
def export_report(request):
    """FR-08 / BG-03: Генерація Excel-звіту (OUT-REP). Лише для авторизованих."""
    date_from = request.GET.get("date_from", "")
    date_to   = request.GET.get("date_to",   "")

    if request.GET and date_from and date_to:
        purchases = Purchase.objects.filter(
            purchase_date__range=[date_from, date_to]
        ).select_related("request__category")

        data = generate_report(purchases, date_from, date_to)
        filename = f"report_{date_from}_{date_to}.xlsx"
        response = HttpResponse(
            data,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    return render(request, "reports/report_form.html", {
        "today": timezone.now().date(),
    })
```

---

### `apps/reports/urls.py`

```python
from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("export/", views.export_report, name="export"),
]
```

---

### `terraform/main.tf`

```hcl
# AWS-інфраструктура для ІС «Сила Єдності»
# Використати: terraform init && terraform apply

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# EC2 для Django
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0" # Ubuntu 22.04
  instance_type = var.instance_type
  key_name      = var.key_name

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io docker-compose
    systemctl start docker
    cd /app && docker compose -f docker-compose.prod.yml up -d
  EOF

  tags = {
    Name    = "syla-yednosti-web"
    Project = "syla-yednosti"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier        = "syla-yednosti-db"
  engine            = "postgres"
  engine_version    = "16"
  instance_class    = var.db_instance_class
  allocated_storage = 20
  db_name           = var.db_name
  username          = var.db_user
  password          = var.db_password
  skip_final_snapshot = true

  tags = {
    Name    = "syla-yednosti-db"
    Project = "syla-yednosti"
  }
}
```

---

### `terraform/variables.tf`

```hcl
variable "aws_region"       { default = "eu-central-1" }
variable "instance_type"    { default = "t3.micro" }
variable "key_name"         { description = "EC2 Key Pair name" }
variable "db_instance_class"{ default = "db.t3.micro" }
variable "db_name"          { default = "syla_yednosti" }
variable "db_user"          { default = "postgres" }
variable "db_password"      { sensitive = true }
```

---

### `terraform/outputs.tf`

```hcl
output "web_public_ip" {
  description = "Публічна IP-адреса EC2"
  value       = aws_instance.web.public_ip
}

output "db_endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.postgres.endpoint
}
```

---

## 🔗 Відповідність курсовій роботі

| Елемент курсової | Файл у проєкті |
|---|---|
| FR-01 Подача заявки | `applications/views.py → create_request()` |
| FR-02 Валідація | `applications/forms.py → clean_phone()` + `services/validator.py` |
| FR-03 Авторизація (UC-03) | `accounts/views.py → login_view()` |
| FR-04 Реєстр (Dashboard) | `applications/views.py → dashboard()` |
| FR-05 Фільтрація | `applications/services/filter_service.py` |
| FR-06 Зміна статусу | `applications/services/status_service.py` |
| FR-07 Коментарі | `applications/models.py → Comment` |
| FR-08 Експорт Excel | `reports/services/excel_export.py` |
| NFR-07 HTTPS | `config/settings/production.py` |
| NFR-08 SQL-ін'єкції | Django ORM (вбудовано) |
| NFR-09 CSRF | `MIDDLEWARE → CsrfViewMiddleware` |
| IN-REQ (таблиця 2.2) | `applications/models.py → Request` |
| IN-BUY (розділ 2.2.2) | `reports/models.py → Purchase` |
| OUT-REP (розділ 2.2.3) | `reports/services/excel_export.py` |
| AuditLog (розділ 3.3.4) | `applications/models.py → AuditLog` + `signals.py` |
| Auth Module (діаграма 3.1) | `apps/accounts/` |
| RequestController | `applications/views.py` |
| FilterService | `applications/services/filter_service.py` |
| StatusService | `applications/services/status_service.py` |
| ReportEngine | `reports/views.py` + `reports/services/` |
