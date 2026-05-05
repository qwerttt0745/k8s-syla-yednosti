# Інструкція для доробки ІС «Сила Єдності»

> **Важливо:** Спочатку виконай **Крок 0 — Аудит**, і тільки після цього переходь до решти.
> AWS / Terraform — видалити повністю, вони не потрібні.
> Уся система — **виключно українською мовою** (інтерфейс, повідомлення, підписи, адмінка).

---

## Крок 0 — Аудит: перевір що вже є

Пройдись по кожному пункту. Якщо файл відсутній або порожній — створи/заповни згідно з інструкцією нижче.

### Обов'язкові файли — перевір існування і непорожність:

```
syla-yednosti/
├── .gitignore                          ← має бути
├── .env.example                        ← має бути
├── docker-compose.yml                  ← має бути (тільки web + db, БЕЗ nginx)
├── Dockerfile                          ← має бути
├── Makefile                            ← має бути
├── manage.py                           ← має бути
│
├── config/
│   ├── __init__.py
│   ├── urls.py                         ← підключає accounts + applications + reports
│   ├── wsgi.py
│   ├── asgi.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py                     ← DATABASES, INSTALLED_APPS, AUTH_USER_MODEL
│       ├── local.py                    ← DEBUG=True, debug-toolbar
│       └── production.py              ← НЕ потрібен зараз, можна залишити порожнім
│
├── apps/
│   ├── accounts/
│   │   ├── models.py                   ← CustomUser з Role (VOLUNTEER/DIRECTOR)
│   │   ├── managers.py                 ← CustomUserManager
│   │   ├── forms.py                    ← LoginForm
│   │   ├── views.py                    ← login_view, logout_view
│   │   ├── urls.py                     ← /login/, /logout/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── migrations/__init__.py
│   │
│   ├── applications/
│   │   ├── models.py                   ← Request, Category, Comment, AuditLog
│   │   ├── forms.py                    ← RequestForm, CommentForm
│   │   ├── views.py                    ← create_request, dashboard, request_detail
│   │   ├── urls.py
│   │   ├── signals.py                  ← auto AuditLog при зміні статусу
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/__init__.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── filter_service.py
│   │       ├── status_service.py
│   │       └── validator.py
│   │
│   └── reports/
│       ├── models.py                   ← Purchase
│       ├── forms.py
│       ├── views.py                    ← export_report
│       ├── urls.py
│       ├── admin.py
│       ├── apps.py
│       ├── migrations/__init__.py
│       └── services/
│           ├── __init__.py
│           └── excel_export.py         ← openpyxl генерація .xlsx
│
├── templates/
│   ├── base.html
│   ├── partials/
│   │   ├── _navbar.html
│   │   └── _messages.html
│   ├── accounts/
│   │   └── login.html
│   ├── applications/
│   │   ├── create_request.html
│   │   ├── request_success.html
│   │   ├── dashboard.html
│   │   └── request_detail.html
│   └── reports/
│       └── report_form.html
│
├── static/
│   ├── css/main.css
│   └── js/main.js
│
├── media/.gitkeep
│
└── requirements/
    ├── base.txt
    ├── local.txt
    └── production.txt
```

**Після аудиту:** якщо якийсь файл відсутній — подивись на вміст у попередньому `architecture.md` і відтвори його. Якщо шаблони (templates/) порожні — заповни їх згідно з Кроком 1 нижче.

---

## Крок 1 — Видалити Terraform / AWS

- Видали папку `terraform/` повністю
- Видали `docker-compose.prod.yml` якщо є
- У `config/settings/` — файл `production.py` може залишитись порожнім або з мінімальним вмістом, він зараз не використовується
- У `docker-compose.yml` — переконайся що там тільки два сервіси: `db` і `web`

---

## Крок 2 — Шаблони (HTML + Bootstrap 5)

Всі шаблони — **Bootstrap 5**, всі написи — **українською**.
Кольорова схема статусів (з курсової роботи, Додаток B):
- `Нова` → `badge bg-danger` (червоний)
- `В обробці` → `badge bg-warning text-dark` (жовтий)
- `Виконано` → `badge bg-success` (зелений)
- `Скасовано` → `badge bg-secondary` (сірий)

---

### `templates/base.html`

