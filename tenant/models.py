from django.db import models
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
