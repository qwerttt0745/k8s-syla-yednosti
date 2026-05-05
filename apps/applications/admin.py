from django.contrib import admin

from .models import AuditLog, Category, Comment, Request


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_name",
        "unit_name",
        "category",
        "status",
        "priority",
        "assigned_to",
        "created_at",
    )
    list_filter = ("status", "priority", "category")
    search_fields = ("user_name", "phone", "unit_name")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25
    ordering = ("-created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("request", "author", "created_at")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("request", "old_status", "new_status", "changed_by", "changed_at")
    readonly_fields = ("request", "old_status", "new_status", "changed_by", "changed_at")
