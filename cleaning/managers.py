from django.db import models


class PropertyManager(models.Manager):
    def for_user(self, user):
        queryset = self.get_queryset()

        if user.role == "owner":
            return queryset.filter(owner=user)

        return queryset


class CleaningManager(models.Manager):
    def for_user(self, user):
        queryset = self.get_queryset()

        if user.role == "owner":
            return queryset.filter(property__owner=user)

        if user.role == "cleaner":
            return queryset.filter(cleaner=user.cleaner)

        return queryset