```html
<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Сила Єдності{% endblock %}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
  {% load static %}
  <link rel="stylesheet" href="{% static 'css/main.css' %}">
</head>
<body>
  {% include 'partials/_navbar.html' %}
  {% include 'partials/_messages.html' %}

  <main class="container py-4">
    {% block content %}{% endblock %}
  </main>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  {% load static %}
  <script src="{% static 'js/main.js' %}"></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

---

### `templates/partials/_navbar.html`

```html
{% if user.is_authenticated %}
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container">
    <a class="navbar-brand fw-bold" href="{% url 'applications:dashboard' %}">
      <i class="bi bi-shield-fill-check me-2 text-warning"></i>Сила Єдності
    </a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navMenu">
      <ul class="navbar-nav me-auto">
        <li class="nav-item">
          <a class="nav-link" href="{% url 'applications:dashboard' %}">
            <i class="bi bi-grid-fill me-1"></i>Дашборд
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="{% url 'applications:create_request' %}">
            <i class="bi bi-plus-circle me-1"></i>Нова заявка
          </a>
        </li>
        {% if user.is_director %}
        <li class="nav-item">
          <a class="nav-link" href="{% url 'reports:export' %}">
            <i class="bi bi-file-earmark-excel me-1"></i>Звіт Excel
          </a>
        </li>
        {% endif %}
      </ul>
      <div class="d-flex align-items-center gap-3">
        <span class="text-light small">
          <i class="bi bi-person-circle me-1"></i>{{ user.email }}
          <span class="badge bg-secondary ms-1">{{ user.get_role_display }}</span>
        </span>
        <a href="{% url 'accounts:logout' %}" class="btn btn-outline-light btn-sm">
          <i class="bi bi-box-arrow-right me-1"></i>Вийти
        </a>
      </div>
    </div>
  </div>
</nav>
{% endif %}
```

---

### `templates/partials/_messages.html`

```html
{% if messages %}
<div class="container mt-3">
  {% for message in messages %}
  <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
    {{ message }}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  </div>
  {% endfor %}
</div>
{% endif %}
```

---

### `templates/accounts/login.html`

```html
{% extends 'base.html' %}
{% block title %}Вхід — Сила Єдності{% endblock %}

{% block content %}
<div class="row justify-content-center mt-5">
  <div class="col-md-5 col-lg-4">

    <div class="text-center mb-4">
      <i class="bi bi-shield-fill-check text-warning" style="font-size: 3rem;"></i>
      <h1 class="h3 mt-2 fw-bold">Сила Єдності</h1>
      <p class="text-muted">Вхід для волонтерів</p>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-body p-4">
        <form method="post" novalidate>
          {% csrf_token %}

          {% if form.non_field_errors %}
          <div class="alert alert-danger py-2">
            <i class="bi bi-exclamation-triangle me-1"></i>
            {{ form.non_field_errors.0 }}
          </div>
          {% endif %}

          <div class="mb-3">
            <label class="form-label fw-semibold">Email</label>
            {{ form.email }}
            {% if form.email.errors %}
            <div class="invalid-feedback d-block">{{ form.email.errors.0 }}</div>
            {% endif %}
          </div>

          <div class="mb-4">
            <label class="form-label fw-semibold">Пароль</label>
            {{ form.password }}
            {% if form.password.errors %}
            <div class="invalid-feedback d-block">{{ form.password.errors.0 }}</div>
            {% endif %}
          </div>

          <button type="submit" class="btn btn-dark w-100 py-2 fw-semibold">
            <i class="bi bi-box-arrow-in-right me-2"></i>Увійти
          </button>
        </form>
      </div>
    </div>

    <p class="text-center text-muted small mt-3">
      Для створення заявки авторизація не потрібна —
      <a href="{% url 'applications:create_request' %}">подати заявку</a>
    </p>
  </div>
</div>
{% endblock %}
```

---

### `templates/applications/create_request.html`

> Це публічна сторінка для військових — мінімалістична, великі кнопки, чіткий контраст.
> Відповідає Додатку А курсової роботи.

```html
{% extends 'base.html' %}
{% block title %}Подати заявку — Сила Єдності{% endblock %}

