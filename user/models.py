from django.contrib.auth.models import AbstractUser
from django.db import models

from base.models import BaseModel


class User(BaseModel, AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    tenant = models.ForeignKey(
        "tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
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
