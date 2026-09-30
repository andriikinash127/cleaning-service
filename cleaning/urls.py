from django.urls import path

from .views import home

app_name = "cleaning"

urlpatterns = [
    path("", home, name="home"),
]
