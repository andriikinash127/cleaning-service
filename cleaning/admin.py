from django.contrib import admin

from .models import Property, CleaningType, Cleaning


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "address",
        "property_type",
        "rooms",
        "owner",
    )
    list_filter = ("property_type",)
    search_fields = ("name", "address")


@admin.register(CleaningType)
class CleaningTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )
    search_fields = ("name", "description")


@admin.register(Cleaning)
class CleaningAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "cleaning_type",
        "status",
        "property",
        "cleaner",
    )
    list_filter = (
        "status",
        "cleaning_type",
    )
    search_fields = (
        "property__name",
        "cleaner__first_name",
        "cleaner__last_name",
    )
