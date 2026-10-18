from django.test import TestCase

from cleaning.models import (
    User,
    UserRole,
    Property,
    PropertyType,
    Cleaner,
    CleaningType,
    StatusChoices,
)

from cleaning.forms import (
    PropertyForm,
    CleanerForm,
    CleaningForm,
)

class PropertyFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword1",
            role=UserRole.MANAGER,
        )

    def test_valid_form(self):
        form = PropertyForm(data={
            "name": "Test House",
            "address": "test st. 10",
            "apartment_number": "",
            "property_type": PropertyType.HOUSE,
            "rooms": 4,
            "owner": self.user.pk,
        })
        self.assertTrue(form.is_valid())

    def test_invalid_form_without_name(self):
        form = PropertyForm(data={
            "name": "",
            "address": "test st. 10",
            "apartment_number": "",
            "property_type": PropertyType.HOUSE,
            "rooms": 4,
            "owner": self.user.pk,
        })
        self.assertFalse(form.is_valid())

    def test_invalid_form_without_address(self):
        form = PropertyForm(data={
            "name": "Test House",
            "address": "",
            "apartment_number": "",
            "property_type": PropertyType.HOUSE,
            "rooms": 4,
            "owner": self.user.pk,
        })
        self.assertFalse(form.is_valid())

    def test_invalid_form_without_rooms(self):
        form = PropertyForm(data={
            "name": "Test House",
            "address": "test st. 10",
            "apartment_number": "",
            "property_type": PropertyType.HOUSE,
            "rooms": "",
            "owner": self.user.pk,
        })
        self.assertFalse(form.is_valid())

    def test_invalid_form_without_property_type(self):
        form = PropertyForm(data={
            "name": "Test House",
            "address": "test st. 10",
            "apartment_number": "",
            "property_type": "",
            "rooms": 4,
            "owner": self.user.pk,
        })
        self.assertFalse(form.is_valid())


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


class CleaningFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="manager",
            password="testpassword1",
            role=UserRole.MANAGER,
        )
        self.cleaning_type = CleaningType.objects.create(
            name="Regular",
            description="Regular cleaning",
        )
        self.cleaner = Cleaner.objects.create(
            user=User.objects.create_user(
                username="cleaner",
                password="testpassword1",
                role=UserRole.CLEANER,
            ),
            first_name="John",
            last_name="Smith",
            phone="123456789",
        )
        self.property = Property.objects.create(
            name="Test House",
            address="test st. 10",
            property_type=PropertyType.HOUSE,
            rooms=4,
            owner=self.user,
        )
        self.cleaner.cleaning_types.add(self.cleaning_type)

    def test_manager_can_see_cleaner_field(self):
        form = CleaningForm(user=self.user)
        self.assertIn("cleaner", form.fields)

    def test_cleaner_cannot_see_cleaner_field(self):
        cleaner_user = self.cleaner.user
        form = CleaningForm(user=cleaner_user)
        self.assertNotIn("cleaner", form.fields)

    def test_cleaner_cannot_use_unsupported_cleaning_type(self):
        unsupported_cleaning_type = CleaningType.objects.create(
            name="General",
            description="General cleaning",
        )
        form = CleaningForm(
            data={
                "date": "2026-10-03",
                "cleaning_type": unsupported_cleaning_type.pk,
                "property": self.property.pk,
                "status": StatusChoices.PLANNED,
            },
            user=self.cleaner.user,
        )
        self.assertFalse(form.is_valid())

    def test_cleaner_can_use_supported_cleaning_type(self):
        form = CleaningForm(
            data={
                "date": "2026-10-03",
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "status": StatusChoices.PLANNED,
            },
            user=self.cleaner.user,
        )
        self.assertTrue(form.is_valid())

    def test_manager_cannot_assign_unsupported_cleaning_type(self):
        unsupported_cleaning_type = CleaningType.objects.create(
            name="General",
            description="General cleaning",
        )
        form = CleaningForm(
            data={
                "date": "2026-10-03",
                "cleaning_type": unsupported_cleaning_type.pk,
                "property": self.property.pk,
                "cleaner": self.cleaner.pk,
                "status": StatusChoices.PLANNED,
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())

    def test_manager_can_assign_supported_cleaning_type(self):
        form = CleaningForm(
            data={
                "date": "2026-10-03",
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "cleaner": self.cleaner.pk,
                "status": StatusChoices.PLANNED,
            },
            user=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_cleaner_is_assigned_to_himself(self):
        form = CleaningForm(
            data={
                "date": "2026-10-03",
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "status": StatusChoices.PLANNED,
            },
            user=self.cleaner.user,
        )
        self.assertTrue(form.is_valid())
        cleaning = form.save(commit=False)
        self.assertEqual(cleaning.cleaner, self.cleaner)
