from django.urls import path

from .views import (
    HomeView,
    PropertyListView,
    PropertyDetailView,
    PropertyCreateView,
    PropertyUpdateView,
    PropertyDeleteView,
    CleaningListView,
    CleaningDetailView,
    CleaningCreateView,
    CleaningUpdateView,
    CleaningDeleteView,
    CleaningTypeListView,
    CleaningTypeDetailView,
)

app_name = "cleaning"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),

    path("properties/", PropertyListView.as_view(), name="property-list"),
    path(
        "properties/<int:pk>/",
        PropertyDetailView.as_view(),
        name="property-detail",
    ),
    path(
        "properties/create/",
        PropertyCreateView.as_view(),
        name="property-create"
    ),
    path(
        "properties/<int:pk>/update/",
        PropertyUpdateView.as_view(),
        name="property-update",
    ),
    path(
        "properties/<int:pk>/delete/",
        PropertyDeleteView.as_view(),
        name="property-delete",
    ),

    path("cleanings/", CleaningListView.as_view(), name="cleaning-list"),
    path(
        "cleanings/<int:pk>/",
        CleaningDetailView.as_view(),
        name="cleaning-detail",
    ),
    path(
        "cleanings/create/",
        CleaningCreateView.as_view(),
        name="cleaning-create"
    ),
    path(
        "cleanings/<int:pk>/update/",
        CleaningUpdateView.as_view(),
        name="cleaning-update",
    ),
    path(
        "cleanings/<int:pk>/delete/",
        CleaningDeleteView.as_view(),
        name="cleaning-delete",
    ),

    path(
        "cleaning-types/",
        CleaningTypeListView.as_view(),
        name="cleaning-type-list",
    ),
    path(
        "cleaning-types/<int:pk>/",
        CleaningTypeDetailView.as_view(),
        name="cleaning-type-detail",
    ),
]
