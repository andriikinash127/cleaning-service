from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Cleaner


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )


@admin.register(Cleaner)
class CleanerAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "phone",
    )
    search_fields = ("first_name", "last_name", "phone")
