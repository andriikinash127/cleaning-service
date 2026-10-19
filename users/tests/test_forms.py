from django.test import TestCase

from users.forms import CleanerForm
from cleaning.models import CleaningType


class CleanerFormTests(TestCase):
    def setUp(self):
        self.cleaning_type = CleaningType.objects.create(
            name="Regular",
            description="Regular cleaning",
        )
        self.second_cleaning_type = CleaningType.objects.create(
            name="General",
            description="General cleaning",
        )

    def test_valid_form(self):
        form = CleanerForm(data={
            "first_name": "John",
            "last_name": "Smith",
            "phone": "123456789",
            "cleaning_types": [self.cleaning_type.pk],
        })
        self.assertTrue(form.is_valid())

    def test_invalid_form_without_first_name(self):
        form = CleanerForm(data={
            "first_name": "",
            "last_name": "Smith",
            "phone": "123456789",
            "cleaning_types": [self.cleaning_type.pk],
        })
        self.assertFalse(form.is_valid())

    def test_invalid_form_without_last_name(self):
        form = CleanerForm(data={
            "first_name": "John",
            "last_name": "",
            "phone": "123456789",
            "cleaning_types": [self.cleaning_type.pk],
        })
        self.assertFalse(form.is_valid())

    def test_invalid_form_without_phone(self):
        form = CleanerForm(data={
            "first_name": "John",
            "last_name": "Smith",
            "phone": "",
            "cleaning_types": [self.cleaning_type.pk],
        })
        self.assertFalse(form.is_valid())

    def test_invalid_form_without_cleaning_types(self):
        form = CleanerForm(data={
            "first_name": "John",
            "last_name": "Smith",
            "phone": "123456789",
            "cleaning_types": [],
        })
        self.assertFalse(form.is_valid())

    def test_valid_form_with_multiple_cleaning_types(self):
        form = CleanerForm(data={
            "first_name": "John",
            "last_name": "Smith",
            "phone": "123456789",
            "cleaning_types": [
                self.cleaning_type.pk,
                self.second_cleaning_type.pk,
            ],
        })
        self.assertTrue(form.is_valid())
