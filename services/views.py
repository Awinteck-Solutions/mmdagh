from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.http import HttpResponse
from django.contrib import messages
from .models import GhanaPoliceService, GhanaFireStation, FireStation, firehydrant, Region,ghmedicalfacility

from django.db.models import Count
from django.core.paginator import Paginator
from django.utils.timezone import now
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import csv

from .models import PoliceStation  # Correct import in other files

# Create your views here.
# ============================
# Ghana Police Service Views
# ============================

from django.shortcuts import render

def police_dashboard(request):
    # You can add context data here if needed
    context = {
        'page_title': 'Police Command Dashboard',
        'active_officers': 24,
        'pending_signals': 15,
        'new_messages': 8
    }
    return render(request, 'police_dashboard.html', context)


def prisonsservice_dashboard(request):
    context = {
        'total_inmates': 15432,
        'facility_capacity': 82,
        'staff_count': 4785,
        'recent_incidents': 3
    }
    return render(request, 'prisonsservice_dashboard.html', context)

def ghmedical_dashboard(request):
    context = {
        'current_patients': 142,
        'available_beds': 28,
        'pending_appointments': 89,
        'critical_cases': 9
    }
    return render(request, 'ghmedical_dashboard.html', context)


def fireservice_dashboard(request):
    context = {
        'active_incidents': 8,
        'recent_rescues': 14,
        'available_units': 22,
        'avg_response': 9.5
    }
    return render(request, 'fireservice_dashboard.html', context)

def educationservice_dashboard(request):
    context = {
        'school_count': 24356,
        'student_count': 6231459,
        'teacher_count': 289345,
        'pending_applications': 1567
    }
    return render(request, 'educationservice_dashboard.html', context)

class GhanaPoliceServiceListView(ListView):
    model = GhanaPoliceService
    template_name = 'ghpolice_list.html'
    context_object_name = 'stations'

    def get_queryset(self):
        queryset = GhanaPoliceService.objects.all()
        query = self.request.GET.get('q')  # Get search query from URL
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset

class GhanaPoliceServiceDetailView(DetailView):
    model = GhanaPoliceService
    template_name = 'ghpolice_details.html'
    context_object_name = 'station'

def ghpolice_reports(request):
    stations = GhanaPoliceService.objects.all()
    return render(request, 'ghpolice_reports.html', {'stations': stations})


# ============================
# Ghana Fire Service Views
# ============================

class GhanaFireStationListView(ListView):
    model = GhanaFireStation
    template_name = 'ghfireservice_list.html'
    context_object_name = 'fire_stations'

    def get_queryset(self):
        queryset = GhanaFireStation.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset

class GhanaFireStationDetailView(DetailView):
    model = FireStation
    template_name = 'ghfireservice_details.html'
    context_object_name = 'fire_stations'

def GhanaFireStation_reports(request):
    stations = FireStation.objects.all()
    return render(request, 'ghfireservice_reports.html', {'fire_station': stations})


# ============================
# Fire Hydrant Views
# ============================

class FirehydrantListView(ListView):
    model = firehydrant
    template_name = 'firehydrant_list.html'
    context_object_name = 'firehydrants'

    def get_queryset(self):
        queryset = firehydrant.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset

class FirehydrantDetailView(DetailView):
    model = firehydrant
    template_name = 'firehydrant_details.html'
    context_object_name = 'firehydrants'


# Commented placeholder retained as requested
'''
def Firehydrant_reports(request):
    firehydrant = firehydrant.objects.all()
    return render(request, 'firehydrant_reports.html', {'firehydrants': firehydrants})
'''

# ============================
# Fire Hydrant Views
# ============================

class FirehydrantListView(ListView):
    model = firehydrant
    template_name = 'firehydrant_list.html'
    context_object_name = 'firehydrants'

    def get_queryset(self):
        queryset = firehydrant.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset

class FirehydrantDetailView(DetailView):
    model = firehydrant
    template_name = 'firehydrant_details.html'
    context_object_name = 'firehydrants'


