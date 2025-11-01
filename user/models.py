from django.contrib.auth.models import AbstractUser
from django.db import models

from base.models import OPTIONAL, BaseModel


class User(BaseModel, AbstractUser):
    class UserTypeChoices(models.TextChoices):
        PLATFORM_ADMIN = "platform admin", "Platform Admin"
        TENANT_ADMIN = "tenant admin", "Tenant Admin"
        TENANT = "tenant", "Tenant"

    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    tenant = models.ForeignKey(
        "tenant.Tenant", on_delete=models.CASCADE, related_name="users", **OPTIONAL
    )
    user_type = models.CharField(
        max_length=20,
        default=UserTypeChoices.TENANT,
        choices=UserTypeChoices.choices,
    )

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """
        Override save method to ensure email is lowercase and username is set from email.
        """
        email = self.email.lower()
        if email:
            self.email = email
            self.username = email.split("@")[0] if not self.username else self.username
        super().save(*args, **kwargs)
