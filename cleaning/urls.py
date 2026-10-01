from django.urls import path

from .views import home, PropertyListView, PropertyDetailView

app_name = "cleaning"

urlpatterns = [
    path("", home, name="home"),
    path("properties/", PropertyListView.as_view(), name="property-list"),
    path(
        "properties/<int:pk>/",
        PropertyDetailView.as_view(),
        name="property-detail",
    ),

]
