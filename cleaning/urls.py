from django.urls import path

from .views import (home,
                    PropertyListView,
                    PropertyDetailView,
                    PropertyCreateView,
                    PropertyUpdateView,
                    PropertyDeleteView,
                    CleanerListView,
                    CleanerDetailView,
                    CleanerUpdateView,
                    CleanerDeleteView,
                    CleanerCreateView,
                    )

app_name = "cleaning"

urlpatterns = [
    path("", home, name="home"),
    path("properties/",
         PropertyListView.as_view(),
         name="property-list"
         ),
    path(
        "properties/<int:pk>/",
        PropertyDetailView.as_view(),
        name="property-detail"
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
    path(
        "cleaners/",
        CleanerListView.as_view(),
        name="cleaner-list"
    ),
    path(
        "cleaners/<int:pk>/",
        CleanerDetailView.as_view(),
        name="cleaner-detail"
    ),
    path(
        "cleaners/<int:pk>/update/",
        CleanerUpdateView.as_view(),
        name="cleaner-update",
    ),
    path(
        "cleaners/<int:pk>/delete/",
        CleanerDeleteView.as_view(),
        name="cleaner-delete"
    ),
    path(
        "cleaners/create/",
        CleanerCreateView.as_view(),
        name="cleaner-create"
    ),
]
