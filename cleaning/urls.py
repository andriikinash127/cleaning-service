from django.urls import path

from .views import (home,
                    PropertyListView,
                    PropertyDetailView,
                    PropertyCreateView,
                    PropertyUpdateView,
                    PropertyDeleteView,

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
    )
]
