from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
import logging
from django.views import View
from .forms import DataCaptureForm  # Import your form
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView
#=from django.db.models import Count, DateFormat, F
from .models import ResidentialCapture
from datetime import datetime, timedelta
from django.db.models import Count,F
from django.db.models.functions import TruncDate  # Use TruncDate inst
#from .models import Region, DataModel  # Assuming your model names


from .forms import (
    DataCaptureForm, EducationForm, ResidentialCaptureForm,
    HealthCaptureForm, GovernmentCaptureForm, SMECaptureForm, SearchForm
)
from .models import (
    DataCapture, EducationCapture, ResidentialCapture,
    HealthCapture, GovernmentCapture, SMECapture, UserAssignment, Region, MMDA
)

logger = logging.getLogger(__name__)



def restricted_view(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to access this page.")
    
    user_assignment = UserAssignment.objects.filter(user=request.user).first()
    if not user_assignment or not user_assignment.region:
        return HttpResponseForbidden("You do not have an assigned region.")
    
    return render(request, "restricted_template.html", {"region": user_assignment.region})



'''class CreateGenericView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = None  # Should be overridden in a subclass
    form_class = DataCaptureForm
    template_name = "create_account.html"
    permission_required = "accounts.create_account"
    success_url = "success_page"  # Ensure this is set in subclasses

    def get_form(self, form_class=None):
        """Override get_form to pass user to the form for proper filtering."""
        form_class = form_class or self.get_form_class()
        return form_class(user=self.request.user)  # Pass user to form

    def form_valid(self, form):
        """Ensures region and MMDA are assigned correctly before saving."""
        user = self.request.user
        capture_instance = form.save(commit=False)

        if not user.is_superuser:
            try:
                user_assignment = UserAssignment.objects.get(user=user)
                capture_instance.region = user_assignment.region
                capture_instance.mmda = user_assignment.mmda
            except UserAssignment.DoesNotExist:
                messages.error(self.request, "You do not have an assigned region or MMDA. Contact admin.")
                return self.form_invalid(form)

        capture_instance.created_by = user
        capture_instance.save()
        messages.success(self.request, "Data successfully captured.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Pass additional context if needed."""
        context = super().get_context_data(**kwargs)
        if hasattr(self, "context_processor") and self.context_processor:
            context.update(self.context_processor(self.request))
        return context  '''





# Subclass the generic view to create a specific view
'''class CreateAccountView(CreateGenericView):
    form_class = DataCaptureForm
    template_name = 'create_account.html'
    success_url = 'your_success_url'
    #context_processor = your_context_processor'''



# Reusable function for listing accounts
def list_generic(request, model_class, template_name, context_name, paginate_by=25):
    if request.user.is_superuser:
        accounts = model_class.objects.all()
    else:
        try:
            user_assignment = UserAssignment.objects.get(user=request.user)
            accounts = model_class.objects.filter(region=user_assignment.region)
        except UserAssignment.DoesNotExist:
            messages.error(request, "You do not have an assigned region. Please contact your administrator.")
            accounts = []
    
    paginator = Paginator(accounts, paginate_by)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, template_name, {context_name: page_obj})



@login_required
def create_account(request):
    return create_generic(request, DataCaptureForm, 'create_account.html', 'account_list')



@login_required
def account_list(request):
    user = request.user
    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")

        # Filter accounts based on the user's assigned region
        accounts = DataCapture.objects.filter(region=user_assignment.region)
    else:
        accounts = DataCapture.objects.all()  # Superusers see all data

    return render(request, 'account_list.html', {'accounts': accounts})



