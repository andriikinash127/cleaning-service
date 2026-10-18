from django import forms
from django.contrib.auth.forms import UserCreationForm

from cleaning.models import Cleaner, Property, User


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


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")
