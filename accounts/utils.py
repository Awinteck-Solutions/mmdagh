from django.db.models import Q
from .utils import filter_by_user_assignment, get_dashboard_data
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from .models import DataCapture
from .forms import DataCaptureForm
from .views import BaseCRUDView
from django.views.decorators.cache import cache_page
from django.http import HttpResponseForbidden

def filter_by_user_assignment(user, model):
    if user.is_superuser:
        return model.objects.all()
    user_assignment = UserAssignment.objects.filter(user=user).first()
    if not user_assignment:
        return model.objects.none()
    return model.objects.filter(region=user_assignment.region)

def get_dashboard_data(user, model):
    if user.is_superuser:
        queryset = model.objects.all()
    else:
        user_assignment = UserAssignment.objects.filter(user=user).first()
        if not user_assignment:
            return None
        queryset = model.objects.filter(region=user_assignment.region)

    total_entries = queryset.count()
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_entries_count = queryset.filter(date_created__gte=seven_days_ago).count()
    category_count = queryset.values('category').distinct().count()

    # Data trend over the last 7 days
    today = timezone.now().date()
    trend_labels = []
    trend_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = queryset.filter(date_created__date=day).count()
        trend_labels.append(day.strftime('%a'))
        trend_data.append(count)

    return {
        'total_entries': total_entries,
        'recent_entries_count': recent_entries_count,
        'category_count': category_count,
        'trend_labels': trend_labels,
        'trend_data': trend_data,
    }

@login_required
def account_list(request):
    accounts = filter_by_user_assignment(request.user, DataCapture)
    return render(request, 'account_list.html', {'accounts': accounts})

@login_required
@cache_page(60 * 15)
def personal_dashboard(request):
    data = get_dashboard_data(request.user, DataCapture)
    if data is None:
        return HttpResponseForbidden("You do not have an assigned region.")
    return render(request, 'accounts/personal_dashboard.html', data)

class CreateAccountView(BaseCRUDView, CreateView):
    model = DataCapture
    form_class = DataCaptureForm
    template_name = 'create_account.html'
    success_url = reverse_lazy('account_list')
    permission_required = 'app.add_datacapture'

class UpdateAccountView(BaseCRUDView, UpdateView):
    model = DataCapture
    form_class = DataCaptureForm
    template_name = 'create_account.html'
    success_url = reverse_lazy('account_list')
    permission_required = 'app.change_datacapture'