from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from users.models import UserRole, User, Cleaner
from cleaning.models import (
    Property,
    PropertyType,
    CleaningType,
    Cleaning,
    StatusChoices,
)

from cleaning.forms import (
    PropertyForm,
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

    def test_status_field_hidden_on_create(self):
        form = CleaningForm(user=self.user)
        self.assertNotIn("status", form.fields)

    def test_status_field_available_on_update(self):
        cleaning = Cleaning.objects.create(
            date=timezone.now() + timedelta(days=1),
            cleaning_type=self.cleaning_type,
            property=self.property,
            cleaner=self.cleaner,
        )
        form = CleaningForm(instance=cleaning, user=self.user)
        self.assertIn("status", form.fields)

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
                "date": "2026-10-20T14:30",
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "status": StatusChoices.PLANNED,
            },
            user=self.cleaner.user,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_manager_cannot_assign_unsupported_cleaning_type(self):
        unsupported_cleaning_type = CleaningType.objects.create(
            name="General",
            description="General cleaning",
        )
        form = CleaningForm(
            data={
                "date": "2026-10-20T14:30",
                "cleaning_type": unsupported_cleaning_type.pk,
                "property": self.property.pk,
                "cleaner": self.cleaner.pk,
                "status": StatusChoices.PLANNED,
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("cleaning_type", form.errors)

    def test_manager_can_assign_supported_cleaning_type(self):
        form = CleaningForm(
            data={
                "date": (timezone.now() +
                         timedelta(days=2)).strftime("%Y-%m-%dT%H:%M"),
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "cleaner": self.cleaner.pk,
                "status": StatusChoices.PLANNED,
            },
            user=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_cleaner_is_assigned_to_himself(self):
        form = CleaningForm(
            data={
                "date": (timezone.now() +
                         timedelta(days=2)).strftime("%Y-%m-%dT%H:%M"),
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "status": StatusChoices.PLANNED,
            },
            user=self.cleaner.user,
        )
        self.assertTrue(form.is_valid(), form.errors)
        cleaning = form.save(commit=False)
        self.assertEqual(cleaning.cleaner, self.cleaner)


class CleaningFormDateAndAvailabilityTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager",
            password="testpassword1",
            role=UserRole.MANAGER,
        )
        self.owner = User.objects.create_user(
            username="owner",
            password="testpassword1",
            role=UserRole.OWNER,
        )
        self.other_owner = User.objects.create_user(
            username="other_owner",
            password="testpassword1",
            role=UserRole.OWNER,
        )
        self.cleaning_type = CleaningType.objects.create(
            name="Regular",
            description="Regular cleaning",
        )
        self.cleaner = Cleaner.objects.create(
            first_name="John",
            last_name="Smith",
            phone="123456789",
        )
        self.cleaner.cleaning_types.add(self.cleaning_type)
        self.property = Property.objects.create(
            name="Own flat",
            address="own st. 1",
            property_type=PropertyType.HOUSE,
            rooms=2,
            owner=self.owner,
        )
        self.other_property = Property.objects.create(
            name="Other flat",
            address="other st. 2",
            property_type=PropertyType.HOUSE,
            rooms=3,
            owner=self.other_owner,
        )
        self.future = (
            timezone.now() + timedelta(days=2)
        ).replace(second=0, microsecond=0)

    def form_data(self, date):
        return {
            "date": date.strftime("%Y-%m-%dT%H:%M"),
            "cleaning_type": self.cleaning_type.pk,
            "property": self.property.pk,
            "cleaner": self.cleaner.pk,
        }

    def create_cleaning(
        self, date, status=StatusChoices.PLANNED, property=None
    ):
        return Cleaning.objects.create(
            date=date,
            cleaning_type=self.cleaning_type,
            property=property or self.property,
            cleaner=self.cleaner,
            status=status,
        )

    def test_owner_does_not_see_other_owners_properties(self):
        form = CleaningForm(user=self.owner)
        properties = form.fields["property"].queryset
        self.assertIn(self.property, properties)
        self.assertNotIn(self.other_property, properties)

    def test_cannot_create_cleaning_in_the_past(self):
        past = timezone.now() - timedelta(days=1)
        form = CleaningForm(data=self.form_data(past), user=self.manager)
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_can_change_status_of_past_cleaning(self):
        past = (
            timezone.now() - timedelta(days=1)
        ).replace(second=0, microsecond=0)
        cleaning = self.create_cleaning(past)
        data = self.form_data(past)
        data["status"] = StatusChoices.DONE
        form = CleaningForm(data=data, instance=cleaning, user=self.manager)
        self.assertTrue(form.is_valid(), form.errors)

    def test_cannot_move_existing_cleaning_to_the_past(self):
        cleaning = self.create_cleaning(self.future)
        past = timezone.now() - timedelta(days=1)
        data = self.form_data(past)
        data["status"] = StatusChoices.PLANNED
        form = CleaningForm(data=data, instance=cleaning, user=self.manager)
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_cannot_book_busy_cleaner(self):
        self.create_cleaning(self.future)
        form = CleaningForm(
            data=self.form_data(self.future),
            user=self.manager,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("already booked", str(form.errors))

    def test_can_book_cleaner_when_previous_cleaning_is_canceled(self):
        self.create_cleaning(
            self.future,
            status=StatusChoices.CANCELLED,
            property=self.other_property,
        )
        form = CleaningForm(
            data=self.form_data(self.future),
            user=self.manager,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_busy_cleaner_creating_own_cleaning_gets_form_error(self):
        cleaner_user = User.objects.create_user(
            username="cleaner_user",
            password="testpassword1",
            role=UserRole.CLEANER,
        )
        self.cleaner.user = cleaner_user
        self.cleaner.save()
        self.create_cleaning(self.future)
        data = self.form_data(self.future)
        del data["cleaner"]
        form = CleaningForm(data=data, user=cleaner_user)
        self.assertFalse(form.is_valid())
        self.assertIn("already booked", str(form.errors))
