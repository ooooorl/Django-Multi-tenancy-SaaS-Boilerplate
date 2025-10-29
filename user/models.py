from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from base.models import BaseModel


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        """Create a normal user and save to the default DB."""
        if not username:
            raise ValueError("Username must be set")
        elif not password:
            raise ValueError("Password must be set")

        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """Create a superuser and save to the default DB."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        if not username:
            raise ValueError("Username must be set")
        elif not password:
            raise ValueError("Password must be set")

        user = self.create_user(username, password, **extra_fields)
        return user


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # This will be prompt when creating an account via management command
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS: list[str] = []

    objects = CustomUserManager()

    def __str__(self):
        """Return username"""
        return f"{self.username}"
