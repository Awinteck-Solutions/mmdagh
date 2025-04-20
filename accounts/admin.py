from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Region, MMDA, UserAssignment,
    DataCapture, EducationCapture, ResidentialCapture,
    HealthCapture, GovernmentCapture
)

# Region Admin
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    list_select_related = True

# MMDA Admin
@admin.register(MMDA)
class MMDAAdmin(admin.ModelAdmin):
    list_display = ("name", "region")
    search_fields = ("name", "region__name")
    list_filter = ("region",)
    list_select_related = ("region",)

# User Assignment Admin
@admin.register(UserAssignment)
class UserAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "region", "mmda")
    search_fields = ("user__username", "region__name", "mmda__name")
    list_filter = ("region", "mmda")
    list_select_related = ("user", "region", "mmda")

# Data Capture Admin
@admin.register(DataCapture)
class DataCaptureAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ('serial_number', 'first_name', 'surname', 'category', 
                   'contact_1', 'network_connectivity', 'date_created')
    list_filter = ('category', 'date_created')
    search_fields = ('first_name', 'surname', 'serial_number')
    list_select_related = True
    #raw_id_fields = ('profile_picture',)
    date_hierarchy = 'date_created'

# Education Capture Form
class EducationCaptureForm(forms.ModelForm):
    class Meta:
        model = EducationCapture
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('electricity_connection') and not cleaned_data.get('ecg_pole_no'):
            raise ValidationError("ECG Pole No. is required when Electricity Connection is Yes")
        return cleaned_data

# Education Capture Admin
@admin.register(EducationCapture)
class EducationAdmin(admin.ModelAdmin):
    form = EducationCaptureForm
    list_display = (
        'serial_number', 'admin_ghana_card', 'category', 
        'boarding_facility', 'electricity_connection', 'date_created',
        'school_type', 'school_role', 'school_type1', 'area_zone'
    )
    list_filter = ('category', 'electricity_connection', 'school_type', 'area_zone', 'date_created')
    search_fields = ('serial_number', 'admin_ghana_card', 'school_type', 'area_zone')
    list_select_related = True
    date_hierarchy = 'date_created'

# Residential Capture Admin
@admin.register(ResidentialCapture)
class ResidentialCaptureAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number', 'category', 'gps_address', 'property_classification', 
        'building_type', 'number_of_floors', 'number_of_occupants', 'date_created'
    )
    list_filter = (
        'category', 'property_classification', 'building_type', 
        'fencing_type', 'water_supply', 'electricity_connection', 
        'proximity_to_public_infrastructure', 'flood_risk_area', 'date_created'
    )
    search_fields = (
        'serial_number', 'gps_address', 'street_name', 'area_name', 
        'house_number', 'neighbor_emergency_name', 'property_classification'
    )
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('serial_number', 'category'),
                ('date_created', 'date_updated'),
            )
        }),
        ('Location Details', {
            'fields': (
                'gps_address', 'area_zone', 'street_name', 'area_name',
                'house_number', 'property_classification', 'nature_ownership',
                ('neighbor_emergency_name', 'neighbor_emergency_contact'),
            )
        }),
        ('Building Details', {
            'fields': (
                'building_type', 'number_of_floors', 'number_of_rooms',
                'toilet_facility', 'parking_spaces', 'fencing_type',
                'building_condition', 'security_features', 'construction_material',
                'type_of_roof',
            )
        }),
        ('Utilities', {
            'fields': (
                'water_supply', 'gwcpl_supply', 'electricity_connection',
                'sewage_system', 'waste_disposal_method', 'internet_connectivity',
            )
        }),
        ('Occupancy', {
            'fields': (
                'number_of_occupants', 'type_of_occupancy', 'tenancy_status',
            )
        }),
        ('Environment & Security', {
            'fields': (
                'proximity_to_public_infrastructure', 'flood_risk_area',
                ('criminal_activities_1', 'criminal_activities_2', 'criminal_activities_3'),
                'network_connectivity', 'road_network',
            )
        }),
        ('Media', {
            'fields': (
                'profile_picture',
            )
        })
    )
    readonly_fields = ('serial_number', 'date_created', 'date_updated')
    list_per_page = 20
    list_select_related = True
    date_hierarchy = 'date_created'

