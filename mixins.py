from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

from cleaning.models import UserRole


class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return (
            user.is_authenticated
            and user.role == UserRole.MANAGER
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        return redirect("users:cleaner-list")



class PropertyManagementMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.role
            in (UserRole.OWNER, UserRole.MANAGER)
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        return redirect("cleaning:property-list")
