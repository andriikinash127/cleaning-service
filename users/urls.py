
from django.urls import path

from .views import (
    UserLoginView,
    UserLogoutView,
    MeView,
    RegisterView,
    OwnerRegisterView,
    CleanerRegisterView,
    CleanerListView,
    CleanerDetailView,
    CleanerCreateView,
    CleanerUpdateView,
    CleanerDeleteView,
)

app_name = "users"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "register/owner/",
        OwnerRegisterView.as_view(),
        name="register-owner",
    ),
    path(
        "register/cleaner/",
        CleanerRegisterView.as_view(),
        name="register-cleaner",
    ),
    path("cleaners/", CleanerListView.as_view(), name="cleaner-list"),
    path(
        "cleaners/<int:pk>/",
        CleanerDetailView.as_view(),
        name="cleaner-detail",
    ),
    path(
        "cleaners/create/",
        CleanerCreateView.as_view(),
        name="cleaner-create",
    ),
    path(
        "cleaners/<int:pk>/update/",
        CleanerUpdateView.as_view(),
        name="cleaner-update",
    ),
    path(
        "cleaners/<int:pk>/delete/",
        CleanerDeleteView.as_view(),
        name="cleaner-delete",
    ),
]
