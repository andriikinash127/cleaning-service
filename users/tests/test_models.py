from django.test import TestCase

from users.models import Cleaner, User, UserRole
from cleaning.models import CleaningType


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
