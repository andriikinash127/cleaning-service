from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Property, Cleaner, Cleaning, User


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = "__all__"


class OwnerPropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        exclude = ("owner",)


class CleanerForm(forms.ModelForm):
    class Meta:
        model = Cleaner
        exclude = ("user",)
        widgets = {
            "cleaning_types": forms.CheckboxSelectMultiple,
        }


class CleaningForm(forms.ModelForm):
    class Meta:
        model = Cleaning
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        cleaner = cleaned_data.get("cleaner")
        cleaning_type = cleaned_data.get("cleaning_type")
        if cleaner and cleaning_type:
            if cleaning_type not in cleaner.cleaning_types.all():
                raise forms.ValidationError(
                    "This cleaner does not have experience with this cleaning type."
                )

        return cleaned_data


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")