{% block content %}
<div class="row justify-content-center">
  <div class="col-12 col-md-8 col-lg-6">

    <!-- Шапка -->
    <div class="text-center mb-4">
      <i class="bi bi-shield-fill-check text-warning" style="font-size:2.5rem;"></i>
      <h1 class="h3 fw-bold mt-2">Сила Єдності</h1>
      <p class="text-muted mb-0">Заявка на матеріальну допомогу</p>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-header bg-dark text-white py-3">
        <h5 class="mb-0 fw-semibold">
          <i class="bi bi-file-earmark-plus me-2"></i>Нова заявка
        </h5>
      </div>
      <div class="card-body p-4">
        <form method="post" novalidate id="requestForm">
          {% csrf_token %}

          <!-- Дані заявника -->
          <h6 class="text-muted text-uppercase small fw-semibold mb-3 mt-1">
            <i class="bi bi-person me-1"></i>Дані заявника
          </h6>

          <div class="row g-3 mb-3">
            <div class="col-12">
              <label class="form-label fw-semibold">
                Прізвище та ініціали <span class="text-danger">*</span>
              </label>
              {{ form.user_name }}
              {% if form.user_name.errors %}
              <div class="invalid-feedback d-block">{{ form.user_name.errors.0 }}</div>
              {% endif %}
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold">
                Контактний телефон <span class="text-danger">*</span>
              </label>
              {{ form.phone }}
              <div class="form-text">Формат: +380XXXXXXXXX</div>
              {% if form.phone.errors %}
              <div class="invalid-feedback d-block">{{ form.phone.errors.0 }}</div>
              {% endif %}
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold">
                Підрозділ <span class="text-danger">*</span>
              </label>
              {{ form.unit_name }}
              <div class="form-text">Наприклад: 72 ОМБр, 2 батальйон</div>
              {% if form.unit_name.errors %}
              <div class="invalid-feedback d-block">{{ form.unit_name.errors.0 }}</div>
              {% endif %}
            </div>
          </div>

          <hr class="my-3">

          <!-- Деталі потреби -->
          <h6 class="text-muted text-uppercase small fw-semibold mb-3">
            <i class="bi bi-box-seam me-1"></i>Що потрібно
          </h6>

          <div class="row g-3 mb-3">
            <div class="col-12 col-sm-6">
              <label class="form-label fw-semibold">
                Категорія <span class="text-danger">*</span>
              </label>
              {{ form.category }}
              {% if form.category.errors %}
              <div class="invalid-feedback d-block">{{ form.category.errors.0 }}</div>
              {% endif %}
            </div>
            <div class="col-12 col-sm-6">
              <label class="form-label fw-semibold">Терміновість</label>
              {{ form.priority }}
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold">
                Опис потреби <span class="text-danger">*</span>
              </label>
              {{ form.item_name }}
              <div class="form-text">Вкажіть модель, тип, характеристики</div>
              {% if form.item_name.errors %}
              <div class="invalid-feedback d-block">{{ form.item_name.errors.0 }}</div>
              {% endif %}
            </div>
            <div class="col-12 col-sm-4">
              <label class="form-label fw-semibold">
                Кількість <span class="text-danger">*</span>
              </label>
              {{ form.quantity }}
              {% if form.quantity.errors %}
              <div class="invalid-feedback d-block">{{ form.quantity.errors.0 }}</div>
              {% endif %}
            </div>
          </div>

          <hr class="my-3">

          <!-- Доставка -->
          <h6 class="text-muted text-uppercase small fw-semibold mb-3">
            <i class="bi bi-truck me-1"></i>Адреса доставки (Нова Пошта)
          </h6>

          <div class="row g-3 mb-4">
            <div class="col-12 col-sm-7">
              <label class="form-label fw-semibold">
                Населений пункт <span class="text-danger">*</span>
              </label>
              {{ form.location }}
              {% if form.location.errors %}
              <div class="invalid-feedback d-block">{{ form.location.errors.0 }}</div>
              {% endif %}
            </div>
            <div class="col-12 col-sm-5">
              <label class="form-label fw-semibold">
                № відділення НП <span class="text-danger">*</span>
              </label>
              {{ form.post_dept }}
              {% if form.post_dept.errors %}
              <div class="invalid-feedback d-block">{{ form.post_dept.errors.0 }}</div>
              {% endif %}
            </div>
          </div>

          <!-- Кнопка — на всю ширину (мобільні, тактичні рукавиці) -->
          <button type="submit" class="btn btn-warning btn-lg w-100 fw-bold py-3" id="submitBtn">
            <i class="bi bi-send-fill me-2"></i>Надіслати заявку
          </button>
          <p class="text-center text-muted small mt-2 mb-0">
            <i class="bi bi-lock-fill me-1"></i>Дані захищені та передаються волонтерам
          </p>
        </form>
      </div>
    </div>

  </div>
</div>
{% endblock %}
```

---

### `templates/applications/request_success.html`

```html
{% extends 'base.html' %}
{% block title %}Заявку прийнято — Сила Єдності{% endblock %}

