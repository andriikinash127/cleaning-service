from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    MANAGER = "manager", "Manager"
    OWNER = "owner", "Owner"
    CLEANER = "cleaner", "Cleaner"


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.OWNER,
    )


class Cleaner(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cleaner",
        null=True,
        blank=True,
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    cleaning_types = models.ManyToManyField("cleaning.CleaningType")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name"],
                name="unique_cleaner_name",
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
