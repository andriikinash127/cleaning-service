from django.contrib import admin
from django.urls import include, path

app_name = "cleaning"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("cleaning.urls")),

]