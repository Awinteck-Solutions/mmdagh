from django.contrib import admin
from .models import DataCapture ,EducationCapture,ResidentialCapture,HealthCapture,GovernmentCapture
from django.core.exceptions import ValidationError
from .models import Region, MMDA, UserAssignment 
from simple_history.admin import SimpleHistoryAdmin

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name","code")
    search_fields = ("name","code")

@admin.register(MMDA)
class MMDAAdmin(admin.ModelAdmin):
    list_display = ("name", "region")
    search_fields = ("name", "region__name")
    list_filter = ("region",)

@admin.register(UserAssignment)
class UserAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "region", "mmda")
    search_fields = ("user__username", "region__name", "mmda__name")
    list_filter = ("region", "mmda")


from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import DataCapture  # Adjust the import based on your project structure

@admin.register(DataCapture)
class DataCaptureAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ('serial_number', 'first_name', 'surname', 'category', 'contact_1', 'network_connectivity', 'date_created')
    list_filter = ('category', 'date_created')
    search_fields = ('first_name', 'surname', 'serial_number')

@admin.register(EducationCapture)
class EducationAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number','admin_ghana_card', 'category', 
        'boarding_facility', 'electricity_connection', 'date_created','school_type','school_role','school_type1','area_zone'
    )
    list_filter = ('category', 'electricity_connection','school_type','area_zone', 'date_created')
    search_fields = ('serial_number','admin_ghana_card','school_type','area_zone')

    def save_model(self, request, obj, form, change):
        if obj.electricity_connection and not obj.ecg_pole_no:
            raise ValidationError("If electricity access is Yes, ECG Pole No. is required.")
        super().save_model(request, obj, form, change)





@admin.register(ResidentialCapture)
class ResidentialCaptureAdmin(admin.ModelAdmin):
    # Display fields in the admin list view
    list_display = (
        'serial_number', 'category', 'gps_address', 'property_classification', 
        'building_type', 'number_of_floors', 'number_of_occupants', 'date_created'
    )
    
    # Filters in the admin interface
    list_filter = (
        'category', 'property_classification', 'building_type', 
        'fencing_type', 'water_supply', 'electricity_connection', 
        'proximity_to_public_infrastructure', 'flood_risk_area', 'date_created'
    )
    
    # Fields to search for in the admin interface
    search_fields = (
        'serial_number', 'gps_address', 'street_name', 'area_name', 
        'house_number', 'neighbor_emergency_name', 'property_classification'
    )
    
    # Fields to display in the detailed view
    fields = (
        # Account Details
        ('serial_number', 'category'),
        ('date_created', 'date_updated'),
        
        # General Property Information
        'gps_address', 'area_zone', 'street_name', 'area_name', 
        'house_number', 'property_classification', 'Ownership_Status', 
        ('neighbor_emergency_name', 'neighbor_emergency_contact'),
        
        # Building Information
        'building_type', 'number_of_floors', 'number_of_rooms', 
        'toilet_facility', 'parking_Spaces_available', 'fencing_type', 
        'building_condition', 'security_features', 'construction_material', 
        'type_of_roof',
        
        # Utility Information
        'water_supply', 'gwcpl_supply', 'electricity_connection', 
        'sewage_system', 'waste_disposal_method', 'internet_connectivity',
        
        # Occupancy Details
        'number_of_occupants', 'type_of_occupancy', 'tenancy_status',
        
        # Environmental Details
        'proximity_to_public_infrastructure', 'flood_risk_area',
        
        # Security
        ('criminal_activities_1', 'criminal_activities_2', 'criminal_activities_3'),
        'network_connectivity', 'road_network',
        
        # Profile Pictures/Image
        'profile_picture',
    )
    
    # Mark fields as read-only
    readonly_fields = ('serial_number', 'date_created', 'date_updated')
    
    # Pagination settings
    list_per_page = 20

    # Customize how objects are represented in the admin interface
    def __str__(self):
        return f"{self.serial_number} - {self.gps_address}"




'''@admin.register(GovernmentCapture)
class GovernmentCaptureAdmin(admin.ModelAdmin):
    exclude = ('category',)  # Ensure category is not included in the form
    
    # Display fields in the admin list view
    list_display = (
        'serial_number', 'category', 'gps_address', 'property_classification', 
        'building_type', 'number_of_floors', 'date_created'
    )
    
    # Filters in the admin interface
    list_filter = (
        'property_classification', 'building_type', 
        'fencing_type', 'water_supply', 'electricity_connection', 
        'proximity_to_public_infrastructure', 'flood_risk_area', 'date_created'
    )
    
    # Fields to search for in the admin interface
    search_fields = (
        'serial_number', 'gps_address', 'street_name', 'area_name', 
        'house_number', 'neighbor_emergency_name', 'property_classification'
    )
    
    # Fields to display in the detailed view (REMOVED 'category')
    fields = (
        # Account Details
        ('serial_number',),
        ('date_created', 'date_updated'),
        
        # General Property Information
        'gps_address', 'area_zone', 'street_name', 'area_name', 
        'house_number', 'property_classification', 'Ownership_Status', 
        ('neighbor_emergency_name', 'neighbor_emergency_contact'),
        
        # Building Information
        'building_type', 'number_of_floors', 'number_of_rooms', 
        'toilet_facility', 'parking_Spaces_available', 'fencing_type', 
        'building_condition', 'security_features', 'construction_material', 
        'type_of_roof',
        
        # Utility Information
        'water_supply', 'gwcpl_supply', 'electricity_connection', 
        'sewage_system', 'waste_disposal_method', 'internet_connectivity',
        
        'type_of_occupancy', 'tenancy_status',
        
        # Environmental Details
        'proximity_to_public_infrastructure', 'flood_risk_area',
        
        # Security
        ('criminal_activities_1', 'criminal_activities_2', 'criminal_activities_3'),
        'network_connectivity', 'road_network',
        
        # Profile Pictures/Image
        'profile_picture',
    )
    
    # Mark fields as read-only
    readonly_fields = ('serial_number', 'date_created', 'date_updated')
    
    # Pagination settings
    list_per_page = 20

    # Customize how objects are represented in the admin interface
    def __str__(self):
        return f"{self.serial_number} - {self.gps_address}"
'''



