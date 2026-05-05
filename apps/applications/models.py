from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class Request(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW", "Нова"
        IN_PROGRESS = "IN_PROGRESS", "В обробці"
        DONE = "DONE", "Виконано"
        CANCELED = "CANCELED", "Скасовано"

    class Priority(models.TextChoices):
        CRITICAL = "CRITICAL", "Критичний"
        MEDIUM = "MEDIUM", "Середній"
        LOW = "LOW", "Низький"

    user_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    unit_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="requests")
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    item_name = models.TextField()
    quantity = models.PositiveIntegerField()
    location = models.CharField(max_length=255)
    post_dept = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_requests",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_name} - {self.get_status_display()}"


class Comment(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment #{self.pk}"


class AuditLog(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="audit_logs")
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.request_id}: {self.old_status} -> {self.new_status}"