{% block content %}
<div class="row justify-content-center mt-5">
  <div class="col-md-6 text-center">
    <div class="card shadow-sm border-0">
      <div class="card-body p-5">
        <i class="bi bi-check-circle-fill text-success" style="font-size:4rem;"></i>
        <h2 class="fw-bold mt-3">Заявку прийнято!</h2>
        <p class="text-muted mt-2">
          Ваш запит зареєстровано в системі. Волонтери зв'яжуться з вами найближчим часом.
        </p>
        <a href="{% url 'applications:create_request' %}" class="btn btn-warning fw-semibold mt-2">
          <i class="bi bi-plus-circle me-1"></i>Подати ще одну заявку
        </a>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

---

### `templates/applications/dashboard.html`

> Панель волонтера. Таблиця із кольоровими статусами, фільтри.
> Відповідає Додатку B курсової роботи.

```html
{% extends 'base.html' %}
{% block title %}Дашборд — Сила Єдності{% endblock %}

{% block content %}

<!-- Заголовок + кнопка нової заявки -->
<div class="d-flex justify-content-between align-items-center mb-4">
  <div>
    <h2 class="fw-bold mb-0"><i class="bi bi-grid-fill me-2 text-warning"></i>Дашборд</h2>
    <p class="text-muted mb-0 small">Управління заявками на матеріальну допомогу</p>
  </div>
  <a href="{% url 'applications:create_request' %}" class="btn btn-warning fw-semibold">
    <i class="bi bi-plus-circle me-1"></i>Нова заявка
  </a>
</div>

<!-- Статистика -->
<div class="row g-3 mb-4">
  <div class="col-6 col-md-3">
    <div class="card border-0 shadow-sm text-center py-3">
      <div class="h3 fw-bold text-danger mb-0">{{ requests|length }}</div>
      <div class="small text-muted">Всього заявок</div>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card border-0 shadow-sm text-center py-3">
      <div class="h3 fw-bold text-danger mb-0">
        {{ requests|dictsort:"status"|length }}
      </div>
      <div class="small text-muted">Нових</div>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card border-0 shadow-sm text-center py-3">
      <div class="h3 fw-bold text-warning mb-0">—</div>
      <div class="small text-muted">В обробці</div>
    </div>
  </div>
  <div class="col-6 col-md-3">
    <div class="card border-0 shadow-sm text-center py-3">
      <div class="h3 fw-bold text-success mb-0">—</div>
      <div class="small text-muted">Виконано</div>
    </div>
  </div>
</div>

<!-- Фільтри (FR-05) -->
<div class="card border-0 shadow-sm mb-4">
  <div class="card-body py-3">
    <form method="get" class="row g-2 align-items-end">
      <div class="col-12 col-sm-6 col-md-3">
        <label class="form-label small fw-semibold mb-1">Статус</label>
        <select name="status" class="form-select form-select-sm">
          <option value="">Всі статуси</option>
          {% for val, label in statuses %}
          <option value="{{ val }}" {% if request.GET.status == val %}selected{% endif %}>
            {{ label }}
          </option>
          {% endfor %}
        </select>
      </div>
      <div class="col-12 col-sm-6 col-md-3">
        <label class="form-label small fw-semibold mb-1">Категорія</label>
        <select name="category" class="form-select form-select-sm">
          <option value="">Всі категорії</option>
          {% for cat in categories %}
          <option value="{{ cat.slug }}" {% if request.GET.category == cat.slug %}selected{% endif %}>
            {{ cat.name }}
          </option>
          {% endfor %}
        </select>
      </div>
      <div class="col-12 col-sm-6 col-md-3">
        <label class="form-label small fw-semibold mb-1">Підрозділ</label>
        <input type="text" name="unit_name" class="form-control form-control-sm"
               placeholder="72 ОМБр..." value="{{ request.GET.unit_name }}">
      </div>
      <div class="col-12 col-sm-6 col-md-3">
        <label class="form-label small fw-semibold mb-1">Пошук (FR-09)</label>
        <div class="input-group input-group-sm">
          <input type="text" name="search" class="form-control"
                 placeholder="Прізвище або телефон" value="{{ request.GET.search }}">
          <button class="btn btn-dark" type="submit">
            <i class="bi bi-search"></i>
          </button>
        </div>
      </div>
    </form>
  </div>
</div>

<!-- Таблиця заявок (FR-04) -->
<div class="card border-0 shadow-sm">
  <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center py-3">
    <h6 class="mb-0 fw-semibold"><i class="bi bi-table me-2"></i>Реєстр заявок</h6>
    <span class="badge bg-secondary">{{ requests|length }} записів</span>
  </div>
  <div class="card-body p-0">
    {% if requests %}
    <div class="table-responsive">
      <table class="table table-hover align-middle mb-0">
        <thead class="table-light">
          <tr>
            <th class="ps-3" style="width:70px;">ID</th>
            <th>Дата</th>
            <th>Заявник / Підрозділ</th>
            <th>Категорія</th>
            <th>Терміновість</th>
            <th>Статус</th>
            <th>Відповідальний</th>
            <th class="text-end pe-3">Дії</th>
          </tr>
        </thead>
        <tbody>
          {% for req in requests %}
          <tr>
            <td class="ps-3 fw-semibold text-muted">#{{ req.pk }}</td>
            <td class="small text-muted">{{ req.created_at|date:"d.m.Y" }}<br>
              <span class="text-muted" style="font-size:11px;">{{ req.created_at|date:"H:i" }}</span>
            </td>
            <td>
              <div class="fw-semibold">{{ req.user_name }}</div>
              <div class="small text-muted">{{ req.unit_name }}</div>
            </td>
            <td><span class="badge bg-dark bg-opacity-10 text-dark">{{ req.category.name }}</span></td>
            <td>
              {% if req.priority == 'CRITICAL' %}
                <span class="badge bg-danger"><i class="bi bi-exclamation-triangle-fill me-1"></i>Критичний</span>
              {% elif req.priority == 'MEDIUM' %}
                <span class="badge bg-warning text-dark">Середній</span>
              {% else %}
                <span class="badge bg-light text-dark border">Низький</span>
              {% endif %}
            </td>
            <td>
              {% if req.status == 'NEW' %}
                <span class="badge bg-danger"><i class="bi bi-circle-fill me-1" style="font-size:8px;"></i>Нова</span>
              {% elif req.status == 'IN_PROGRESS' %}
                <span class="badge bg-warning text-dark"><i class="bi bi-circle-fill me-1" style="font-size:8px;"></i>В обробці</span>
              {% elif req.status == 'DONE' %}
                <span class="badge bg-success"><i class="bi bi-check-circle-fill me-1"></i>Виконано</span>
              {% else %}
                <span class="badge bg-secondary">Скасовано</span>
              {% endif %}
            </td>
            <td class="small text-muted">
              {% if req.assigned_to %}{{ req.assigned_to.email }}{% else %}<span class="text-muted">—</span>{% endif %}
            </td>
            <td class="text-end pe-3">
              <a href="{% url 'applications:request_detail' req.pk %}"
                 class="btn btn-sm btn-outline-dark">
                <i class="bi bi-eye me-1"></i>Деталі
              </a>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
    <div class="text-center py-5 text-muted">
      <i class="bi bi-inbox" style="font-size:3rem;"></i>
      <p class="mt-2">Заявок не знайдено</p>
      {% if request.GET %}
      <a href="{% url 'applications:dashboard' %}" class="btn btn-sm btn-outline-secondary">
        Скинути фільтри
      </a>
      {% endif %}
    </div>
    {% endif %}
  </div>
</div>

{% endblock %}
```

