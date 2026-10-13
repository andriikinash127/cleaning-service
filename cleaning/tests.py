from datetime import date

from django.test import TestCase
from django.db import IntegrityError
from django.urls import reverse

from .models import (
    User,
    UserRole,
    Property,
    PropertyType,
    Cleaner,
    CleaningType,
    Cleaning,
    StatusChoices,
    CleaningTypeChoices,
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


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword1",
            role=UserRole.OWNER,
        )

    def test_user_can_login(self):
        response = self.client.post(
            reverse("cleaning:login"),
            {
                "username": "testuser",
                "password": "testpassword1",
            },
        )
        self.assertRedirects(response, "/")
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_cannot_login_with_wrong_password(self):
        response = self.client.post(
            reverse("cleaning:login"),
            {
                "username": "testuser",
                "password": "wrongpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_nonexistent_user_cannot_login(self):
        response = self.client.post(
            reverse("cleaning:login"),
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
        response = self.client.post(
            reverse("cleaning:logout"),
        )
        self.assertRedirects(response, "/")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_unauthenticated_user_cannot_access_properties(self):
        response = self.client.get(
            reverse("cleaning:property-list"),
        )
        self.assertRedirects(
            response,
            "/login/?next=/properties/",
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
        response = self.client.get(
            reverse("cleaning:property-list"),
        )
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
            reverse("cleaning:property-create"),
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
            reverse("cleaning:property-create"),
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
            reverse("cleaning:property-create"),
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
        response = self.client.get(
            reverse("cleaning:cleaner-list"),
        )
        self.assertEqual(response.status_code, 200)

    def test_cleaner_detail_view(self):
        response = self.client.get(
            reverse(
                "cleaning:cleaner-detail",
                kwargs={"pk": self.cleaner.pk},
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_cleaner_detail_view_with_invalid_pk(self):
        response = self.client.get(
            reverse(
                "cleaning:cleaner-detail",
                kwargs={"pk": 9999},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_cleaner_create_view_creates_cleaner(self):
        response = self.client.post(
            reverse("cleaning:cleaner-create"),
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
                "cleaning:cleaner-update",
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
                "cleaning:cleaner-delete",
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
            reverse("cleaning:cleaner-create"),
        )
        self.assertRedirects(
            response,
            "/login/?next=/cleaners/create/",
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
            reverse("cleaning:cleaner-create"),
        )
        self.assertRedirects(
            response,
            reverse("cleaning:cleaner-list"),
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
        )
        response = self.client.get(
            reverse("cleaning:cleaner-create"),
        )
        self.assertRedirects(
            response,
            reverse("cleaning:cleaner-list"),
        )


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
            reverse("cleaning:cleaning-type-list"),
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
            reverse("cleaning:cleaning-type-list"),
        )
        self.assertEqual(response.status_code, 200)


class CleaningViewTests(TestCase):
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
            date="2026-10-03",
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
            reverse("cleaning:cleaning-list"),
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
        response = self.client.post(
            reverse("cleaning:cleaning-create"),
            {
                "date": "2026-10-10",
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "cleaner": self.cleaner.pk,
                "status": StatusChoices.PLANNED,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Cleaning.objects.filter(
                date="2026-10-10",
                cleaning_type=self.cleaning_type,
                property=self.property,
                cleaner=self.cleaner,
            ).exists()
        )

    def test_cleaning_update_view_updates_cleaning(self):
        response = self.client.post(
            reverse(
                "cleaning:cleaning-update",
                kwargs={"pk": self.cleaning.pk},
            ),
            {
                "date": "2026-10-15",
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "cleaner": self.cleaner.pk,
                "status": StatusChoices.DONE,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.cleaning.refresh_from_db()
        self.assertEqual(
            self.cleaning.date,
            date(2026, 10, 15),
        )
        self.assertEqual(
            self.cleaning.status,
            StatusChoices.DONE,
        )

    def test_cleaning_delete_view_deletes_cleaning(self):
        response = self.client.post(
            reverse(
                "cleaning:cleaning-delete",
                kwargs={"pk": self.cleaning.pk},
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Cleaning.objects.filter(
                pk=self.cleaning.pk
            ).exists()
        )

    def test_unauthenticated_user_cannot_create_cleaning(self):
        self.client.logout()
        response = self.client.get(
            reverse("cleaning:cleaning-create"),
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
        Cleaner.objects.create(
            user=cleaner_user,
            first_name="Mike",
            last_name="Brown",
            phone="+380991234567",
        )
        cleaner_user.cleaner.cleaning_types.add(self.cleaning_type)
        self.client.login(
            username="cleaner",
            password="password123",
        )
        response = self.client.post(
            reverse("cleaning:cleaning-create"),
            {
                "date": "2026-10-10",
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "status": StatusChoices.PLANNED,
            },
        )
        self.assertEqual(response.status_code, 302)
        cleaning = Cleaning.objects.get(
            date="2026-10-10",
            property=self.property,
        )
        self.assertEqual(
            cleaning.cleaner,
            cleaner_user.cleaner,
        )

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
                "date": "2026-10-10",
                "cleaning_type": self.cleaning_type.pk,
                "property": self.property.pk,
                "cleaner": self.cleaner.pk,
                "status": StatusChoices.PLANNED,
            },
        )
        self.assertRedirects(
            response,
            reverse("cleaning:cleaning-list"),
        )

    def test_cleaning_filter_by_status(self):
        Cleaning.objects.create(
            date="2026-10-10",
            cleaning_type=self.cleaning_type,
            property=self.property,
            cleaner=self.cleaner,
            status=StatusChoices.DONE,
        )
        response = self.client.get(
            reverse("cleaning:cleaning-list"),
            {"status": StatusChoices.DONE},
        )
        self.assertContains(response, "2026-10-10")
        self.assertNotContains(response, "2026-10-03")
