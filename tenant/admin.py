from django.contrib import admin

from tenant.models import Tenant
from user.models import User


class InlineUserAdmin(admin.TabularInline):
    """Inline admin interface for User model within Tenant admin."""

    model = User
    extra = 0
    fields = ("username", "email", "first_name", "last_name", "is_active", "is_staff")
    readonly_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
    )
    can_delete = True
    show_change_link = True


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin interface for Tenant model."""

    list_display = (
        "name",
        "subdomain",
        "plan",
        "created_at",
        "updated_at",
        "is_active",
    )
    search_fields = ("name", "subdomain")
    ordering = ("-created_at",)
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    inlines = [InlineUserAdmin]
