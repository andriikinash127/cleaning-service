
from django.test import TestCase
from django.db import IntegrityError

from users.models import UserRole, User, Cleaner
from cleaning.models import (
    Property,
    PropertyType,
    CleaningType,
    Cleaning,
    StatusChoices,
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
        CleaningType.objects.create(
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
