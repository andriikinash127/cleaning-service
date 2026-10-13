from django.db import models
from django.contrib.auth.models import AbstractUser


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


class PropertyType(models.TextChoices):
    APARTMENT = "Apartment"
    HOUSE = "House"


class Property(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    apartment_number = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
    )
    rooms = models.PositiveIntegerField()
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="properties"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["address", "apartment_number"],
                condition=models.Q(property_type=PropertyType.APARTMENT),
                name="unique_apartment_address",
            ),
            models.UniqueConstraint(
                fields=["address"],
                condition=models.Q(property_type=PropertyType.HOUSE),
                name="unique_house_address",
            )
        ]

    def __str__(self):
        return self.name


class CleaningTypeChoices(models.TextChoices):
    REGULAR = "Regular"
    GENERAL = "General"
    DEEP = "Deep cleaning"
    MOVE = "Move in / Move out"


class CleaningType(models.Model):
    name = models.CharField(
        max_length=255,
        choices=CleaningTypeChoices.choices,
    )
    description = models.TextField()

    def __str__(self):
        return self.name


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
    cleaning_types = models.ManyToManyField(CleaningType)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name"],
                name="unique_cleaner_name",
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class StatusChoices(models.TextChoices):
    PLANNED = "planned", "Planned"
    INPROGRESS = "in progress", "In progress"
    DONE = "finished", "Finished"
    CANCELLED = "canceled", "Canceled"


class Cleaning(models.Model):
    date = models.DateField()
    cleaning_type = models.ForeignKey(
        CleaningType,
        on_delete=models.CASCADE,
        related_name="cleanings",
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="cleanings",
    )
    cleaner = models.ForeignKey(
        Cleaner,
        on_delete=models.CASCADE,
        related_name="cleanings",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
    )
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["date", "property", "cleaner"],
                name="unique_cleaning_combination"
            )
        ]

    def __str__(self):
        return f"{self.cleaner} works on {self.property} at {self.date}"