# HealthCapture Admin Class
class HealthCaptureAdmin(admin.ModelAdmin):
    # Display these fields in the list view (overview screen)
    list_display = (
        'serial_number',
        'hospital_name',
        'hospital_admin',
        'hospital_admin_contact',
        'gps_address',
        'road_network',
        'road_condition',
        'date_created',
    )
    
    # Add search functionality
    search_fields = ('hospital_name', 'hospital_admin', 'gps_address',)

    # Filter options in the sidebar
    list_filter = ('category', 'road_network', 'road_condition', 'nature_ownership', 'building_condition')

    # Make fields editable directly from the list page
    list_editable = ('road_network', 'road_condition')

    # Display more detailed information when editing
    fieldsets = (
        (None, {
            'fields': (
                'category',
            )
        }),
        ('General Property Information', {
            'fields': (
                'hospital_name', 'hospital_admin', 'hospital_admin_contact',
                'hospital_admin_ghana_card', 'gps_address', 'latitude', 'longitude',
                'area_zone', 'street_name', 'location', 'hospital_reg_no',
                'ambulance', 'nature_ownership',
                'emergency_name', 'emergency_contact',
            )
        }),
        ('Road Network', {
            'fields': (
                'road_network', 'road_condition',
            )
        }),
        ('Building Information', {
            'fields': (
                'building_type', 'number_of_floors', 'number_of_beds', 'toilet_facility',
                'parking_spaces', 'fenced', 'fencing_type', 'building_condition',
                'security_features', 'construction_material', 'type_of_roof',
            )
        }),
        ('Utility Information', {
            'fields': (
                'water_supply', 'gwcpl_supply', 'electricity_connection', 'has_backup_generator',
                'sewage_system', 'waste_disposal_method', 'internet_connectivity',
            )
        }),
        ('Environmental Details', {
            'fields': (
                'proximity_to_public_infrastructure', 'flood_risk_area',
            )
        }),
        ('Security', {
            'fields': (
                'criminal_activities', 'network_connectivity',
            )
        }),
        ('Profile Picture', {
            'fields': (
                'profile_picture',
            )
        })
    )

# Unregister the model only if it is registered
try:
    admin.site.unregister(HealthCapture)
except admin.sites.NotRegistered:
    pass  # Ignore the exception if the model is not already registered

# Register the model and admin class
admin.site.register(HealthCapture, HealthCaptureAdmin)


# GovernmentCapture Admin Class
class GovernmentCaptureAdmin(admin.ModelAdmin):
    # Display these fields in the list view (overview screen)
    list_display = (
        'serial_number',
        'institutional_name',
        'institutional_admin',
        'institutional_admin_contact',
        'gps_address',
        'road_network',
        'road_condition',
        'date_created',
    )
    
    # Add search functionality
    search_fields = ('institutional_name','institutional_admin','gps_address',)

    # Filter options in the sidebar
    list_filter = ('category','road_network','road_condition','nature_ownership','building_condition')

    # Make fields editable directly from the list page
    list_editable = ('road_network','road_condition')

    # Display more detailed information when editing
    fieldsets = (
        (None, {
            'fields': (
                'category',
            )
        }),
        ('General Property Information', {
            'fields': (
                'institutional_name', 'institutional_admin', 'institutional_admin_contact',
                'institutional_admin_ghana_card', 'gps_address', 'latitude', 'longitude',
                'area_zone', 'street_name', 'location', 'registration_no',
                'nature_ownership','service_type',
                'emergency_name', 'emergency_contact',
            )
        }),
        ('Road Network', {
            'fields': (
                'road_network', 'road_condition',
            )
        }),
        ('Building Information', {
            'fields': (
                'building_type', 'number_of_floors', 'toilet_facility',
                'parking_spaces', 'fenced', 'fencing_type', 'building_condition',
                'security_features', 'construction_material', 'type_of_roof',
            )
        }),
        ('Utility Information', {
            'fields': (
                'water_supply', 'gwcpl_supply', 'electricity_connection', 'has_backup_generator',
                'sewage_system', 'waste_disposal_method', 'internet_connectivity',
            )
        }),
        ('Environmental Details', {
            'fields': (
                'proximity_to_public_infrastructure', 'flood_risk_area',
            )
        }),
        ('Security', {
            'fields': (
                'criminal_activities', 'network_connectivity',
            )
        }),
        ('Profile Picture', {
            'fields': (
                'profile_picture',
            )
        })
    )

# Unregister the model only if it is registered
try:
    admin.site.unregister(GovernmentCapture)
except admin.sites.NotRegistered:
    pass  # Ignore the exception if the model is not already registered

# Register the model and admin class
admin.site.register(GovernmentCapture, GovernmentCaptureAdmin)


