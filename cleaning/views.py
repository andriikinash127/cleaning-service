from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (DetailView,
                                  ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from .models import (Property,
                     Cleaner,
                     )
from .forms import PropertyForm, CleanerForm


def home(request):
    return render(request, "home.html")


class PropertyListView(ListView):
    model = Property
    template_name = "cleaning/property_list.html"

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
