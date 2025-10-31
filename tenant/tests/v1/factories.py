import re

import factory

from tenant.models import Tenant


def normalize_subdomain(name: str) -> str:
    """Convert company name to a valid subdomain: lowercase letters, numbers, hyphens only."""
    name = name.lower()
    # replace spaces with hyphens
    name = name.replace(" ", "-")
    # remove any character that is not a-z, 0-9, or hyphen
    return re.sub(r"[^a-z0-9-]", "", name)


class TenantFactory(factory.django.DjangoModelFactory):
    """Factory for creating Tenant instances for testing."""

    class Meta:
        model = Tenant

    name = factory.Faker("company")
    slug = factory.LazyAttribute(lambda obj: normalize_subdomain(obj.name))
    subdomain = factory.LazyAttribute(lambda obj: normalize_subdomain(obj.name))
    plan = Tenant.PlanChoices.FREE
    payment_status = Tenant.PaymentStatusChoices.PENDING
    policy = factory.Faker("text", max_nb_chars=200)