# Health Capture Admin
@admin.register(HealthCapture)
class HealthCaptureAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number', 'hospital_name', 'hospital_admin',
        'hospital_admin_contact', 'gps_address', 'road_network',
        'road_condition', 'date_created',
    )
    search_fields = ('hospital_name', 'hospital_admin', 'gps_address')
    list_filter = ('category', 'road_network', 'road_condition', 
                  'nature_ownership', 'building_condition')
    list_editable = ('road_network', 'road_condition')
    fieldsets = (
        ('Basic Information', {
            'fields': ('category',)
        }),
        ('Hospital Details', {
            'fields': (
                'hospital_name', 'hospital_admin', 'hospital_admin_contact',
                'hospital_admin_ghana_card', 'gps_address', 'latitude', 'longitude',
                'area_zone', 'street_name', 'location', 'hospital_reg_no',
                'ambulance', 'nature_ownership', 'emergency_name', 'emergency_contact',
            )
        }),
        ('Infrastructure', {
            'fields': (
                'road_network', 'road_condition',
                'building_type', 'number_of_floors', 'number_of_beds', 
                'toilet_facility', 'parking_spaces', 'fenced', 'fencing_type',
                'building_condition', 'security_features', 'construction_material', 
                'type_of_roof',
            )
        }),
        ('Utilities', {
            'fields': (
                'water_supply', 'gwcpl_supply', 'electricity_connection', 
                'has_backup_generator', 'sewage_system', 'waste_disposal_method', 
                'internet_connectivity',
            )
        }),
        ('Environment & Security', {
            'fields': (
                'proximity_to_public_infrastructure', 'flood_risk_area',
                ('criminal_activities_1', 'criminal_activities_2', 'criminal_activities_3'),
                'network_connectivity',
            )
        }),
        ('Media', {
            'fields': ('profile_picture',)
        })
    )
    list_select_related = True
    date_hierarchy = 'date_created'

# Government Capture Admin
@admin.register(GovernmentCapture)
class GovernmentCaptureAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number', 'institutional_name', 'institutional_admin',
        'institutional_admin_contact', 'gps_address', 'road_network',
        'road_condition', 'date_created',
    )
    search_fields = ('institutional_name', 'institutional_admin', 'gps_address')
    list_filter = ('category', 'road_network', 'road_condition', 
                  'nature_ownership', 'building_condition')
    list_editable = ('road_network', 'road_condition')
    fieldsets = (
        ('Basic Information', {
            'fields': ('category',)
        }),
        ('Institution Details', {
            'fields': (
                'institutional_name', 'institutional_admin', 'institutional_admin_contact',
                'institutional_admin_ghana_card', 'gps_address', 'latitude', 'longitude',
                'area_zone', 'street_name', 'location', 'registration_no',
                'nature_ownership', 'service_type', 'emergency_name', 'emergency_contact',
            )
        }),
        ('Infrastructure', {
            'fields': (
                'road_network', 'road_condition',
                'building_type', 'number_of_floors', 'toilet_facility',
                'parking_spaces', 'fenced', 'fencing_type', 'building_condition',
                'security_features', 'construction_material', 'type_of_roof',
            )
        }),
        ('Utilities', {
            'fields': (
                'water_supply', 'gwcpl_supply', 'electricity_connection', 
                'has_backup_generator', 'sewage_system', 'waste_disposal_method', 
                'internet_connectivity',
            )
        }),
        ('Environment & Security', {
            'fields': (
                'proximity_to_public_infrastructure', 'flood_risk_area',
                ('criminal_activities_1', 'criminal_activities_2', 'criminal_activities_3'),
                'network_connectivity',
            )
        }),
        ('Media', {
            'fields': ('profile_picture',)
        })
    )
    list_select_related = True
    date_hierarchy = 'date_created'