def Firehydrant_reports(request):
    """
    View to display fire hydrant reports with filters, charts, pagination, and export.
    """
    # Step 1: Get filters
    condition = request.GET.get('condition')
    accessibility = request.GET.get('accessibility')
    region_id = request.GET.get('region')

    # Step 2: Query and filter hydrants
    hydrants = firehydrant.objects.all().select_related('region')
    if condition:
        hydrants = hydrants.filter(nature_of_firehydrant=condition)
    if accessibility:
        hydrants = hydrants.filter(Accessibility_of_hydrant=accessibility)
    if region_id:
        hydrants = hydrants.filter(region_id=region_id)

    # Step 3: Data aggregation
    total_count = hydrants.count()
    good_condition_count = hydrants.filter(nature_of_firehydrant='Good').count()
    moderate_condition_count = hydrants.filter(nature_of_firehydrant='Moderate').count()
    bad_condition_count = hydrants.filter(nature_of_firehydrant='Bad').count()

    easy_access_count = hydrants.filter(Accessibility_of_hydrant='Easy').count()
    difficult_access_count = hydrants.filter(Accessibility_of_hydrant='Difficult').count()
    encouraged_access_count = hydrants.filter(Accessibility_of_hydrant='Encouraged').count()

    def get_percentage(part, total):
        return round((part / total) * 100, 1) if total > 0 else 0

    # Step 4: Export data
    export_format = request.GET.get('export')
    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="firehydrants.csv"'
        writer = csv.writer(response)
        writer.writerow(['Hydrant Name', 'Area', 'Region', 'Condition', 'Accessibility', 'Last Updated'])
        for hydrant in hydrants:
            writer.writerow([
                hydrant.firehydrant_name,
                hydrant.area_name,
                hydrant.region.name if hydrant.region else '',
                hydrant.nature_of_firehydrant,
                hydrant.Accessibility_of_hydrant,
                hydrant.date_updated.strftime('%Y-%m-%d'),
            ])
        return response

    elif export_format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="firehydrants.pdf"'
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter
        y = height - 50
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "Fire Hydrant Report")
        y -= 30
        p.setFont("Helvetica", 10)
        p.drawString(50, y, "Generated on: " + now().strftime('%Y-%m-%d %H:%M'))
        y -= 30
        p.setFont("Helvetica-Bold", 9)
        p.drawString(50, y, "Name")
        p.drawString(150, y, "Area")
        p.drawString(250, y, "Region")
        p.drawString(350, y, "Condition")
        p.drawString(450, y, "Accessibility")
        y -= 15
        p.setFont("Helvetica", 9)
        for hydrant in hydrants:
            if y < 50:
                p.showPage()
                y = height - 50
            p.drawString(50, y, hydrant.firehydrant_name or '')
            p.drawString(150, y, hydrant.area_name or '')
            p.drawString(250, y, hydrant.region.name if hydrant.region else '')
            p.drawString(350, y, hydrant.nature_of_firehydrant or '')
            p.drawString(450, y, hydrant.Accessibility_of_hydrant or '')
            y -= 15
        p.showPage()
        p.save()
        return response

    # Step 5: Pagination
    paginator = Paginator(hydrants, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'firehydrants': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'paginator': paginator,

        'total_count': total_count,
        'good_condition_count': good_condition_count,
        'moderate_condition_count': moderate_condition_count,
        'bad_condition_count': bad_condition_count,

        'good_condition_percentage': get_percentage(good_condition_count, total_count),
        'moderate_condition_percentage': get_percentage(moderate_condition_count, total_count),
        'bad_condition_percentage': get_percentage(bad_condition_count, total_count),

        'easy_access_count': easy_access_count,
        'difficult_access_count': difficult_access_count,
        'encouraged_access_count': encouraged_access_count,

        'regions': Region.objects.all(),
        'current_date': now(),
    }

    return render(request, 'firehydrant_reports.html', context)



# Ghana Police Service Views
# ============================

from django.views.generic import ListView, DetailView
from django.shortcuts import render
from .models import ghmedicalfacility

class ghmedicalfacilityListView(ListView):
    model = ghmedicalfacility
    template_name = 'ghmedical_list.html'
    context_object_name = 'facilitys'  # Correct variable name

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(facility_name__name__icontains=query)
        return queryset

class ghmedicalfacilityDetailView(DetailView):
    model = ghmedicalfacility
    template_name = 'ghmedical_details.html'
    context_object_name = 'facility'

'''def ghmedicalfacility_reports(request):
    facilities = ghmedicalfacility.objects.all()
    return render(request, 'ghmedical_reports.html', {
        'facilitys': facilities
    })'''




