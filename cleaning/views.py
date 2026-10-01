from django.shortcuts import render
from django.views.generic import DetailView, ListView
from .models import Property

def home(request):
    return render(request, "home.html")


class PropertyListView(ListView):
    model = Property
    template_name = "cleaning/property_list.html"

class PropertyDetailView(DetailView):
    model = Property
    template_name = "cleaning/property_detail.html"