def create_generic(request, form_class, template_name, success_url):
    """Handles form creation, ensuring the user's region and MMDA are set properly."""
    
    user = request.user  # Get the logged-in user

    # Initialize form variable
    form = None

    # Set default region and MMDA values based on user's assignment (if user is not a superuser)
    if user.is_superuser:
        default_region = None
        default_mmda = None
    else:
        try:
            assignment = user.assignment  # Fetch the related UserAssignment
            default_region = assignment.region
            default_mmda = assignment.mmda
        except UserAssignment.DoesNotExist:
            messages.error(request, "You have not been assigned a region or MMDA. Please update your profile.")
            return redirect('profile_update')  # Redirect users with no assignment
    
    if request.method == 'POST':
        form = form_class(request.POST, user=user)  # Pass user explicitly
        if form.is_valid():
            instance = form.save(commit=False)

            # If user is not a superuser, enforce region and MMDA restrictions
            if not user.is_superuser:
                try:
                    user_assignment = UserAssignment.objects.get(user=user)
                    instance.region = user_assignment.region
                    instance.mmda = user_assignment.mmda
                except UserAssignment.DoesNotExist:
                    messages.error(request, "You do not have a region or MMDA assigned. Contact admin.")
                    return render(request, template_name, {'form': form})

            instance.save()
            messages.success(request, "Record created successfully.")
            return redirect(success_url)

    else:
        ghana_card = request.GET.get('ghana_card', None)

        if ghana_card:
            data_capture = DataCapture.objects.filter(ghana_card=ghana_card).first()
            if data_capture:
                # Pre-fill form with existing Ghana Card details
                initial_data = {
                    'first_name': data_capture.first_name,
                    'surname': data_capture.surname,
                    'gender': data_capture.gender,
                    'date_of_birth': data_capture.date_of_birth,
                }
                form = form_class(initial=initial_data, user=user)
            else:
                form = form_class(user=user)  # Empty form if no data found
        else:
            form = form_class(user=user)  # Ensure user is passed on GET request

    return render(request, template_name, {'form': form})



def create_education(request):
    """Create an education record linked to the user's assigned region, MMDA, and optionally a Ghana Card."""
    
    user = request.user  # Get the logged-in user

    # Initialize form variable
    form = None

    # Set default region and MMDA values based on user's assignment (if user is not a superuser)
    if user.is_superuser:
        default_region = None
        default_mmda = None
    else:
        try:
            assignment = user.assignment  # Fetch the related UserAssignment
            default_region = assignment.region
            default_mmda = assignment.mmda
        except UserAssignment.DoesNotExist:
            messages.error(request, "You have not been assigned a region or MMDA. Please update your profile.")
            return redirect('profile_update')  # Redirect users with no assignment

    # Handle POST request to create the education record
    if request.method == 'POST':
        form = EducationForm(request.POST, user=user)
        if form.is_valid():
            education_instance = form.save(commit=False)
            # Assign the user's region and MMDA before saving
            education_instance.region = default_region
            education_instance.mmda = default_mmda
            education_instance.save()
            messages.success(request, "Education record created successfully.")
            return redirect('education_success')

        else:
            print(form.errors)  # Print form errors for debugging

    # Handle pre-filling the form with Ghana Card details
    ghana_card = request.GET.get('ghana_card', None)

    if ghana_card:
        data_capture = DataCapture.objects.filter(ghana_card=ghana_card).first()
        if data_capture:
            # Initialize form with data from DataCapture model
            initial_data = {
                'first_name': data_capture.first_name,
                'surname': data_capture.surname,
                'gender': data_capture.gender,
                'date_of_birth': data_capture.date_of_birth,
            }
            form = EducationForm(initial=initial_data, user=user)
        else:
            form = EducationForm()  # Empty form if no data found
    else:
        form = EducationForm(user=user)  # Ensure we have a form for GET requests

    return render(request, 'create_education.html', {'form': form})


# Account Update Views
class EducationUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'app.change_educationcapture'
    model = EducationCapture
    form_class = EducationForm
    template_name = 'create_education.html'
    success_url = reverse_lazy('education_list')

# User Registration
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Registration successful! Welcome!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# User Login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# User Logout
@login_required
def logout_view(request):
    if request.method == 'POST':
        auth_logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('login')



'''def personal_dashboard(request):
    context = {
        'user': request.user,
        # Add other variables here
    }
    return render(request, 'accounts/personal_dashboard.html', context)'''

'''def personal_dashboard(request):
    user = request.user
    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")
        accounts = DataCapture.objects.filter(region=user_assignment.region)
    else:
        accounts = DataCapture.objects.all()
    
    return render(request,'accounts/personal_dashboard.html', {'accounts': accounts})'''


from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from .models import DataCapture, UserAssignment

