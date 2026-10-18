from django.contrib import admin
from django.urls import include, path
from users.views import UserLoginView, UserLogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("login/", UserLoginView.as_view(), name="legacy-login"),
    path("logout/", UserLogoutView.as_view(), name="legacy-logout"),
    path("", include("cleaning.urls")),
]