---

### `templates/applications/request_detail.html`

```html
{% extends 'base.html' %}
{% block title %}Заявка #{{ req.pk }} — Сила Єдності{% endblock %}

{% block content %}

<!-- Хлібні крихти -->
<nav aria-label="breadcrumb" class="mb-3">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="{% url 'applications:dashboard' %}">Дашборд</a></li>
    <li class="breadcrumb-item active">Заявка #{{ req.pk }}</li>
  </ol>
</nav>

<div class="row g-4">

  <!-- Ліва колонка — деталі -->
  <div class="col-12 col-lg-8">
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center py-3">
        <h5 class="mb-0 fw-semibold">
          <i class="bi bi-file-earmark-text me-2"></i>Заявка #{{ req.pk }}
        </h5>
        {% if req.status == 'NEW' %}
          <span class="badge bg-danger fs-6">Нова</span>
        {% elif req.status == 'IN_PROGRESS' %}
          <span class="badge bg-warning text-dark fs-6">В обробці</span>
        {% elif req.status == 'DONE' %}
          <span class="badge bg-success fs-6">Виконано</span>
        {% else %}
          <span class="badge bg-secondary fs-6">Скасовано</span>
        {% endif %}
      </div>
      <div class="card-body p-4">
        <div class="row g-3">
          <div class="col-sm-6">
            <div class="text-muted small fw-semibold text-uppercase">Заявник</div>
            <div class="fw-semibold">{{ req.user_name }}</div>
          </div>
          <div class="col-sm-6">
            <div class="text-muted small fw-semibold text-uppercase">Телефон</div>
            <div><a href="tel:{{ req.phone }}">{{ req.phone }}</a></div>
          </div>
          <div class="col-sm-6">
            <div class="text-muted small fw-semibold text-uppercase">Підрозділ</div>
            <div>{{ req.unit_name }}</div>
          </div>
          <div class="col-sm-6">
            <div class="text-muted small fw-semibold text-uppercase">Категорія</div>
            <div>{{ req.category.name }}</div>
          </div>
          <div class="col-12">
            <div class="text-muted small fw-semibold text-uppercase">Що потрібно</div>
            <div class="border rounded p-3 bg-light mt-1">{{ req.item_name }}</div>
          </div>
          <div class="col-sm-4">
            <div class="text-muted small fw-semibold text-uppercase">Кількість</div>
            <div class="fw-bold fs-5">{{ req.quantity }}</div>
          </div>
          <div class="col-sm-4">
            <div class="text-muted small fw-semibold text-uppercase">Терміновість</div>
            <div>{{ req.get_priority_display }}</div>
          </div>
          <div class="col-sm-4">
            <div class="text-muted small fw-semibold text-uppercase">Дата подачі</div>
            <div>{{ req.created_at|date:"d.m.Y H:i" }}</div>
          </div>
          <div class="col-sm-6">
            <div class="text-muted small fw-semibold text-uppercase">Місто</div>
            <div>{{ req.location }}</div>
          </div>
          <div class="col-sm-6">
            <div class="text-muted small fw-semibold text-uppercase">Відділення НП</div>
            <div>№{{ req.post_dept }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Внутрішні коментарі (FR-07) -->
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-light py-3">
        <h6 class="mb-0 fw-semibold">
          <i class="bi bi-chat-left-text me-2"></i>Внутрішні нотатки
          <span class="badge bg-secondary ms-1">{{ req.comments.count }}</span>
        </h6>
      </div>
      <div class="card-body p-4">
        {% for comment in req.comments.all %}
        <div class="d-flex gap-3 mb-3">
          <div class="rounded-circle bg-dark text-white d-flex align-items-center justify-content-center flex-shrink-0"
               style="width:36px;height:36px;font-size:14px;">
            {{ comment.author.email|slice:":1"|upper }}
          </div>
          <div class="flex-grow-1">
            <div class="d-flex justify-content-between">
              <span class="fw-semibold small">{{ comment.author.email }}</span>
              <span class="text-muted small">{{ comment.created_at|date:"d.m.Y H:i" }}</span>
            </div>
            <div class="mt-1 text-break">{{ comment.text }}</div>
          </div>
        </div>
        {% empty %}
        <p class="text-muted small mb-3">Нотаток поки немає</p>
        {% endfor %}

        <form method="post" class="mt-3">
          {% csrf_token %}
          {{ comment_form.text }}
          <button type="submit" class="btn btn-sm btn-dark mt-2">
            <i class="bi bi-send me-1"></i>Додати нотатку
          </button>
        </form>
      </div>
    </div>
  </div>

  <!-- Права колонка — дії і журнал -->
  <div class="col-12 col-lg-4">

    <!-- Зміна статусу (FR-06) -->
    {% if allowed_transitions %}
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-dark text-white py-3">
        <h6 class="mb-0 fw-semibold"><i class="bi bi-arrow-right-circle me-2"></i>Змінити статус</h6>
      </div>
      <div class="card-body p-3 d-grid gap-2">
        {% for status in allowed_transitions %}
        <form method="post">
          {% csrf_token %}
          <input type="hidden" name="new_status" value="{{ status }}">
          {% if status == 'IN_PROGRESS' %}
          <button type="submit" class="btn btn-warning w-100 fw-semibold">
            <i class="bi bi-play-fill me-1"></i>Взяти в роботу
          </button>
          {% elif status == 'DONE' %}
          <button type="submit" class="btn btn-success w-100 fw-semibold">
            <i class="bi bi-check-lg me-1"></i>Позначити виконаною
          </button>
          {% elif status == 'CANCELED' %}
          <button type="submit" class="btn btn-outline-danger w-100"
                  onclick="return confirm('Скасувати цю заявку?')">
            <i class="bi bi-x-circle me-1"></i>Скасувати
          </button>
          {% endif %}
        </form>
        {% endfor %}
      </div>
    </div>
    {% endif %}

    <!-- Журнал змін AuditLog -->
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-light py-3">
        <h6 class="mb-0 fw-semibold"><i class="bi bi-clock-history me-2"></i>Журнал змін</h6>
      </div>
      <div class="card-body p-3">
        {% for log in audit_logs %}
        <div class="d-flex gap-2 align-items-start mb-2">
          <i class="bi bi-arrow-right-circle text-muted mt-1"></i>
          <div class="small">
            <span class="text-muted">{{ log.changed_at|date:"d.m H:i" }}</span>
            <span class="fw-semibold ms-1">{{ log.old_status }} → {{ log.new_status }}</span>
            {% if log.changed_by %}
            <div class="text-muted">{{ log.changed_by.email }}</div>
            {% endif %}
          </div>
        </div>
        {% empty %}
        <p class="text-muted small mb-0">Змін ще не було</p>
        {% endfor %}
      </div>
    </div>

  </div>
</div>
{% endblock %}
```