'''from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from .models import DataCapture, UserAssignment

@login_required
def personal_dashboard(request):
    user = request.user

    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")
        accounts = DataCapture.objects.filter(region=user_assignment.region)
    else:
        accounts = DataCapture.objects.all()

    total_entries = accounts.count()

    # Entries in the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_entries_count = accounts.filter(date_created__gte=seven_days_ago).count()


    # Unique category count (adjust 'category' field name if needed)
    category_count = accounts.values('category').distinct().count()

    return render(
        request,
        'accounts/personal_dashboard.html',
        {
            'accounts': accounts,
            'total_entries': total_entries,
            'recent_entries_count': recent_entries_count,
            'category_count': category_count,
        }
    )'''



from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.contrib.sessions.models import Session
from django.db.models import Count
import json
from datetime import timedelta

from .models import DataCapture, UserAssignment  # Adjust imports as necessary


@login_required
def personal_dashboard(request):
    user = request.user

    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")
        accounts = DataCapture.objects.filter(region=user_assignment.region)
    else:
        accounts = DataCapture.objects.all()

    total_entries = accounts.count()

    # Entries in the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_entries_count = accounts.filter(date_created__gte=seven_days_ago).count()

    # Unique category count
    category_count = accounts.values('category').distinct().count()

    # Data trend over the last 7 days
    today = timezone.now().date()
    trend_labels = []
    trend_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = accounts.filter(date_created__date=day).count()
        trend_labels.append(day.strftime('%a'))  # e.g., Mon, Tue
        trend_data.append(count)

    # Recent activity data
    recent_created = accounts.order_by('-date_created').first()
    recent_updated = accounts.order_by('-date_updated').first()
    recent_login = user.last_login
    recent_logout = Session.objects.filter(expire_date__lt=timezone.now()).order_by('-expire_date').first()

    return render(
        request,
        'accounts/personal_dashboard.html',
        {
            'accounts': accounts,
            'total_entries': total_entries,
            'recent_entries_count': recent_entries_count,
            'category_count': category_count,
            'trend_labels': json.dumps(trend_labels),
            'trend_data': json.dumps(trend_data),
            'recent_created': recent_created,
            'recent_updated': recent_updated,
            'recent_login': recent_login,
            'recent_logout': recent_logout,
        }
    )


@login_required
def residential_dashboard(request):
    user = request.user

    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")
        residentials = ResidentialCapture.objects.filter(region=user_assignment.region)
    else:
        residentials = ResidentialCapture.objects.all()

    total_entries = residentials.count()

    # Entries in the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_entries_count = residentials.filter(date_created__gte=seven_days_ago).count()

    # Unique category count
    category_count = residentials.values('category').distinct().count()

    # Data trend over the last 7 days
    today = timezone.now().date()
    trend_labels = []
    trend_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = residentials.filter(date_created__date=day).count()
        trend_labels.append(day.strftime('%a'))  # e.g., Mon, Tue
        trend_data.append(count)

    # Recent activity data
    recent_created = residentials.order_by('-date_created').first()
    recent_updated = residentials.order_by('-date_updated').first()
    recent_login = user.last_login
    recent_logout = Session.objects.filter(expire_date__lt=timezone.now()).order_by('-expire_date').first()

    return render(
        request,
        'accounts/residential_dashboard.html',
        {
            'residentials': residentials,
            'total_entries': total_entries,
            'recent_entries_count': recent_entries_count,
            'category_count': category_count,
            'trend_labels': json.dumps(trend_labels),
            'trend_data': json.dumps(trend_data),
            'recent_created': recent_created,
            'recent_updated': recent_updated,
            'recent_login': recent_login,
            'recent_logout': recent_logout,
        }
    )




