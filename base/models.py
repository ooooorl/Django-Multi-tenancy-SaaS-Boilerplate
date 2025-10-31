from typing import Optional

from django.conf import settings
from django.db import models
from django.utils import timezone

OPTIONAL = {"null": True, "blank": True}


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_%(class)s_set",
        **OPTIONAL,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="updated_%(class)s_set",
        **OPTIONAL,
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="deleted_%(class)s_set",
        **OPTIONAL,
    )
    is_active = models.BooleanField(default=True)

    def delete(self, using: Optional[str] = None, keep_parents: bool = False) -> None:
        """
        Soft delete—stamp metadata instead of hard remove.

        Args:
            using (str, optional): The database alias to use.
            keep_parents (bool, optional): Whether to keep parent data in
            multi-table inheritance.
                Defaults to False, which deletes the parent model as well.

        Notes:
            - Sets `deleted_at` to the current timestamp.
            - Only updates the `deleted_at` and `deleted_by` fields.
            - `deleted_by` must be set manually before calling this method.

        Example:
            user_1 = User.objects.get(name="Senpai")
            user_2 = User.objects.get(name="Orly")

            user_2.deleted_by = user_1
            user_2.delete()
        """
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "deleted_by"])

    class Meta:
        """Abstract base model with audit fields."""

        abstract = True
