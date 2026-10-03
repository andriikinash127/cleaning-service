from django.contrib.auth import login
from django.contrib.auth.views import (
    LoginView,
    LogoutView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect
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
    Cleaner,
    Cleaning,
    CleaningType,
    UserRole,
)
from .forms import (
    PropertyForm,
    CleanerForm,
    CleaningForm,
    UserRegistrationForm,
    OwnerPropertyForm,

)


def home(request):
    return render(request, "home.html")


def filter_cleanings_for_user(queryset, user):
    if user.role == UserRole.OWNER:
        return queryset.filter(property__owner=user)
    if user.role == UserRole.CLEANER:
        return queryset.filter(cleaner=user.cleaner)
    return queryset


def filter_properties_for_user(queryset, user):
    if user.role == UserRole.OWNER:
        return queryset.filter(owner=user)
    return queryset


def is_manager(user):
    return user.role == UserRole.MANAGER


def can_manage_properties(user):
    return user.role in [UserRole.OWNER, UserRole.MANAGER]


class UserLoginView(LoginView):
    template_name = "registration/login.html"


class UserLogoutView(LogoutView):
    next_page = "/"


class RegisterView(TemplateView):
    template_name = "registration/register.html"


class OwnerRegisterView(TemplateView):
    template_name = "registration/owner_register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_form"] = UserRegistrationForm()
        context["property_form"] = OwnerPropertyForm()
        return context

    def post(self, request, *args, **kwargs):
        user_form = UserRegistrationForm(request.POST)
        property_form = OwnerPropertyForm(request.POST)

        if user_form.is_valid() and property_form.is_valid():
            user = user_form.save(commit=False)
            user.role = UserRole.OWNER
            user.save()

            property = property_form.save(commit=False)
            property.owner = user
            property.save()

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
        context["user_form"] = UserRegistrationForm()
        context["cleaner_form"] = CleanerForm()
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


class PropertyListView(LoginRequiredMixin, ListView):
    model = Property
    template_name = "cleaning/property_list.html"
    paginate_by = 10
    ordering = "id"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = filter_properties_for_user(
            queryset,
            self.request.user,
        )
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
        queryset = super().get_queryset()
        return filter_properties_for_user(
            queryset,
            self.request.user,
        )


class PropertyCreateView(LoginRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = "cleaning/property_form.html"
    success_url = reverse_lazy("cleaning:property-list")

    def dispatch(self, request, *args, **kwargs):
        if not can_manage_properties(request.user):
            return redirect("cleaning:property-list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class PropertyUpdateView(LoginRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = "cleaning/property_form.html"
    success_url = reverse_lazy("cleaning:property-list")

    def get_queryset(self):
        queryset = super().get_queryset()
        return filter_properties_for_user(
            queryset,
            self.request.user,
        )

    def dispatch(self, request, *args, **kwargs):
        if not can_manage_properties(request.user):
            return redirect("cleaning:property-list")
        return super().dispatch(request, *args, **kwargs)


class PropertyDeleteView(LoginRequiredMixin, DeleteView):
    model = Property
    success_url = reverse_lazy("cleaning:property-list")

    def get_queryset(self):
        queryset = super().get_queryset()
        return filter_properties_for_user(
            queryset,
            self.request.user,
        )

    def dispatch(self, request, *args, **kwargs):
        if not can_manage_properties(request.user):
            return redirect("cleaning:property-list")
        return super().dispatch(request, *args, **kwargs)


class CleanerListView(ListView):
    model = Cleaner
    template_name = "cleaning/cleaner_list.html"
    paginate_by = 5
    ordering = "id"

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search")
        cleaning_type = self.request.GET.get("cleaning_type")
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        if cleaning_type:
            queryset = queryset.filter(
                cleaning_types__name=cleaning_type
            )
        return queryset


class CleanerDetailView(DetailView):
    model = Cleaner
    template_name = "cleaning/cleaner_detail.html"


class CleanerUpdateView(LoginRequiredMixin, UpdateView):
    model = Cleaner
    form_class = CleanerForm
    template_name = "cleaning/cleaner_form.html"
    success_url = reverse_lazy("cleaning:cleaner-list")

    def dispatch(self, request, *args, **kwargs):
        if not is_manager(request.user):
            return redirect("cleaning:cleaner-list")
        return super().dispatch(request, *args, **kwargs)


class CleanerDeleteView(LoginRequiredMixin, DeleteView):
    model = Cleaner
    success_url = reverse_lazy("cleaning:cleaner-list")

    def dispatch(self, request, *args, **kwargs):
        if not is_manager(request.user):
            return redirect("cleaning:cleaner-list")
        return super().dispatch(request, *args, **kwargs)


class CleanerCreateView(LoginRequiredMixin, CreateView):
    model = Cleaner
    form_class = CleanerForm
    template_name = "cleaning/cleaner_form.html"
    success_url = reverse_lazy("cleaning:cleaner-list")

    def dispatch(self, request, *args, **kwargs):
        if not is_manager(request.user):
            return redirect("cleaning:cleaner-list")
        return super().dispatch(request, *args, **kwargs)


class CleaningListView(LoginRequiredMixin, ListView):
    model = Cleaning
    template_name = "cleaning/cleaning_list.html"
    paginate_by = 10
    ordering = "id"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = filter_cleanings_for_user(
            queryset,
            self.request.user,
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
        queryset = super().get_queryset()
        return filter_cleanings_for_user(
            queryset,
            self.request.user,
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
        queryset = super().get_queryset()
        return filter_cleanings_for_user(
            queryset,
            self.request.user,
        )


class CleaningDeleteView(LoginRequiredMixin, DeleteView):
    model = Cleaning
    success_url = reverse_lazy("cleaning:cleaning-list")

    def get_queryset(self):
        queryset = super().get_queryset()
        return filter_cleanings_for_user(
            queryset,
            self.request.user,
        )


class CleaningTypeListView(ListView):
    model = CleaningType
    template_name = "cleaning/cleaning_type_list.html"


class CleaningTypeDetailView(DetailView):
    model = CleaningType
    template_name = "cleaning/cleaning_type_detail.html"
    context_object_name = "cleaning_type"