def ghmedicalfacility_reports(request):
    """
    View to display fire hydrant reports with filters, charts, pagination, and export.
    """
    # Step 1: Get filters
    condition = request.GET.get('condition')
    accessibility = request.GET.get('accessibility')
    facilitytype = request.GET.get('facilitytype')
    region_id = request.GET.get('region')

    # Step 2: Query and filter hydrants
    facilities = ghmedicalfacility.objects.all().select_related('region')
    if condition:
        facilities = facilities.filter(nature_of_building=condition)
    if accessibility:
        facilities = facilities.filter(Accessibility_of_facility=accessibility)
    if facilitytype:
        facilities = facilities.filter(type_facility=facilitytype)

    if region_id:
        facilities = facilities.filter(region_id=region_id)

    # Step 3: Data aggregation
    total_count = facilities.count()
    good_condition_count = facilities.filter(nature_of_building='Good').count()
    moderate_condition_count = facilities.filter(nature_of_building='Moderate').count()
    bad_condition_count = facilities.filter(nature_of_building='Bad').count()

    easy_access_count = facilities.filter(Accessibility_of_facility='Easy').count()
    difficult_access_count = facilities.filter(Accessibility_of_facility='Difficult').count()
    encouraged_access_count = facilities.filter(Accessibility_of_facility='Encouraged').count()

    chip_compound_count= facilities.filter(type_facility='Chip Compound').count()
    clinic_count= facilities.filter(type_facility='Clinic').count()
    hospital_count= facilities.filter(type_facility='Hospital').count()
    maternity_home_count= facilities.filter(type_facility='Maternity Home').count()
    pharmacy_count= facilities.filter(type_facility='Pharmacy').count()
    other_count= facilities.filter(type_facility='other').count()


    def get_percentage(part, total):
        return round((part / total) * 100, 1) if total > 0 else 0

    # Step 4: Export data
    export_format = request.GET.get('export')
    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ghmedicalfaciltys.csv"'
        writer = csv.writer(response)
        writer.writerow(['Facility Name', 'Area', 'Region', 'Facility Type','Condition', 'Accessibility', 'Last Updated'])
        for facility in facilities:
            writer.writerow([
                facility.facility_name,
                facility.area_name,
                facility.region.name if facility.region else '',
                facility.type_facility,
                facility.nature_of_building,
                facility.Accessibility_of_facility,
                facility.date_updated.strftime('%Y-%m-%d'),
            ])
        return response

    elif export_format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="ghmedicalfaciltys.pdf"'
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter
        y = height - 50
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "Gh Medical facilities Report")
        y -= 30
        p.setFont("Helvetica", 10)
        p.drawString(50, y, "Generated on: " + now().strftime('%Y-%m-%d %H:%M'))
        y -= 30
        p.setFont("Helvetica-Bold", 9)
        p.drawString(50, y, "Name")
        p.drawString(150, y, "Area")
        p.drawString(250, y, "Region")
        p.drawString(350, y, "Condition")
        p.drawString(450, y, "Accessibility")
        p.drawString(500, y, "Facility Type")
        y -= 15
        p.setFont("Helvetica", 9)
        for facility in facilities:
            if y < 50:
                p.showPage()
                y = height - 50
            p.drawString(50, y, facility.facility_name or '')
            p.drawString(150, y, facility.area_name or '')
            p.drawString(250, y, facility.region.name if facility.region else '')
            p.drawString(350, y, facility.nature_of_building or '')
            p.drawString(450, y, facility.Accessibility_of_facility or '')
            p.drawString(450, y, facility.type_facility or '')
            y -= 15
        p.showPage()
        p.save()
        return response

    # Step 5: Pagination
    paginator = Paginator(facilities, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'facilities': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'paginator': paginator,

        'total_count': total_count,
        'good_condition_count': good_condition_count,
        'moderate_condition_count': moderate_condition_count,
        'bad_condition_count': bad_condition_count,

        'good_condition_percentage': get_percentage(good_condition_count, total_count),
        'moderate_condition_percentage': get_percentage(moderate_condition_count, total_count),
        'bad_condition_percentage': get_percentage(bad_condition_count, total_count),

        'easy_access_count': easy_access_count,
        'difficult_access_count': difficult_access_count,
        'encouraged_access_count': encouraged_access_count,

        'chip_compound_count': chip_compound_count,
        'clinic_count': clinic_count,
        'hospital_count': hospital_count,
        'maternity_home_count': maternity_home_count,
        'pharmacy_count': pharmacy_count,
        'other_count': other_count,



        'regions': Region.objects.all(),
        'current_date': now(),
    }

    return render(request, 'ghmedical_reports.html', context)