def residential_analytics(request):
    # Total residential properties
    total_residential = ResidentialCapture.objects.count()
    
    # Registration trends (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    trend_data = (
        ResidentialCapture.objects
        .filter(date_created__gte=start_date)
        .annotate(date=TruncDate('date_created'))  # Using TruncDate
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    
    # Fill in missing dates
    date_dict = {}
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        date_dict[date_str] = 0
        current_date += timedelta(days=1)
    
    for entry in trend_data:
        date_dict[entry['date']] = entry['count']
    
    trend_labels = list(date_dict.keys())
    trend_values = list(date_dict.values())
    
    # Property type distribution
    property_distribution = (
        ResidentialCapture.objects
        .values(type=F('property_classification'))
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    
    property_labels = [d['type'] for d in property_distribution]
    property_data = [d['total'] for d in property_distribution]
    
    context = {
        'total_residential': total_residential,
        'trend_labels': trend_labels,
        'trend_data': trend_values,
        'property_labels': property_labels,
        'property_data': property_data,
    }
    
    return render(request, 'residential_analytical.html', context)

class AccountUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'app.change_accountcapture'
    model = DataCapture
    form_class = DataCaptureForm
    template_name = 'create_account.html'
    success_url = reverse_lazy('account_list')






@login_required
def education_list(request):
    return list_generic(request, EducationCapture, 'education_list.html', 'educations')


@login_required
def educational_dashboard(request):
    user = request.user

    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")
        educations= EducationCapture.objects.filter(region=user_assignment.region)
    else:
        educations= EducationCapture.objects.all()

    total_entries = educations.count()

    # Entries in the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_entries_count = educations.filter(date_created__gte=seven_days_ago).count()

    # Unique category count
    category_count = educations.values('category').distinct().count()

    # Data trend over the last 7 days
    today = timezone.now().date()
    trend_labels = []
    trend_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = educations.filter(date_created__date=day).count()
        trend_labels.append(day.strftime('%a'))  # e.g., Mon, Tue
        trend_data.append(count)

    # Recent activity data
    recent_created = educations.order_by('-date_created').first()
    recent_updated = educations.order_by('-date_updated').first()
    recent_login = user.last_login
    recent_logout = Session.objects.filter(expire_date__lt=timezone.now()).order_by('-expire_date').first()

    return render(
        request,
        'accounts/educational_dashboard.html',
        {
            'educations': educations,
            'total_entries': total_entries,
            'recent_entries_count': recent_entries_count,
            'category_count': category_count,
            'trend_labels': json.dumps(trend_labels),
            'trend_data': json.dumps(trend_data),
            'recent_created': recent_created,
            'recent_updated': recent_updated,
            'recent_login': recent_login,
            'recent_logout': recent_logout,
        }
    )


@login_required
def health_dashboard(request):
    user = request.user

    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")
        healths= HealthCapture.objects.filter(region=user_assignment.region)
    else:
        healths= HealthCapture.objects.all()

    total_entries = healths.count()

    # Entries in the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_entries_count = healths.filter(date_created__gte=seven_days_ago).count()

    # Unique category count
    category_count = healths.values('category').distinct().count()

    # Data trend over the last 7 days
    today = timezone.now().date()
    trend_labels = []
    trend_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = healths.filter(date_created__date=day).count()
        trend_labels.append(day.strftime('%a'))  # e.g., Mon, Tue
        trend_data.append(count)

    # Recent activity data
    recent_created = healths.order_by('-date_created').first()
    recent_updated = healths.order_by('-date_updated').first()
    recent_login = user.last_login
    recent_logout = Session.objects.filter(expire_date__lt=timezone.now()).order_by('-expire_date').first()

    return render(
        request,
        'accounts/health_dashboard.html',
        {
            'healths': healths,
            'total_entries': total_entries,
            'recent_entries_count': recent_entries_count,
            'category_count': category_count,
            'trend_labels': json.dumps(trend_labels),
            'trend_data': json.dumps(trend_data),
            'recent_created': recent_created,
            'recent_updated': recent_updated,
            'recent_login': recent_login,
            'recent_logout': recent_logout,
        }
    )





class EducationUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'app.change_educationcapture'
    model = EducationCapture
    form_class = EducationForm
    template_name = 'create_education.html'
    success_url = reverse_lazy('education_list')


@login_required
def education_detail(request, pk):
    education = get_object_or_404(EducationCapture, pk=pk)
    return render(request, 'education_detail.html', {'education': education})


class EducationDeleteView(PermissionRequiredMixin, DeleteView):
    model = EducationCapture  # Replace with the correct model if needed
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('education_list')  # Ensure 'account_list' exists in your URL patterns
    permission_required = 'app.delete_educationcapture'  # Update with the correct permission

    def get_queryset(self):
        if self.request.user.is_superuser:
            return EducationCapture.objects.all()
        else:
            return EducationCapture.objects.filter(region=self.request.user.userassignment.region)


def success_view(request):
    return render(request, 'success.html')







#RESIDENTIAL  accounts RECORDS
@login_required
def create_residential (request):
    return create_generic(request, ResidentialCaptureForm, 'create_residential.html', 'residential_list')


@login_required
def residential_list(request):
    return list_generic(request, ResidentialCapture, 'residential_list.html', 'residentials')

class ResidentialUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'app.change_residentialcapture'
    model = ResidentialCapture
    form_class = ResidentialCaptureForm
    template_name = 'create_residential.html'
    success_url = reverse_lazy('residential_list')


@login_required
def residential_detail(request, pk):
    residential = get_object_or_404(ResidentialCapture, pk=pk)
    return render(request, 'residential_detail.html', {'residential': residential})


class ResidentialDeleteView(PermissionRequiredMixin, DeleteView):
    model = ResidentialCapture  # Replace with the correct model if needed
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('residential_list')  # Ensure 'account_list' exists in your URL patterns
    permission_required = 'app.delete_residentialcapture'  # Update with the correct permission

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ResidentialCapture.objects.all()
        else:
            return ResidentialCapture.objects.filter(region=self.request.user.userassignment.region)




@login_required
def create_health(request):
    return create_generic(request, HealthCaptureForm, 'create_health.html', 'health_list')

@login_required
def health_list(request):
    return list_generic(request, HealthCapture, 'health_list.html', 'healths')


class HealthUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'app.change_healthcapture'
    model = HealthCapture
    form_class = HealthCaptureForm
    template_name = 'create_health.html'
    success_url = reverse_lazy('health_list')


@login_required
def health_detail(request, pk):
    health = get_object_or_404(HealthCapture, pk=pk)
    return render(request, 'health_detail.html', {'health': health})

class HealthDeleteView(PermissionRequiredMixin, DeleteView):
    model = HealthCapture  # Replace with the correct model if needed
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('health_list')  # Ensure 'account_list' exists in your URL patterns
    permission_required = 'app.delete_healthcapture'  # Update with the correct permission

    def get_queryset(self):
        if self.request.user.is_superuser:
            return HealthCapture.objects.all()
        else:
            return HealthCapture.objects.filter(region=self.request.user.userassignment.region)


def success_view(request):
    return render(request, 'success.html')


#Government accounts RECORDS

@login_required
def government_dashboard(request):
    user = request.user

    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")
        governments= GovernmentCapture.objects.filter(region=user_assignment.region)
    else:
        governments= GovernmentCapture.objects.all()

    total_entries = governments.count()

    # Entries in the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_entries_count = governments.filter(date_created__gte=seven_days_ago).count()

    # Unique category count
    category_count = governments.values('category').distinct().count()

    # Data trend over the last 7 days
    today = timezone.now().date()
    trend_labels = []
    trend_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = governments.filter(date_created__date=day).count()
        trend_labels.append(day.strftime('%a'))  # e.g., Mon, Tue
        trend_data.append(count)

    # Recent activity data
    recent_created = governments.order_by('-date_created').first()
    recent_updated = governments.order_by('-date_updated').first()
    recent_login = user.last_login
    recent_logout = Session.objects.filter(expire_date__lt=timezone.now()).order_by('-expire_date').first()

    return render(
        request,
        'accounts/government_dashboard.html',
        {
            'governments': governments,
            'total_entries': total_entries,
            'recent_entries_count': recent_entries_count,
            'category_count': category_count,
            'trend_labels': json.dumps(trend_labels),
            'trend_data': json.dumps(trend_data),
            'recent_created': recent_created,
            'recent_updated': recent_updated,
            'recent_login': recent_login,
            'recent_logout': recent_logout,
        }
    )


@login_required
def create_government(request):
    return create_generic(request, GovernmentCaptureForm, 'create_government.html', 'government_list')


@login_required
def government_list(request):
    return list_generic(request, GovernmentCapture, 'government_list.html', 'governments')



@login_required
def government_detail(request, pk):
    government = get_object_or_404(GovernmentCapture, pk=pk)
    return render(request, 'government_detail.html', {'government': government})



class GovernmentUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'app.change_governmentcapture'
    model = GovernmentCapture
    form_class = GovernmentCaptureForm
    template_name = 'create_government.html'
    success_url = reverse_lazy('government_list')


class GovernmentDeleteView(PermissionRequiredMixin, DeleteView):
    model = GovernmentCapture  # Replace with the correct model if needed
    template_name = 'account_confirm_delete.html'
    success_url = reverse_lazy('government_list')  # Ensure 'account_list' exists in your URL patterns
    permission_required = 'app.delete_governmentcapture'  # Update with the correct permission

    def get_queryset(self):
        if self.request.user.is_superuser:
            return GovernmentCapture.objects.all()
        else:
            return GovernmentCapture.objects.filter(region=self.request.user.userassignment.region)


def success_view(request):
    return render(request, 'success.html')




#SME accounts RECORDS
@login_required
def sme_dashboard(request):
    user = request.user

    if not user.is_superuser:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return HttpResponseForbidden("You do not have an assigned region.")
        smes= SMECapture.objects.filter(region=user_assignment.region)
    else:
        smes= SMECapture.objects.all()

    total_entries = smes.count()

    # Entries in the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_entries_count = smes.filter(date_created__gte=seven_days_ago).count()

    # Unique category count
    category_count = smes.values('category').distinct().count()

    # Data trend over the last 7 days
    today = timezone.now().date()
    trend_labels = []
    trend_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = smes.filter(date_created__date=day).count()
        trend_labels.append(day.strftime('%a'))  # e.g., Mon, Tue
        trend_data.append(count)

    # Recent activity data
    recent_created = smes.order_by('-date_created').first()
    recent_updated = smes.order_by('-date_updated').first()
    recent_login = user.last_login
    recent_logout = Session.objects.filter(expire_date__lt=timezone.now()).order_by('-expire_date').first()

    return render(
        request,
        'accounts/sme_dashboard.html',
        {
            'smes': smes,
            'total_entries': total_entries,
            'recent_entries_count': recent_entries_count,
            'category_count': category_count,
            'trend_labels': json.dumps(trend_labels),
            'trend_data': json.dumps(trend_data),
            'recent_created': recent_created,
            'recent_updated': recent_updated,
            'recent_login': recent_login,
            'recent_logout': recent_logout,
        }
    )





@login_required
def create_sme(request):
    return create_generic(request, SMECaptureForm, 'create_sme.html', 'sme_list')

@login_required
def sme_list(request):
    return list_generic(request, SMECapture, 'sme_list.html', 'smes')

class SMEUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'app.change_smecapture'
    model = SMECapture
    form_class = SMECaptureForm
    template_name = 'create_sme.html'
    success_url = reverse_lazy('sme_list')

@login_required
def sme_detail(request, pk):
    sme = get_object_or_404(SMECapture, pk=pk)
    return render(request, 'sme_detail.html', {'sme': sme})


class SMEDeleteView(PermissionRequiredMixin, DeleteView):
    model = SMECapture  # Replace with the correct model if needed
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('smes_list')  # Ensure 'account_list' exists in your URL patterns
    permission_required = 'app.delete_smecapture'  # Update with the correct permission

    def get_queryset(self):
        if self.request.user.is_superuser:
            return SMECapture.objects.all()
        else:
            return SMECapture.objects.filter(region=self.request.user.userassignment.region)


def success_view(request):
    return render(request, 'success.html')




@login_required
def account_detail(request, pk):
    account = get_object_or_404(DataCapture, pk=pk)
    return render(request, 'account_detail.html', {'account': account})




class AccountDeleteView(PermissionRequiredMixin, DeleteView):
    model = DataCapture  # Replace with the correct model if needed
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('account_list')  # Ensure 'account_list' exists in your URL patterns
    permission_required = 'app.delete_datacapture'  # Update with the correct permission

    def get_queryset(self):
        if self.request.user.is_superuser:
            return DataCapture.objects.all()
        else:
            return DataCapture.objects.filter(region=self.request.user.userassignment.region)




@login_required
def search_view(request):
    form = SearchForm(request.GET or None)
    account_results = []
    education_results = []

    if form.is_valid():
        query = form.cleaned_data.get('query', '')

        if query:
            # Search in DataCapture
            account_results = DataCapture.objects.filter(
                first_name__icontains=query
            ) | DataCapture.objects.filter(
                surname__icontains=query
            ) | DataCapture.objects.filter(
                serial_number__icontains=query
            )

            # Search in EducationCapture
            education_results = EducationCapture.objects.filter(
                first_name__icontains=query
            ) | EducationCapture.objects.filter(
                surname__icontains=query
            ) | EducationCapture.objects.filter(
                school_name__icontains=query
            ) | EducationCapture.objects.filter(
                serial_number__icontains=query
            )

    context = {
        'form': form,
        'account_results': account_results,
        'education_results': education_results,
    }
    return render(request, 'search.html', context)



# Home Page
@login_required
def home(request):
    context = {
        'title': 'Home',
        'message': 'Welcome to the MMDA Education Portal!',
    }
    return render(request, 'home.html', context)


# About Page
def about(request):
    return render(request, 'about.html')


# Contact Page
def contact_view(request):
    if request.method == 'POST':
        message_name = request.POST.get('message-name')
        message_email = request.POST.get('message-email')
        message = request.POST.get('message')

        # Simulate email sending (replace with actual email logic)
        try:
            # Replace this with actual send_mail logic
            print(f"Email sent: {message_name}, {message_email}, {message}")
            return JsonResponse({'success': True})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'contact.html')


