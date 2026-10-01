from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (DetailView,
                                  ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from .models import Property
from .forms import PropertyForm

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
