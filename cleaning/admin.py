from django.contrib import admin

from .models import User, Property, CleaningType, Cleaning, Cleaner


admin.site.register(User)


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


@admin.register(Cleaner)
class CleanerAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "phone",
    )
    search_fields = ("first_name", "last_name", "phone")


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
