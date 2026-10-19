from django import forms
from django.utils import timezone

from .models import (
    Property,
    Cleaner,
    Cleaning,
    UserRole,
    StatusChoices,
    CleaningType,
)


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.role == UserRole.OWNER:
            self.fields.pop("owner", None)



class CleaningForm(forms.ModelForm):
    class Meta:
        model = Cleaning
        fields = "__all__"
        widgets = {
            "date": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={"type": "datetime-local"},
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if user and user.role == UserRole.CLEANER:
            self.fields.pop("cleaner", None)

            try:
                cleaner = user.cleaner
                self.fields["cleaning_type"].queryset = (
                    cleaner.cleaning_types.all()
                )
            except Cleaner.DoesNotExist:
                self.fields["cleaning_type"].queryset = (
                    CleaningType.objects.none()
                )

    def clean_date(self):
        date = self.cleaned_data.get("date")

        if date and date < timezone.now():
            raise forms.ValidationError(
                "Cleaning cannot be scheduled in the past."
            )

        return date

    def clean(self):
        cleaned_data = super().clean()

        cleaner = cleaned_data.get("cleaner")

        if self.user and self.user.role == UserRole.CLEANER:
            try:
                cleaner = self.user.cleaner
            except Cleaner.DoesNotExist:
                raise forms.ValidationError(
                    "Your user account is not linked to a cleaner."
                )

            cleaned_data["cleaner"] = cleaner
            self.instance.cleaner = cleaner

        cleaning_type = cleaned_data.get("cleaning_type")
        date = cleaned_data.get("date")

        if cleaner and cleaning_type:
            if not cleaner.cleaning_types.filter(
                pk=cleaning_type.pk
            ).exists():
                self.add_error(
                    "cleaning_type",
                    "This cleaner does not have experience "
                    "with this cleaning type.",
                )

        if cleaner and date:
            conflicts = Cleaning.objects.filter(
                cleaner=cleaner,
                date=date,
            ).exclude(
                status=StatusChoices.CANCELLED,
            )

            if self.instance.pk:
                conflicts = conflicts.exclude(pk=self.instance.pk)

            if conflicts.exists():
                self.add_error(
                    "cleaner" if "cleaner" in self.fields else None,
                    "This cleaner is already booked at this date and time.",
                )

        return cleaned_data
