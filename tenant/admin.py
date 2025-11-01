from django.contrib import admin

from tenant.models import Tenant, TenantPayment
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


@admin.register(TenantPayment)
class TenantPaymentAdmin(admin.ModelAdmin):
    """Admin interface for TenantPayment model."""

    list_display = (
        "tenant",
        "plan",
        "amount",
        "provider",
        "status",
        "start_date",
        "end_date",
        "created_at",
    )
    search_fields = ("tenant__name", "provider_subscription_id")
    ordering = ("-created_at",)
    list_filter = ("status", "provider", "created_at")
    readonly_fields = ("created_at", "updated_at")
