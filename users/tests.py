from django.test import TestCase
from django.urls import reverse

from users.models import Cleaner, User, UserRole
from cleaning.models import (
    CleaningType,
    CleaningTypeChoices,
    Property,
    PropertyType,
)


class MeViewTests(TestCase):
    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("users:me"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_owner_sees_own_profile_and_properties(self):
        owner = User.objects.create_user(
            username="owner1", password="pass12345", role=UserRole.OWNER
        )
        Property.objects.create(
            name="My flat",
            address="1 Main St",
            apartment_number=1,
            property_type=PropertyType.APARTMENT,
            rooms=2,
            owner=owner,
        )
        self.client.force_login(owner)

        response = self.client.get(reverse("users:me"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "owner1")
        self.assertContains(response, "My flat")

    def test_cleaner_sees_phone_and_cleaning_types(self):
        user = User.objects.create_user(
            username="cleaner1", password="pass12345", role=UserRole.CLEANER
        )
        cleaner = Cleaner.objects.create(
            user=user, first_name="Ann", last_name="Lee", phone="12345"
        )
        cleaner.cleaning_types.add(
            CleaningType.objects.create(
                name=CleaningTypeChoices.DEEP, description="Deep"
            )
        )
        self.client.force_login(user)

        response = self.client.get(reverse("users:me"))

        self.assertContains(response, "12345")
        self.assertContains(response, CleaningTypeChoices.DEEP.label)

    def test_cleaner_without_profile_does_not_crash(self):
        user = User.objects.create_user(
            username="nocleaner", password="pass12345", role=UserRole.CLEANER
        )
        self.client.force_login(user)

        response = self.client.get(reverse("users:me"))

        self.assertEqual(response.status_code, 200)
