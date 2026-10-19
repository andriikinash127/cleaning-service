from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from users.mixins import ManagerRequiredMixin
from users.forms import (
    CleanerForm,
    OwnerPropertyForm,
    UserRegistrationForm,
)
from users.models import Cleaner, UserRole


class UserLoginView(LoginView):
    template_name = "registration/login.html"


class UserLogoutView(LogoutView):
    next_page = "/"


class MeView(LoginRequiredMixin, TemplateView):
    template_name = "users/me.html"


class RegisterView(TemplateView):
    template_name = "registration/register.html"


class OwnerRegisterView(TemplateView):
    template_name = "registration/owner_register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("user_form", UserRegistrationForm())
        context.setdefault("property_form", OwnerPropertyForm())
        return context

    def post(self, request, *args, **kwargs):
        user_form = UserRegistrationForm(request.POST)
        property_form = OwnerPropertyForm(request.POST)

        if user_form.is_valid() and property_form.is_valid():
            user = user_form.save(commit=False)
            user.role = UserRole.OWNER
            user.save()

            property_obj = property_form.save(commit=False)
            property_obj.owner = user
            property_obj.save()

            login(request, user)
            return redirect("cleaning:home")

        return self.render_to_response(
            self.get_context_data(
                user_form=user_form,
                property_form=property_form,
            )
        )


class CleanerRegisterView(TemplateView):
    template_name = "registration/cleaner_register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("user_form", UserRegistrationForm())
        context.setdefault("cleaner_form", CleanerForm())
        return context

    def post(self, request, *args, **kwargs):
        user_form = UserRegistrationForm(request.POST)
        cleaner_form = CleanerForm(request.POST)

        if user_form.is_valid() and cleaner_form.is_valid():
            user = user_form.save(commit=False)
            user.role = UserRole.CLEANER
            user.save()

            cleaner = cleaner_form.save(commit=False)
            cleaner.user = user
            cleaner.save()
            cleaner_form.save_m2m()

            login(request, user)
            return redirect("cleaning:home")

        return self.render_to_response(
            self.get_context_data(
                user_form=user_form,
                cleaner_form=cleaner_form,
            )
        )


class CleanerListView(
    LoginRequiredMixin,
    ListView
):
    model = Cleaner
    template_name = "users/cleaner_list.html"
    paginate_by = 5
    ordering = "id"

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related(
            "cleaning_types",
        )
        search = self.request.GET.get("search")
        cleaning_type = self.request.GET.get("cleaning_type")

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        if cleaning_type:
            queryset = queryset.filter(
                cleaning_types__name=cleaning_type
            )

        return queryset


class CleanerDetailView(
    DetailView
):
    model = Cleaner
    template_name = "users/cleaner_detail.html"

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            "cleaning_types",
        )


class CleanerUpdateView(ManagerRequiredMixin, UpdateView):
    model = Cleaner
    form_class = CleanerForm
    template_name = "users/cleaner_form.html"
    success_url = reverse_lazy("users:cleaner-list")


class CleanerDeleteView(
    LoginRequiredMixin,
    ManagerRequiredMixin,
    DeleteView
):
    model = Cleaner
    success_url = reverse_lazy("users:cleaner-list")


class CleanerCreateView(
    LoginRequiredMixin,
    ManagerRequiredMixin,
    CreateView,):
    model = Cleaner
    form_class = CleanerForm
    template_name = "users/cleaner_form.html"
    success_url = reverse_lazy("users:cleaner-list")
