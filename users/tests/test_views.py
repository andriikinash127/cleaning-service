from django.test import TestCase
from django.urls import reverse

from users.models import Cleaner, User, UserRole
from cleaning.models import (
    CleaningType,
    CleaningTypeChoices,
    Property,
    PropertyType,
)


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword1",
            role=UserRole.OWNER,
        )

    def test_user_can_login(self):
        response = self.client.post(
            reverse("users:login"),
            {
                "username": "testuser",
                "password": "testpassword1",
            },
        )
        self.assertRedirects(response, "/")
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_cannot_login_with_wrong_password(self):
        response = self.client.post(
            reverse("users:login"),
            {
                "username": "testuser",
                "password": "wrongpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_nonexistent_user_cannot_login(self):
        response = self.client.post(
            reverse("users:login"),
            {
                "username": "unknownuser",
                "password": "testpassword1",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_user_can_logout(self):
        self.client.login(
            username="testuser",
            password="testpassword1",
        )
        response = self.client.post(reverse("users:logout"))
        self.assertRedirects(response, "/")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_unauthenticated_user_cannot_access_properties(self):
        response = self.client.get(reverse("cleaning:property-list"))
        self.assertRedirects(
            response,
            "/login/?next=/properties/",
        )


class CleanerViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword1",
            role=UserRole.MANAGER,
        )
        self.client.login(
            username="testuser",
            password="testpassword1",
        )
        self.cleaning_type = CleaningType.objects.create(
            name=CleaningTypeChoices.REGULAR,
            description="Regular cleaning",
        )
        self.cleaner = Cleaner.objects.create(
            first_name="John",
            last_name="Smith",
            phone="+380991234567",
        )

    def test_cleaner_list_view(self):
        response = self.client.get(reverse("users:cleaner-list"))
        self.assertEqual(response.status_code, 200)

    def test_cleaner_detail_view(self):
        response = self.client.get(
            reverse(
                "users:cleaner-detail",
                kwargs={"pk": self.cleaner.pk},
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_cleaner_detail_view_with_invalid_pk(self):
        response = self.client.get(
            reverse(
                "users:cleaner-detail",
                kwargs={"pk": 9999},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_cleaner_create_view_creates_cleaner(self):
        response = self.client.post(
            reverse("users:cleaner-create"),
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "phone": "+380991112233",
                "cleaning_types": [self.cleaning_type.pk],
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_cleaner_update_view_updates_cleaner(self):
        response = self.client.post(
            reverse(
                "users:cleaner-update",
                kwargs={"pk": self.cleaner.pk},
            ),
            {
                "first_name": "Updated",
                "last_name": "Cleaner",
                "phone": "+380991234567",
                "cleaning_types": [self.cleaning_type.pk],
            },
        )
        self.assertEqual(response.status_code, 302)
        self.cleaner.refresh_from_db()
        self.assertEqual(self.cleaner.first_name, "Updated")
        self.assertEqual(self.cleaner.last_name, "Cleaner")
        self.assertEqual(self.cleaner.phone, "+380991234567")

    def test_cleaner_delete_view_deletes_cleaner(self):
        response = self.client.post(
            reverse(
                "users:cleaner-delete",
                kwargs={"pk": self.cleaner.pk},
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Cleaner.objects.filter(pk=self.cleaner.pk).exists()
        )

    def test_unauthenticated_user_cannot_create_cleaner(self):
        self.client.logout()
        response = self.client.get(
            reverse("users:cleaner-create")
        )
        self.assertRedirects(
            response,
            "/login/?next=/users/cleaners/create/",
        )

    def test_owner_cannot_create_cleaner(self):
        User.objects.create_user(
            username="owner",
            password="password123",
            role=UserRole.OWNER,
        )
        self.client.login(
            username="owner",
            password="password123",
        )
        response = self.client.get(
            reverse("users:cleaner-create")
        )
        self.assertRedirects(
            response,
            reverse("users:cleaner-list"),
        )

    def test_cleaner_cannot_create_cleaner(self):
        User.objects.create_user(
            username="cleaner",
            password="password123",
            role=UserRole.CLEANER,
        )
        self.client.login(
            username="cleaner",
            password="password123",
            role=UserRole.CLEANER,
        )
        response = self.client.get(
            reverse("users:cleaner-create")
        )
        self.assertRedirects(
            response,
            reverse("users:cleaner-list"),
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


class CleanerAccessTests(TestCase):
    def setUp(self):
        self.cleaner = Cleaner.objects.create(
            first_name="John",
            last_name="Smith",
            phone="+380991234567",
        )
        self.owner = User.objects.create_user(
            username="owner",
            password="testpassword1",
            role=UserRole.OWNER,
        )
        self.cleaner_user = User.objects.create_user(
            username="cleaner_user",
            password="testpassword1",
            role=UserRole.CLEANER,
        )

    def test_anonymous_user_is_redirected_from_cleaner_list(self):
        response = self.client.get(reverse("users:cleaner-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_anonymous_user_is_redirected_from_cleaner_detail(self):
        response = self.client.get(
            reverse("users:cleaner-detail", kwargs={"pk": self.cleaner.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_owner_and_cleaner_cannot_update_or_delete_cleaner(self):
        for user in (self.owner, self.cleaner_user):
            self.client.force_login(user)
            for name in ("users:cleaner-update", "users:cleaner-delete"):
                url = reverse(name, kwargs={"pk": self.cleaner.pk})
                response = self.client.post(url, {"first_name": "Hacked"})
                self.assertRedirects(
                    response,
                    reverse("users:cleaner-list"),
                )
        self.cleaner.refresh_from_db()
        self.assertEqual(self.cleaner.first_name, "John")