---

### `templates/reports/report_form.html`

```html
{% extends 'base.html' %}
{% block title %}Звіт Excel — Сила Єдності{% endblock %}

{% block content %}
<div class="row justify-content-center">
  <div class="col-md-6 col-lg-5">
    <h2 class="fw-bold mb-4"><i class="bi bi-file-earmark-excel me-2 text-success"></i>Звіт для донорів</h2>

    <div class="card border-0 shadow-sm">
      <div class="card-body p-4">
        <p class="text-muted mb-4">Вкажіть діапазон дат для формування звіту у форматі Excel (.xlsx).</p>
        <form method="get">
          <div class="mb-3">
            <label class="form-label fw-semibold">Дата з</label>
            <input type="date" name="date_from" class="form-control"
                   value="{{ request.GET.date_from }}" required>
          </div>
          <div class="mb-4">
            <label class="form-label fw-semibold">Дата по</label>
            <input type="date" name="date_to" class="form-control"
                   value="{{ request.GET.date_to }}" max="{{ today }}" required>
          </div>
          <button type="submit" class="btn btn-success w-100 fw-semibold py-2">
            <i class="bi bi-download me-2"></i>Завантажити звіт (.xlsx)
          </button>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

---

## Крок 3 — Статичні файли

### `static/css/main.css`

```css
/* Сила Єдності — кастомні стилі */