# views.py
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
# services/views.py
from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import SignalMessage, DeliveryReport  # <- Add this import
from .forms import SignalMessageForm  # Ensure you have this form created


'''class SignalCreateView(CreateView):
    model = SignalMessage
    fields = ['service', 'regions', 'divisions', 'districts', 'stations', 
             'subject', 'content', 'priority']
    #template_name = 'signals/signal_create.html'
    template_name = 'services/signal_create.html'

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.status = 'SENT'
        response = super().form_valid(form)
        # Add real-time notification logic here
        return response'''


# services/views.py
class SignalCreateView(CreateView):
    model = SignalMessage
    form_class = SignalMessageForm
    template_name = 'signal/signal_create.html'
    success_url = reverse_lazy('signal-outbox')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['police_regions'] = PoliceRegion.objects.all()
        return context

def form_valid(self, form):
    form.instance.sender = self.request.user
    form.instance.status = 'SENT'
    
    # Get cleaned data
    station = form.cleaned_data.get('station')
    district = form.cleaned_data.get('district')
    division = form.cleaned_data.get('division')
    police_region = form.cleaned_data.get('police_region')  # Directly from form

    # Cascade from lowest to highest level
    if station:
        form.instance.district = station.district
        form.instance.division = station.district.division
        form.instance.police_region = station.district.division.police_region
    elif district:
        form.instance.division = district.division
        form.instance.police_region = district.division.police_region
    elif division:
        form.instance.police_region = division.police_region
    else:
        # Explicitly set police_region from form input
        form.instance.police_region = police_region  # Key fix
    
    return super().form_valid(form)




class InboxView(ListView):
    model = DeliveryReport
    template_name = 'signal/inbox.html'

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'police_unit') and user.police_unit:
            return super().get_queryset().filter(
                recipient_unit=user.police_unit
            )
        else:
            return DeliveryReport.objects.none()  # Or filter by a default/fallback logic




class OutboxView(ListView):
    model = SignalMessage
    template_name = 'signal/outbox.html'
    
    # Remove filter for debugging
    def get_queryset(self):
        return super().get_queryset().all()

# views.py
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from .models import SignalMessage, DeliveryReport

class DeliveryReportView(DetailView):
    model = SignalMessage
    template_name = 'services/delivery_reports.html'
    context_object_name = 'message'
    pk_url_kwarg = 'message_id'  # Matches the URL parameter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get paginated delivery reports
        reports = self.object.reports.all().select_related('recipient_unit')
        paginator = Paginator(reports, 25)  # Show 25 reports per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context.update({
            'page_obj': page_obj,
            'total_reports': reports.count(),
            'delivered_count': reports.filter(received_at__isnull=False).count(),
            'read_count': reports.filter(read_at__isnull=False).count()
        })
        return context

    def get_queryset(self):
        return super().get_queryset().prefetch_related('reports')



from django.shortcuts import render
from .models import PoliceRegion, Division, District


# services/views.py
from django.http import JsonResponse

def load_divisions(request):
    region_id = request.GET.get('region_id')
    if not region_id:
        return JsonResponse({'error': 'Missing region_id parameter'}, status=400)
    
    try:
        divisions = Division.objects.filter(police_region_id=region_id)
        return render(request, 'division_dropdown.html', {'divisions': divisions})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def load_districts(request):
    division_id = request.GET.get('division_id')
    if not division_id:
        return JsonResponse({'error': 'Missing division_id parameter'}, status=400)
    
    try:
        districts = District.objects.filter(division_id=division_id)
        return render(request, 'services/district_dropdown.html', {'districts': districts})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def load_policestations(request):
    try:
        district_id = request.GET['district_id']
        stations = PoliceStation.objects.filter(district_id=district_id)
        return render(request, 'services/station_dropdown.html', {'stations': stations})
    except KeyError:
        return JsonResponse({'error': 'Missing district_id parameter'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Invalid district_id format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



# services/views.py
import logging
logger = logging.getLogger(__name__)

def load_divisions(request):
    region_id = request.GET.get('region_id')
    logger.debug(f"Loading divisions for region_id: {region_id}")
    
    try:
        divisions = Division.objects.filter(police_region_id=region_id)
        logger.debug(f"Found {divisions.count()} divisions")
        return render(request, 'services/division_dropdown.html', {'divisions': divisions})
    except Exception as e:
        logger.error(f"Error loading divisions: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)