from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    DetailView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView
)
from .models import (
    Property,
    Cleaning,
    CleaningType,
    UserRole,
)
from .forms import (
    PropertyForm,
    CleaningForm,
)
from mixins import PropertyManagementMixin


class HomeView(TemplateView):
    template_name = "home.html"


class PropertyListView(LoginRequiredMixin, ListView):
    model = Property
    template_name = "cleaning/property_list.html"
    paginate_by = 10
    ordering = "id"

    def get_queryset(self):
        queryset = Property.objects.for_user(self.request.user)

        search = self.request.GET.get("search")
        property_type = self.request.GET.get("property_type")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(address__icontains=search)
            )

        if property_type:
            queryset = queryset.filter(property_type=property_type)

        return queryset


class PropertyDetailView(LoginRequiredMixin, DetailView):
    model = Property
    template_name = "cleaning/property_detail.html"

    def get_queryset(self):
        return Property.objects.for_user(self.request.user)


class PropertyCreateView(
    PropertyManagementMixin,
    LoginRequiredMixin,
    CreateView
):
    model = Property
    form_class = PropertyForm
    template_name = "cleaning/property_form.html"
    success_url = reverse_lazy("cleaning:property-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        if self.request.user.role == UserRole.OWNER:
            form.instance.owner = self.request.user
        return super().form_valid(form)


class PropertyUpdateView(
    PropertyManagementMixin,
    LoginRequiredMixin,
    UpdateView
):
    model = Property
    form_class = PropertyForm
    template_name = "cleaning/property_form.html"
    success_url = reverse_lazy("cleaning:property-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        return Property.objects.for_user(self.request.user)

    def form_valid(self, form):
        if self.request.user.role == UserRole.OWNER:
            form.instance.owner = self.request.user
        return super().form_valid(form)


class PropertyDeleteView(
    PropertyManagementMixin,
    LoginRequiredMixin,
    DeleteView
):
    model = Property
    success_url = reverse_lazy("cleaning:property-list")

    def get_queryset(self):
        return Property.objects.for_user(self.request.user)


class CleaningListView(LoginRequiredMixin, ListView):
    model = Cleaning
    template_name = "cleaning/cleaning_list.html"
    paginate_by = 10
    ordering = "id"

    def get_queryset(self):
        queryset = Cleaning.objects.for_user(
            self.request.user
        ).select_related(
            "property",
            "cleaner",
            "cleaning_type",
        )

        search = self.request.GET.get("search")
        status = self.request.GET.get("status")
        cleaning_type = self.request.GET.get("cleaning_type")

        if search:
            queryset = queryset.filter(
                Q(property__name__icontains=search) |
                Q(cleaner__first_name__icontains=search) |
                Q(cleaner__last_name__icontains=search) |
                Q(cleaning_type__name__icontains=search)
            )

        if status:
            queryset = queryset.filter(status=status)

        if cleaning_type:
            queryset = queryset.filter(cleaning_type=cleaning_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cleaning_types"] = CleaningType.objects.all()
        return context


class CleaningDetailView(LoginRequiredMixin, DetailView):
    model = Cleaning
    template_name = "cleaning/cleaning_detail.html"

    def get_queryset(self):
        return Cleaning.objects.for_user(
            self.request.user
        ).select_related(
            "property",
            "cleaner",
            "cleaning_type",
        )


class CleaningCreateView(LoginRequiredMixin, CreateView):
    model = Cleaning
    form_class = CleaningForm
    template_name = "cleaning/cleaning_form.html"
    success_url = reverse_lazy("cleaning:cleaning-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        if self.request.user.role == UserRole.OWNER:
            if form.instance.property.owner != self.request.user:
                return redirect("cleaning:cleaning-list")
        elif self.request.user.role == UserRole.CLEANER:
            form.instance.cleaner = self.request.user.cleaner
        return super().form_valid(form)


class CleaningUpdateView(LoginRequiredMixin, UpdateView):
    model = Cleaning
    form_class = CleaningForm
    template_name = "cleaning/cleaning_form.html"
    success_url = reverse_lazy("cleaning:cleaning-list")

    def get_queryset(self):
        return Cleaning.objects.for_user(self.request.user)


class CleaningDeleteView(LoginRequiredMixin, DeleteView):
    model = Cleaning
    success_url = reverse_lazy("cleaning:cleaning-list")

    def get_queryset(self):
        return Cleaning.objects.for_user(self.request.user)


class CleaningTypeListView(ListView):
    model = CleaningType
    template_name = "cleaning/cleaning_type_list.html"


class CleaningTypeDetailView(DetailView):
    model = CleaningType
    template_name = "cleaning/cleaning_type_detail.html"
    context_object_name = "cleaning_type"
