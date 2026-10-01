from django import forms

from .models import Property, Cleaner


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = "__all__"


class CleanerForm(forms.ModelForm):
    class Meta:
        model = Cleaner
        fields = "__all__"
        widgets = {
            "cleaning_types": forms.CheckboxSelectMultiple,
        }