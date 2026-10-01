from multiprocessing.connection import address_type

from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
    DetailView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import (
    Property,
    Cleaner,
    Cleaning,
    CleaningType
)
from .forms import (
    PropertyForm,
    CleanerForm,
    CleaningForm
)


def home(request):
    return render(request, "home.html")


class PropertyListView(ListView):
    model = Property
    template_name = "cleaning/property_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(address__icontains=search)
            )
        return queryset


class PropertyDetailView(DetailView):
    model = Property
    template_name = "cleaning/property_detail.html"


class PropertyCreateView(CreateView):
    model = Property
    form_class = PropertyForm
    template_name = "cleaning/property_form.html"
    success_url = reverse_lazy("cleaning:property-list")


class PropertyUpdateView(UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = "cleaning/property_form.html"
    success_url = reverse_lazy("cleaning:property-list")


class PropertyDeleteView(DeleteView):
    model = Property
    success_url = reverse_lazy("cleaning:property-list")


class CleanerListView(ListView):
    model = Cleaner
    template_name = "cleaning/cleaner_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search")

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        return queryset


class CleanerDetailView(DetailView):
    model = Cleaner
    template_name = "cleaning/cleaner_detail.html"


class CleanerUpdateView(UpdateView):
    model = Cleaner
    form_class = CleanerForm
    template_name = "cleaning/cleaner_form.html"
    success_url = reverse_lazy("cleaning:cleaner-list")


class CleanerDeleteView(DeleteView):
    model = Cleaner
    success_url = reverse_lazy("cleaning:cleaner-list")


class CleanerCreateView(CreateView):
    model = Cleaner
    form_class = CleanerForm
    template_name = "cleaning/cleaner_form.html"
    success_url = reverse_lazy("cleaning:cleaner-list")


class CleaningListView(ListView):
    model = Cleaning
    template_name = "cleaning/cleaning_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search")

        if search:
            queryset = queryset.filter(
                Q(property__name__icontains=search) |
                Q(cleaner__first_name__icontains=search) |
                Q(cleaner__last_name__icontains=search) |
                Q(cleaning_type__name__icontains=search)
            )
        return queryset


class CleaningDetailView(DetailView):
    model = Cleaning
    template_name = "cleaning/cleaning_detail.html"


class CleaningCreateView(CreateView):
    model = Cleaning
    form_class = CleaningForm
    template_name = "cleaning/cleaning_form.html"
    success_url = reverse_lazy("cleaning:cleaning-list")


class CleaningUpdateView(UpdateView):
    model = Cleaning
    form_class = CleaningForm
    template_name = "cleaning/cleaning_form.html"
    success_url = reverse_lazy("cleaning:cleaning-list")


class CleaningDeleteView(DeleteView):
    model = Cleaning
    success_url = reverse_lazy("cleaning:cleaning-list")


class CleaningTypeListView(ListView):
    model = CleaningType
    template_name = "cleaning/cleaning_type_list.html"


class CleaningTypeDetailView(DetailView):
    model = CleaningType
    template_name = "cleaning/cleaning_type_detail.html"
    context_object_name = "cleaning_type"
