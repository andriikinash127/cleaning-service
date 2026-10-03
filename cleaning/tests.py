from django.test import TestCase
from django.db import IntegrityError

from .models import (
    User,
    UserRole,
    Property,
    PropertyType,
    Cleaner,
    CleaningType,
    Cleaning,
    StatusChoices,
)

from .forms import (
    PropertyForm,
    CleanerForm,
    CleaningForm,
)


class PropertyModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testusername",
            password="testpassword1",
            role=UserRole.MANAGER,
        )

        self.house = Property.objects.create(
            name="Test House",
            address="test st. 10",
            property_type=PropertyType.HOUSE,
            rooms=4,
            owner=self.user,
        )

        self.apartment = Property.objects.create(
            name="Test Apartment",
            address="test st. 20",
            apartment_number=5,
            property_type=PropertyType.APARTMENT,
            rooms=2,
            owner=self.user,
        )


    def test_property_creation(self):
        self.assertEqual(Property.objects.count(), 2)


    def test_property_str(self):
        self.assertEqual(str(self.house), "Test House")


    def test_apartment_address_and_number_are_unique(self):
        with self.assertRaises(IntegrityError):
            Property.objects.create(
                name="Apartment 2",
                address=self.apartment.address,
                apartment_number=self.apartment.apartment_number,
                property_type=PropertyType.APARTMENT,
                rooms=3,
                owner=self.user,
            )


    def test_house_address_is_unique(self):
        with self.assertRaises(IntegrityError):
            Property.objects.create(
                name="House 2",
                address=self.house.address,
                property_type=PropertyType.HOUSE,
                rooms=3,
                owner=self.user,
            )

    def test_house_and_apartment_can_have_same_address(self):
        Property.objects.create(
            name="Apartment 2",
            address=self.house.address,
            apartment_number=10,
            property_type=PropertyType.APARTMENT,
            rooms=2,
            owner=self.user,
        )


class CleanerModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cleaner",
            password="testpassword1",
            role=UserRole.CLEANER,
        )
        self.cleaner = Cleaner.objects.create(
            user=self.user,
            first_name="John",
            last_name="Smith",
            phone="123456789",
        )
        self.cleaning_type = CleaningType.objects.create(
            name="Regular",
            description="Regular cleaning",
        )
        self.second_cleaning_type = CleaningType.objects.create(
            name="General",
            description="General cleaning",
        )


    def test_cleaner_creation(self):
        self.assertEqual(Cleaner.objects.count(), 1)


    def test_cleaner_str(self):
        self.assertEqual(str(self.cleaner), "John Smith")


    def test_cleaner_can_have_cleaning_type(self):
        self.cleaner.cleaning_types.add(self.cleaning_type)
        self.assertEqual(
            self.cleaner.cleaning_types.count(),
            1,
        )

    def test_cleaner_can_have_multiple_cleaning_types(self):
        self.cleaner.cleaning_types.add(
            self.cleaning_type,
            self.second_cleaning_type,
        )
        self.assertEqual(
            self.cleaner.cleaning_types.count(),
            2,
        )

    def test_cleaner_user(self):
        self.assertEqual(self.cleaner.user, self.user)


class CleaningTypeModelTests(TestCase):
    def test_cleaning_type_creation(self):
        cleaning_type = CleaningType.objects.create(
            name="Regular",
            description="Regular cleaning",
        )
        self.assertEqual(CleaningType.objects.count(), 1)

    def test_cleaning_type_str(self):
        cleaning_type = CleaningType.objects.create(
            name="Regular",
            description="Regular cleaning",
        )
        self.assertEqual(str(cleaning_type), "Regular")


class CleaningModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cleaner",
            password="testpassword1",
            role=UserRole.CLEANER,
        )
        self.property = Property.objects.create(
            name="Test House",
            address="test st. 10",
            property_type=PropertyType.HOUSE,
            rooms=4,
            owner=self.user,
        )
        self.cleaning_type = CleaningType.objects.create(
            name="Regular",
            description="Regular cleaning",
        )
        self.cleaner = Cleaner.objects.create(
            user=self.user,
            first_name="John",
            last_name="Smith",
            phone="123456789",
        )
        self.cleaning = Cleaning.objects.create(
            date="2026-10-03",
            cleaning_type=self.cleaning_type,
            property=self.property,
            cleaner=self.cleaner,
            status=StatusChoices.PLANNED,
        )


    def test_cleaning_creation(self):
        self.assertEqual(Cleaning.objects.count(), 1)


    def test_cleaning_str(self):
        self.assertEqual(
            str(self.cleaning),
            f"{self.cleaner} works on {self.property} at 2026-10-03",
        )


    def test_cleaning_property(self):
        self.assertEqual(self.cleaning.property, self.property)


    def test_cleaning_cleaner(self):
        self.assertEqual(self.cleaning.cleaner, self.cleaner)


    def test_cleaning_type(self):
        self.assertEqual(
            self.cleaning.cleaning_type,
            self.cleaning_type,
        )


    def test_cleaning_status(self):
        self.assertEqual(
            self.cleaning.status,
            StatusChoices.PLANNED,
        )


    def test_cleaning_date_property_cleaner_are_unique(self):
        with self.assertRaises(IntegrityError):
            Cleaning.objects.create(
                date=self.cleaning.date,
                cleaning_type=self.cleaning_type,
                property=self.property,
                cleaner=self.cleaner,
                status=StatusChoices.PLANNED,
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