# Contact Success Page
def contact_success(request):
    return render(request, 'contact_success.html', {'message': 'Your message has been sent successfully!'})


# Access Denied Page
def access_denied(request):
    return render(request, 'accounts/access_denied.html', {
        "message": "You do not have permission to access this resource. Please contact your administrator."
    })


def fetch_ghana_card(request):
    """Fetch data associated with the Ghana Card number."""
    ghana_card = request.GET.get('ghana_card', None)
    if not ghana_card:
        return JsonResponse({'error': 'Ghana Card number not provided'}, status=400)

    data_capture = DataCapture.objects.filter(ghana_card=ghana_card).first()

    if data_capture:
        # Return the data associated with the Ghana Card number
        data = {
            'first_name': data_capture.first_name,
            'surname': data_capture.surname,
            'gender': data_capture.gender,
            'date_of_birth': data_capture.date_of_birth,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Ghana Card not found'}, status=404)

'''from django.shortcuts import render, redirect
from django.contrib import messages
from .models import EducationCapture, UserAssignment, DataCapture
from .forms import EducationForm'''



'''def create_education(request):
    """Create an education record linked to the user's assigned region, MMDA, and optionally a Ghana Card."""
    
    user = request.user  # Get the logged-in user

    # If the user is a superuser, skip the assignment check
    if user.is_superuser:
        # Superusers can bypass the region and MMDA check
        default_region = None
        default_mmda = None
    else:
        # For non-superusers, fetch the related UserAssignment
        try:
            assignment = user.assignment  # Fetch the related UserAssignment
            default_region = assignment.region
            default_mmda = assignment.mmda
        except UserAssignment.DoesNotExist:
            messages.error(request, "You have not been assigned a region or MMDA. Please update your profile.")
            return redirect('profile_update')  # Redirect users with no assignment


    form = None  # Initialize form variable

    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education_instance = form.save(commit=False)
            # Assign the user's region and MMDA before saving
            education_instance.region = default_region
            education_instance.mmda = default_mmda
            education_instance.save()
            messages.success(request, "Education record created successfully.")
            return redirect('education_success')

        else:
            print(form.errors)  # Print form errors for debugging

    # Handle pre-filling the form with Ghana Card details
    ghana_card = request.GET.get('ghana_card', None)

    if ghana_card:
        data_capture = DataCapture.objects.filter(ghana_card=ghana_card).first()
        if data_capture:
            # Initialize form with data from DataCapture model
            initial_data = {
                'first_name': data_capture.first_name,
                'surname': data_capture.surname,
                'gender': data_capture.gender,
                'date_of_birth': data_capture.date_of_birth,
            }
            form = EducationForm(initial=initial_data)
        else:
            form = EducationForm()  # Empty form if no data found
    else:
        form = EducationForm()  # Ensure we have a form for GET requests

    return render(request, 'create_education.html', {'form': form})


    def save(self, *args, **kwargs):
        print("Saving EducationCapture instance...")
        if not self.serial_number:
            self.serial_number = self.generate_serial_number()
        super().save(*args, **kwargs)'''


    # This line is unreachable because it is after the return statement
    # if not form.is_valid():
    #     print(form.errors)  # Print form errors in the console







def enter_ghana_card(request):
    """Render the page for entering the Ghana Card number."""
    return render(request, 'enter_ghana_card.html')

def success_view(request):
    return render(request, 'success.html')  # Render a success page or template


def paynow(request):
    """Render the page for entering the Ghana Card number."""
    return render(request, 'paynow.html')