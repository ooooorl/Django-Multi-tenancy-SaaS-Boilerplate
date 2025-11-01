from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from base.models import OPTIONAL, BaseModel


class Tenant(BaseModel):
    """
    Represents a tenant (organization or workspace) in a multi-tenant SaaS architecture.
    Each tenant has its own users, plan, and subdomain.
    """

    class PlanChoices(models.TextChoices):
        """Enumeration for tenant subscription plans."""

        FREE = "free", "Free"
        BASIC = "basic", "Basic"
        PRO = "pro", "Pro"
        ENTERPRISE = "enterprise", "Enterprise"

    class PaymentStatusChoices(models.TextChoices):
        """Enumeration for tenant payment statuses."""

        ACTIVE = "active", "Active"
        PENDING = "pending", "Pending"
        INACTIVE = "inactive", "Inactive"
        PAST_DUE = "past_due", "Past Due"
        CANCELED = "canceled", "Canceled"

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, **OPTIONAL)
    policy = models.TextField(
        help_text="Terms of service and privacy policy for the tenant.",
        **OPTIONAL,
    )
    subdomain = models.CharField(
        max_length=255,
        unique=True,
        **OPTIONAL,
        help_text="Unique subdomain for the tenant, e.g., 'acme' for acme.example.com.",
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.PENDING,
    )
    plan = models.CharField(
        max_length=20,
        choices=PlanChoices.choices,
        default=PlanChoices.FREE,
    )

    def __str__(self):
        return f"{self.name} ({self.subdomain or 'no-subdomain'})"

    def save(self, *args, **kwargs):
        """
        Override save method to ensure subdomain is lowercase and slug is set from name.
        """
        if self.subdomain:
            self.subdomain = self.subdomain.lower()
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class TenantPayment(BaseModel):
    """
    Represents payment information for a tenant.
    """

    class PaymentProviderChoices(models.TextChoices):
        """Enumeration for payment providers."""

        STRIPE = "stripe", "Stripe"
        PAYPAL = "paypal", "PayPal"

    PLAN_DURATIONS = {
        Tenant.PlanChoices.FREE: 0,
        Tenant.PlanChoices.BASIC: 30,
        Tenant.PlanChoices.PRO: 30,
        Tenant.PlanChoices.ENTERPRISE: 30,
    }

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    provider = models.CharField(
        max_length=20,
        choices=PaymentProviderChoices.choices,
    )
    plan = models.CharField(max_length=20, choices=Tenant.PlanChoices.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Tenant.PaymentStatusChoices.choices,
        default=Tenant.PaymentStatusChoices.PENDING,
    )
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(**OPTIONAL)
    provider_subscription_id = models.CharField(max_length=255, **OPTIONAL)

    class Meta:
        indexes = [
            models.Index(fields=["tenant"]),
            models.Index(fields=["provider_subscription_id"]),
        ]

    def __str__(self):
        return f"{self.tenant.name} - {self.provider} - {self.plan} - {self.status}"

    @property
    def is_expired(self):
        """Check if the subscription has expired."""
        return self.end_date and timezone.now() > self.end_date

    def save(self, *args, **kwargs):
        """Automatically set end_date based on plan if not provided."""
        if not self.end_date and self.plan in self.PLAN_DURATIONS:
            duration_days = self.PLAN_DURATIONS[self.plan]
            if duration_days > 0:
                self.end_date = self.start_date + timedelta(days=duration_days)
        super().save(*args, **kwargs)
