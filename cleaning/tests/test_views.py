from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from users.models import UserRole, User, Cleaner

from cleaning.models import (
    Property,
    PropertyType,
    CleaningType,
    Cleaning,
    StatusChoices,
    CleaningTypeChoices,
)


class PropertyViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword1",
            role=UserRole.MANAGER,
        )
        self.property = Property.objects.create(
            name="Test House",
            address="test st. 10",
            property_type=PropertyType.HOUSE,
            rooms=4,
            owner=self.user,
        )
        self.client.login(
            username="testuser",
            password="testpassword1",
        )

    def test_property_list_view(self):
        response = self.client.get(reverse("cleaning:property-list"))
        self.assertEqual(response.status_code, 200)

    def test_property_detail_view(self):
        response = self.client.get(
            reverse(
                "cleaning:property-detail",
                kwargs={"pk": self.property.pk},
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_property_detail_view_with_invalid_pk(self):
        response = self.client.get(
            reverse(
                "cleaning:property-detail",
                kwargs={"pk": 9999},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_property_create_view_creates_property(self):
        response = self.client.post(
            reverse("cleaning:property-create"),
            {
                "name": "New House",
                "address": "new st. 15",
                "property_type": PropertyType.HOUSE,
                "rooms": 3,
                "owner": self.user.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Property.objects.filter(name="New House").exists()
        )

    def test_property_update_view_updates_property(self):
        response = self.client.post(
            reverse(
                "cleaning:property-update",
                kwargs={"pk": self.property.pk},
            ),
            {
                "name": "Updated House",
                "address": "updated st. 20",
                "property_type": PropertyType.HOUSE,
                "rooms": 5,
                "owner": self.user.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.property.refresh_from_db()
        self.assertEqual(self.property.name, "Updated House")
        self.assertEqual(self.property.address, "updated st. 20")
        self.assertEqual(self.property.rooms, 5)

    def test_property_delete_view_deletes_property(self):
        response = self.client.post(
            reverse(
                "cleaning:property-delete",
                kwargs={"pk": self.property.pk},
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Property.objects.filter(pk=self.property.pk).exists()
        )

    def test_unauthenticated_user_cannot_create_property(self):
        self.client.logout()
        response = self.client.get(
            reverse("cleaning:property-create")
        )
        self.assertRedirects(
            response,
            "/login/?next=/properties/create/",
        )

    def test_owner_can_create_property(self):
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
            reverse("cleaning:property-create")
        )
        self.assertEqual(response.status_code, 200)

    def test_cleaner_cannot_create_property(self):
        User.objects.create_user(
            username="cleaner",
            password="password123",
            role=UserRole.CLEANER,
        )
        self.client.login(
            username="cleaner",
            password="password123",
        )
        response = self.client.get(
            reverse("cleaning:property-create")
        )
        self.assertRedirects(
            response,
            reverse("cleaning:property-list"),
        )

    def test_property_search(self):
        Property.objects.create(
            name="Big House",
            address="Main Street 10",
            property_type=PropertyType.HOUSE,
            rooms=5,
            owner=self.user,
        )
        Property.objects.create(
            name="Small Apartment",
            address="Other Street 5",
            apartment_number=10,
            property_type=PropertyType.APARTMENT,
            rooms=2,
            owner=self.user,
        )
        response = self.client.get(
            reverse("cleaning:property-list"),
            {"search": "Big"},
        )
        self.assertContains(response, "Big House")
        self.assertNotContains(response, "Small Apartment")

    def test_property_pagination(self):
        for i in range(11):
            Property.objects.create(
                name=f"Property {i}",
                address=f"Street {i}",
                property_type=PropertyType.HOUSE,
                rooms=3,
                owner=self.user,
            )
        response = self.client.get(
            reverse("cleaning:property-list"),
            {"page": 2},
        )
        self.assertContains(response, "Property 10")
        self.assertNotContains(response, "Property 0")


class CleaningTypeViewTests(TestCase):
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

    def test_cleaning_type_list_view(self):
        response = self.client.get(
            reverse("cleaning:cleaning-type-list")
        )
        self.assertEqual(response.status_code, 200)

    def test_cleaning_type_detail_view(self):
        response = self.client.get(
            reverse(
                "cleaning:cleaning-type-detail",
                kwargs={"pk": self.cleaning_type.pk},
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_cleaning_type_detail_view_with_invalid_pk(self):
        response = self.client.get(
            reverse(
                "cleaning:cleaning-type-detail",
                kwargs={"pk": 9999},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_can_view_cleaning_type_list(self):
        self.client.logout()
        response = self.client.get(
            reverse("cleaning:cleaning-type-list")
        )
        self.assertEqual(response.status_code, 200)


class CleaningViewTests(TestCase):
    def future_datetime(self):
        return (
            timezone.now() + timedelta(days=2)
        ).strftime("%Y-%m-%dT%H:%M")

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword1",
            role=UserRole.MANAGER,
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
        self.cleaner.cleaning_types.add(self.cleaning_type)
        self.property = Property.objects.create(
            name="Test House",
            address="test st. 10",
            property_type=PropertyType.HOUSE,
            rooms=4,
            owner=self.user,
        )
        self.cleaning = Cleaning.objects.create(
            date=timezone.now() + timedelta(days=2),
            cleaning_type=self.cleaning_type,
            property=self.property,
            cleaner=self.cleaner,
            status=StatusChoices.PLANNED,
        )
        self.client.login(
            username="testuser",
            password="testpassword1",
        )

    def test_cleaning_list_view(self):
        response = self.client.get(
            reverse("cleaning:cleaning-list")
        )
        self.assertEqual(response.status_code, 200)

    def test_cleaning_detail_view(self):
        response = self.client.get(
            reverse(
                "cleaning:cleaning-detail",
                kwargs={"pk": self.cleaning.pk},
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_cleaning_detail_view_with_invalid_pk(self):
        response = self.client.get(
            reverse(
                "cleaning:cleaning-detail",
                kwargs={"pk": 9999},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_cleaning_create_view_creates_cleaning(self):
        cleaning_date = self.future_datetime()

        response = self.client.post(
            reverse("cleaning:cleaning-create"),
            {
                "date": cleaning_date,
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "cleaner": self.cleaner.pk,
                "status": StatusChoices.PLANNED,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
            getattr(response, "context", {}).get("form").errors
            if response.context and response.context.get("form")
            else "",
        )
        self.assertTrue(
            Cleaning.objects.filter(
                cleaning_type=self.cleaning_type,
                property=self.property,
                cleaner=self.cleaner,
                status=StatusChoices.PLANNED,
            ).exists()
        )

    def test_cleaning_is_created_as_planned_by_default(self):
        self.client.post(
            reverse("cleaning:cleaning-create"),
            {
                "date": self.future_datetime(),
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "cleaner": self.cleaner.pk,
                "status": StatusChoices.DONE,
            },
        )

        new_cleaning = Cleaning.objects.exclude(pk=self.cleaning.pk).get()
        self.assertEqual(new_cleaning.status, StatusChoices.PLANNED)

    def test_cleaning_update_view_updates_cleaning(self):
        cleaning_date = self.future_datetime()

        response = self.client.post(
            reverse(
                "cleaning:cleaning-update",
                kwargs={"pk": self.cleaning.pk},
            ),
            {
                "date": cleaning_date,
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "cleaner": self.cleaner.pk,
                "status": StatusChoices.DONE,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
            getattr(response, "context", {}).get("form").errors
            if response.context and response.context.get("form")
            else "",
        )
        self.cleaning.refresh_from_db()
        self.assertEqual(
            self.cleaning.date.replace(second=0, microsecond=0),
            timezone.datetime.strptime(
                cleaning_date, "%Y-%m-%dT%H:%M"
            ).replace(tzinfo=timezone.get_current_timezone()),
        )
        self.assertEqual(self.cleaning.status, StatusChoices.DONE)

    def test_cleaning_delete_view_deletes_cleaning(self):
        response = self.client.post(
            reverse(
                "cleaning:cleaning-delete",
                kwargs={"pk": self.cleaning.pk},
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Cleaning.objects.filter(pk=self.cleaning.pk).exists()
        )

    def test_unauthenticated_user_cannot_create_cleaning(self):
        self.client.logout()
        response = self.client.get(
            reverse("cleaning:cleaning-create")
        )
        self.assertRedirects(
            response,
            "/login/?next=/cleanings/create/",
        )

    def test_cleaner_is_assigned_to_created_cleaning(self):
        cleaner_user = User.objects.create_user(
            username="cleaner",
            password="password123",
            role=UserRole.CLEANER,
        )
        cleaner = Cleaner.objects.create(
            user=cleaner_user,
            first_name="Mike",
            last_name="Brown",
            phone="+380991234567",
        )
        cleaner.cleaning_types.add(self.cleaning_type)

        self.client.login(
            username="cleaner",
            password="password123",
        )
        cleaning_date = self.future_datetime()

        response = self.client.post(
            reverse("cleaning:cleaning-create"),
            {
                "date": cleaning_date,
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "status": StatusChoices.PLANNED,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
            getattr(response, "context", {}).get("form").errors
            if response.context and response.context.get("form")
            else "",
        )
        cleaning = Cleaning.objects.get(
            property=self.property,
            cleaner=cleaner,
            cleaning_type=self.cleaning_type,
            status=StatusChoices.PLANNED,
        )
        self.assertEqual(cleaning.cleaner, cleaner)

    def test_owner_cannot_create_cleaning_for_other_property(self):
        User.objects.create_user(
            username="owner",
            password="password123",
            role=UserRole.OWNER,
        )
        self.client.login(
            username="owner",
            password="password123",
        )

        response = self.client.post(
            reverse("cleaning:cleaning-create"),
            {
                "date": self.future_datetime(),
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "cleaner": self.cleaner.pk,
                "status": StatusChoices.PLANNED,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("property", response.context["form"].errors)
        self.assertEqual(Cleaning.objects.count(), 1)

    def test_cleaning_filter_by_status(self):
        Cleaning.objects.create(
            date=timezone.now() + timedelta(days=3),
            cleaning_type=self.cleaning_type,
            property=self.property,
            cleaner=self.cleaner,
            status=StatusChoices.DONE,
        )

        response = self.client.get(
            reverse("cleaning:cleaning-list"),
            {"status": StatusChoices.DONE},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "finished")


class CleaningUpdateFormTests(TestCase):
    def test_cleaner_sees_only_own_types_on_update(self):
        user = User.objects.create_user(
            username="cleaner",
            password="testpassword1",
            role=UserRole.CLEANER,
        )
        owner = User.objects.create_user(
            username="owner",
            password="testpassword1",
            role=UserRole.OWNER,
        )
        own_type = CleaningType.objects.create(
            name=CleaningTypeChoices.REGULAR,
            description="Regular",
        )
        other_type = CleaningType.objects.create(
            name=CleaningTypeChoices.DEEP,
            description="Deep",
        )
        cleaner = Cleaner.objects.create(
            user=user,
            first_name="Ann",
            last_name="Lee",
            phone="123",
        )
        cleaner.cleaning_types.add(own_type)
        prop = Property.objects.create(
            name="Flat",
            address="st. 1",
            property_type=PropertyType.HOUSE,
            rooms=2,
            owner=owner,
        )
        cleaning = Cleaning.objects.create(
            date=timezone.now() + timedelta(days=2),
            cleaning_type=own_type,
            property=prop,
            cleaner=cleaner,
        )
        self.client.force_login(user)

        response = self.client.get(
            reverse("cleaning:cleaning-update", kwargs={"pk": cleaning.pk})
        )

        types = response.context["form"].fields["cleaning_type"].queryset
        self.assertIn(own_type, types)
        self.assertNotIn(other_type, types)
