from django.contrib import admin, messages
from django.shortcuts import redirect, render
import csv
from io import TextIOWrapper
from django.urls import path
from .models import (
    Region, Division, District, PoliceStation, Service, GhanaPoliceService,
    GhanaFireStation, FireStation, firehydrant, ghmedicalfacility, PoliceRegion, POLICE_REGIONS
)
from .models import SignalMessage, DeliveryReport

# CSV Import Admin
class CSVImportAdmin(admin.ModelAdmin):
    change_list_template = "admin/csv_import.html"  # Attach CSV template

    def import_csv(self, request):
        if request.method == "POST" and 'csv_file' in request.FILES:
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
            reader = csv.reader(csv_file)
            for row in reader:
                region, _ = Region.objects.get_or_create(name=row[0], code=row[1])
                police_region, _ = PoliceRegion.objects.get_or_create(region=region, name=row[2], code=row[3])
                division, _ = Division.objects.get_or_create(police_region=police_region, name=row[4], code=row[5])
                district, _ = District.objects.get_or_create(division=division, name=row[6], code=row[7])
                PoliceStation.objects.get_or_create(district=district, name=row[8], code=row[9])
            
            messages.success(request, "CSV file imported successfully")
            return redirect("..")
        return render(request, "admin/csv_import.html", {"title": "CSV Import"})

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv), name='import_csv')
        ]
        return custom_urls + urls


# Register Models with CSV Import Admin
@admin.register(Division)
class DivisionAdmin(CSVImportAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    list_filter = ("name", "code")

@admin.register(District)
class DistrictAdmin(CSVImportAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    list_filter = ("name", "code")

@admin.register(PoliceStation)
class PoliceStationAdmin(CSVImportAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    list_filter = ("name", "code")

@admin.register(FireStation)
class FireStationAdmin(CSVImportAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    list_filter = ("name", "code")

# Standard Model Registrations
admin.site.register(Service)
admin.site.register(GhanaPoliceService)
admin.site.register(GhanaFireStation)
admin.site.register(firehydrant)
admin.site.register(ghmedicalfacility)


# Police Region Admin
@admin.register(PoliceRegion)
class PoliceRegionAdmin(admin.ModelAdmin):
    list_display = ("formatted_display", "code", "region")  # Shows formatted name in list

    def formatted_display(self, obj):
        police_regions_dict = dict(POLICE_REGIONS)  # Convert tuple list to dictionary
        return f"{obj.code} - {police_regions_dict.get(obj.code, obj.name)}"

    formatted_display.short_description = "Police Region"  # Column header



# admin.py
from django.contrib import admin


class DeliveryReportInline(admin.TabularInline):
    model = DeliveryReport
    extra = 0
    readonly_fields = ('received_at', 'read_at')
    can_delete = False

'''@admin.register(SignalMessage)
class SignalMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'priority', 'status', 'created_at')
    list_filter = ('priority', 'status', 'service', 'regions')
    search_fields = ('subject', 'content', 'sender__username')
    filter_horizontal = ('regions', 'divisions', 'districts', 'stations')
    inlines = [DeliveryReportInline]
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Metadata', {
            'fields': ('sender', 'service', 'status', 'priority')
        }),
        ('Recipients', {
            'fields': ('regions', 'divisions', 'districts', 'stations')
        }),
        ('Content', {
            'fields': ('subject', 'content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.sender:
            obj.sender = request.user
        super().save_model(request, obj, form, change)'''


# services/admin.py
@admin.register(SignalMessage)
class SignalMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'priority', 'status', 'created_at')
    search_fields = ('subject', 'content', 'sender__username')
    inlines = [DeliveryReportInline]
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('police_region', 'division', 'district', 'station')  # Updated field names

    fieldsets = (
        ('Metadata', {
            'fields': ('sender', 'service', 'status', 'priority')
        }),
        ('Recipients', {
            'fields': ('police_region', 'division', 'district', 'station')  # Updated here
        }),
        ('Content', {
            'fields': ('subject', 'content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.sender:
            obj.sender = request.user
        super().save_model(request, obj, form, change)


@admin.register(DeliveryReport)
class DeliveryReportAdmin(admin.ModelAdmin):
    list_display = ('message', 'recipient_unit', 'received_at', 'read_at')
    list_filter = ('recipient_unit', 'received_at')
    search_fields = ('message__subject', 'recipient_unit__name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('message', 'recipient_unit')