body {
  background-color: #f8f9fa;
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}

/* Navbar */
.navbar-brand {
  letter-spacing: 0.5px;
}

/* Картки */
.card {
  border-radius: 12px;
}

/* Таблиця заявок */
.table th {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6c757d;
  font-weight: 600;
}

.table tbody tr:hover {
  background-color: #fff8e7;
  cursor: pointer;
}

/* Бейджі статусів */
.badge {
  font-size: 0.75rem;
  padding: 0.4em 0.7em;
}

/* Форма заявки (UC-01) — кнопка великий палець */
#submitBtn {
  font-size: 1.1rem;
  letter-spacing: 0.3px;
}

/* Мобільні */
@media (max-width: 576px) {
  .container { padding-left: 12px; padding-right: 12px; }
  .card-body { padding: 1.25rem !important; }
  .btn-lg { font-size: 1.05rem; }
}

/* Активний пункт меню */
.nav-link.active {
  font-weight: 600;
  color: #ffc107 !important;
}

/* Хедер картки — рядок */
.card-header h5, .card-header h6 {
  font-size: 0.95rem;
}
```

---

### `static/js/main.js`

```javascript
// FR-02: Клієнтська валідація форми заявки

document.addEventListener('DOMContentLoaded', function () {

  const form = document.getElementById('requestForm');
  if (!form) return;

  // Валідація телефону +380XXXXXXXXX
  const phoneInput = form.querySelector('[name="phone"]');
  if (phoneInput) {
    phoneInput.addEventListener('blur', function () {
      const val = this.value.trim();
      const valid = /^\+380\d{9}$/.test(val);
      this.classList.toggle('is-invalid', !valid && val.length > 0);
      this.classList.toggle('is-valid', valid);
    });

    // Автододавання +380 якщо починається з 0
    phoneInput.addEventListener('input', function () {
      if (this.value.startsWith('0') && !this.value.startsWith('+')) {
        this.value = '+38' + this.value;
      }
    });
  }

  // Показуємо спінер при відправці
  const submitBtn = document.getElementById('submitBtn');
  if (submitBtn) {
    form.addEventListener('submit', function () {
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Відправляємо...';
      submitBtn.disabled = true;
    });
  }

  // Підсвічування рядків таблиці — клік веде на деталі
  document.querySelectorAll('table tbody tr[data-href]').forEach(row => {
    row.addEventListener('click', function () {
      window.location.href = this.dataset.href;
    });
  });

});
```

---

## Крок 4 — Apps.py і реєстрація сигналів

### `apps/applications/apps.py`

```python
from django.apps import AppConfig


class ApplicationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.applications"
    verbose_name = "Заявки"

    def ready(self):
        import apps.applications.signals  # noqa — реєстрація сигналів AuditLog
```

---

## Крок 5 — Admin (українська мова)

### `apps/applications/admin.py`

```python
from django.contrib import admin
from .models import Request, Category, AuditLog, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display  = ["id", "user_name", "unit_name", "category", "status",
                     "priority", "assigned_to", "created_at"]
    list_filter   = ["status", "priority", "category"]
    search_fields = ["user_name", "phone", "unit_name"]
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 25
    ordering      = ["-created_at"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["request", "old_status", "new_status", "changed_by", "changed_at"]
    readonly_fields = ["request", "old_status", "new_status", "changed_by", "changed_at"]
```

### `apps/accounts/admin.py`

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display  = ["email", "role", "is_active", "is_staff"]
    list_filter   = ["role", "is_active"]
    ordering      = ["email"]
    fieldsets = (
        (None,             {"fields": ("email", "password")}),
        ("Роль та доступ", {"fields": ("role", "is_active", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "password1", "password2", "role")}),
    )
    search_fields = ["email"]
    filter_horizontal = ()
```

---

## Крок 6 — Налаштування Django Admin: українська мова

У файлі `config/settings/base.py` переконайся що є:

```python
LANGUAGE_CODE = "uk"
TIME_ZONE     = "Europe/Kyiv"
USE_I18N      = True
USE_TZ        = True
```

---

## Крок 7 — Фікстури: початкові категорії

Створи файл `apps/applications/fixtures/categories.json`:

```json
[
  {"model": "applications.category", "pk": 1, "fields": {"name": "Дрони та БПЛА",         "slug": "drones"}},
  {"model": "applications.category", "pk": 2, "fields": {"name": "Тактична медицина",     "slug": "medicine"}},
  {"model": "applications.category", "pk": 3, "fields": {"name": "Засоби зв'язку",        "slug": "communication"}},
  {"model": "applications.category", "pk": 4, "fields": {"name": "Амуніція та оптика",    "slug": "ammo"}},
  {"model": "applications.category", "pk": 5, "fields": {"name": "Енергонезалежність",    "slug": "energy"}},
  {"model": "applications.category", "pk": 6, "fields": {"name": "Автотехніка",           "slug": "vehicles"}},
  {"model": "applications.category", "pk": 7, "fields": {"name": "Інше",                  "slug": "other"}}
]
```

Завантажити: `python manage.py loaddata categories`

---

## Крок 8 — Фінальна перевірка

Після всіх змін виконай по черзі:

```bash
# 1. Зупини і перебудуй контейнери
docker compose down
docker compose up --build

# 2. Міграції
docker compose exec web python manage.py migrate

# 3. Завантаж категорії
docker compose exec web python manage.py loaddata categories

# 4. Створи суперкористувача (директор)
docker compose exec web python manage.py createsuperuser

# 5. Перевір що все доступно
# http://localhost:8000/          ← форма для військових
# http://localhost:8000/login/    ← вхід для волонтерів
# http://localhost:8000/dashboard/ ← дашборд (після входу)
# http://localhost:8000/admin/    ← Django Admin
```

---

## Підсумок змін

| # | Що зроблено |
|---|---|
| 0 | Аудит всіх файлів — перевірено існування і вміст |
| 1 | Видалено Terraform / AWS |
| 2 | Заповнено всі 8 HTML-шаблонів (Bootstrap 5, українська) |
| 3 | Додано CSS + JS для валідації та стилів |
| 4 | Зареєстровано сигнали в apps.py |
| 5 | Admin налаштований українською |
| 6 | Мова/часовий пояс = uk / Europe/Kyiv |
| 7 | Фікстура категорій (7 позицій з курсової) |
| 8 | Інструкція для запуску і перевірки |
