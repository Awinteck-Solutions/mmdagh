from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField  #
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import transaction
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

CATEGORY_CHOICES = [
    ('IND', 'Individual'),
    ('RES', 'Residential'),
    ('EDU', 'Education'),
    ('HTH', 'Health'),
    ('FIS', 'Financial Institution'),
    ('REG', 'Religious'),
    ('BUS', 'Business/Manufacturing'),
    ('GOV', 'Government Agencies'),
    ('SME', 'Business/SME'),
]

NETWORK_CHOICES = [
    ('Strong', 'Strong'),
    ('Average', 'Average'),
    ('Weak', 'Weak'),
    ('No Network', 'No Network'),
]

ROAD_CHOICES = [
    ('Tired', 'Tired'),
    ('Non-Tired', 'Non-Tired'),
    ('No Road', 'No Road')
]

REGION_CHOICES = [
    ('Greater Accra', 'Greater Accra'),
    ('Ashanti', 'Ashanti'),
    ('Western', 'Western'),
    ('Central', 'Central'),
    ('Eastern', 'Eastern'),
    ('Northern', 'Northern'),
    ('Upper East', 'Upper East'),
    ('Upper West', 'Upper West'),
    ('Volta', 'Volta'),
    ('Oti', 'Oti'),
    ('Western North', 'Western North'),
    ('Bono', 'Bono'),
    ('Bono East', 'Bono East'),
    ('Ahafo', 'Ahafo'),
    ('Savannah', 'Savannah'),
    ('North East', 'North East'),
]

#MMDA_CHOICES = [
    #('Ga West Municipal', 'Ga West Municipal'),
    #('Tema West', 'Tema West'),
    #('Tema East', 'Tema East'),
    #('Tema Central', 'Tema Central'),
    #('Kumasi Metro', 'Kumasi Metro'),
    #('Trobo Municipal', 'Trobo Municipal'),
    #('Krowo', 'Krowo'),
    #('La Dadekotopon', 'La Dadekotopon'),
    #('Ashaiman', 'Ashaiman'),
#]

LANGUAGE_CHOICES = [
    ('English', 'English'),
    ('Twi', 'Twi'),
    ('Hausa', 'Hausa'),
    ('Ga', 'Ga'),
    ('Kusaal', 'Kusaal'),
    ('Dagomba', 'Dagomba'),
    ('French', 'French'),
    ('Fante', 'Fante'),
    ('Ewe', 'Ewe'),
]

RELIGION_CHOICES = [
    ('Christian', 'Christian'),
    ('Muslim', 'Muslim'),
    ('Traditional', 'Traditional'),
    ('N/A', 'N/A'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]

CRIMINAL_CHOICES = [
    ('Stealing', 'Stealing'),
    ('Assault', 'Assault'),
    ('Fraud', 'Fraud'),
    ('Theft', 'Theft'),
    ('Rape & Defilement', 'Rape & Defilement'),
    ('Robbery', 'Robbery'),
]


SCHOOL_TYPE_CHOICES = [
    ('Private School', 'Private School'),
    ('Government School', 'Government School'),
]

SCHOOL_TYPE1_CHOICES = [
    ('Crech_or_ Montesori ', 'Crech_or_ Montesori'),
    ('Primary only,', 'Primary only'),
    ('J.H.S only', 'J.H.S only,'),
    ('S.H.S only', 'S.H.S only,'),
    ('University', 'University'),
    ('Crech,Primary,', 'Crech,Primary'),
    ('Crech,Primary,J.H.S', 'Crech,Primary,J.H.S'),
    ('Crech,Primary,J.H.S,S.H.S', 'Crech,Primary,J.H.S,S.H.S'),
    ('Crech,Primary,J.H.S,S.H.S,University', 'Crech,Primary,J.H.S,S.H.S,University'),
    ('Remedial', 'Remedial'),
]

SCHOOL_ROLE_CHOICES = [
    ('HeadMaster/Principal', 'HeadMaster/Principal'),
    ('Owner', 'Owner'),
    ('Teacher', 'Teacher'),
    ('Key_Contact', 'Key_Contact'),
]

AREA_ZONE_CHOICES = [
    ('Zone_A', 'Zone A'),
    ('Zone_B', 'Zone B'),
    ('Zone_C', 'Zone C'),
    ('Zone_D', 'Zone D'),("Urban", "Urban"), ("Rural", "Rural")
]


PROPERTY_CLASS_CHOICES= [
    ('Residential', 'Residential'),
    ('Commercial', 'Commercial'),
    ('Mixed-use', 'Mixed-use'),
]
OWNERSHIPS_STATUS_CHOICES= [
    ('Owner-occupied', 'Owner-occupied'),
    ('Apartment', 'Apartment'),
    ('Townhouse', 'Townhouse'),
]
BUILDING_TYPE_CHOICES= [
    ('Single-family home', 'Single-family home'),
    ('Apartment', 'Apartment'),
    ('Townhouse', 'Townhouse'),
]

FENCE_CHOICES= [
    ('Wall Fenced', 'Wall Fenced'),
    ('Hedged', 'Hedged'),
    ('Non-Fenced', 'Non-Fenced'),
]
BUILDING_CONDITION_CHOICES= [
    ('Excellent', 'Excellent'),
    ('Good', 'Good'),
    ('Average', 'Average'),
    ('Poor', 'Poor'),
]
SECURITY_FEATURES_CHOICES= [
    ('CCTV', 'CCTV'),
    ('Gated community', 'Gated community'),
    ('Security guard', 'Security guard'),
    ('All', 'All'),
]
MATERIAL_CHOICES= [
    ('Concrete/bricks', 'Concrete/bricks'),
    ('Wood', 'Wood'),
    ('Metal', 'Metal'),
]
ROOF_CHOICES= [
    ('Metal Sheet', 'Metal Sheet'),
    ('Thatched', 'Thatched'),
    ('Concrete', 'Concrete'),
]
WATER_SUPPY_CHOICES= [
    ('Piped/GWCL', 'Piped/GWCL'),
    ('Borehole', 'Borehole'),
    ('Well', 'Well'),
    ('Borehole', 'Borehole'),
    ('River', 'River'),
    ('N/A', 'N/A'),
]
ELECTRICTY_CHOICES= [
    ('National Grid', 'National Grid'),
    ('Solar', 'Solar'),
    ('N/A', 'N/A'),
]
SEWAGE_SYSTEM_CHOICES= [
    ('Connected to the sewer', 'Connected to the sewer'),
    ('Septic tank', 'Septic tank'),
    ('open drainage', 'open drainage'),
]
WASTEAGE_CHOICES= [
    ('Municipal collection', 'Municipal collection'),
    ('Burning', 'Burning'),
    ('Dumping', 'Dumping'),
]
INTERNET_CHOICES= [
    ('broadband', 'broadband'),
    ('Mobile', 'Mobile'),
    ('None', 'None'),
]


TENANCY_CHOICES= [
    ('Owner', 'Owner'),
    ('Tenant', 'Tenant'),
    ('Caretaker', 'Caretaker'),
]
PUBLIC_INFRA_CHOICES= [
    ('Church', 'Church'),
    ('Schools', 'Schools'),
    ('Hospitals', 'Hospitals'),
    ('Markets', 'Markets'),
]
TOILET_CHOICES= [
    ('In-house', 'In-house'),
    ('Public toilet', 'Public toilet'),
    ('Open defication', 'Open defication'),("Flush", "Flush"), ("Pit Latrine", "Pit Latrine")
]


NATURE_CHOICES= [
    ('Govt', 'Govt'),
    ('Private', 'Private'),
    ('Govt/Private', 'Govt/Private'),
    ('Religious', 'Religious'),
]

ROAD_CONDITION_CHOICES = [
    ('Good', 'Good'),('Fair', 'Fair'),('Poor', 'Poor'),("Paved", "Paved"), ("Gravel", "Gravel")
]

SERVICE_NATURE_CHOICES = [
    ('Security', 'Security'),('Financial', 'Financial'),('Accountancy', 'Accountancy'),
    ('Education','Education'),('MMDA', 'MMDA'),('Agri', 'Agri'),('Consultancy','Consultancy'),
    ('Trading','Trading'),('Other', 'Other'),
]


BOARDING_CHOICES = [

    ('day_only', 'Day Only'),('day_boarding', 'Day & Boarding')]

BUILDING_DESCRIPTION = [

    ('Paint', 'Paint'),('Ceramic', 'Ceramic'),('Tires', 'Tires'),('Other', 'Other')]

LAND_SIZE_CHOICES= [

    ('Half Plot', 'Half Plot'),('Quarter Plot', 'Quarter Plot'),('One Plot', 'One Plot'),('2 Plot', '3 Plot'),('3 Plot', '3 Plot'),('One Acre or more', 'One Acre or more')]

# account/models.py
from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=50, choices=REGION_CHOICES)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class MMDA(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=100, unique=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="mmdas")
    gps_address = models.CharField(max_length=100)
    location=models.CharField(max_length=100)
    contact_1 = models.CharField(max_length=20)  # Adjusted length for phone numbers
    contact_2 = models.CharField(max_length=10, blank=True, null=True)  # Adjusted length
    email= models.CharField(max_length=30)
    latitude = models.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    longitude = models.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])
    postal_address= models.CharField(max_length=100)
    logo_1 = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    local_govt_logo = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    coat_of_arms = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)


    def __str__(self):
        return f"{self.name} ({self.region.name})"

class UserAssignment(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="assignment")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    mmda = models.ForeignKey(MMDA, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        assigned = f"Region: {self.region.name}" if self.region else "Unassigned"
        if self.mmda:
            assigned += f", MMDA: {self.mmda.name}"
        return f"{self.user.username} - {assigned}"



def generate_serial_number(category):
    """
    Generate a unique serial number for a given category.
    Ensures uniqueness across all models even under concurrency.
    """
    date_str = timezone.now().strftime('%y%m%d')  # Format: YYMMDD
    
    with transaction.atomic():
        # Start count for the current category
        count = DataCapture.objects.filter(category=category).count() + 1
        serial_number = f"{category}{date_str}{str(count).zfill(4)}"
        
        # Check uniqueness across all relevant models
        while (
            EducationCapture.objects.filter(serial_number=serial_number).exists() or
            DataCapture.objects.filter(serial_number=serial_number).exists() or
            ResidentialCapture.objects.filter(serial_number=serial_number).exists() or
            HealthCapture.objects.filter(serial_number=serial_number).exists()
        ):
            count += 1
            serial_number = f"{category}{date_str}{str(count).zfill(4)}"
        
    return serial_number

class DataCapture(models.Model):
    # Account Details
    serial_number = models.CharField(max_length=20, unique=True, editable=False)
    category = models.CharField(max_length=10, default="INDV",editable=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)  # Add Region ForeignKey
    mmda = models.ForeignKey(MMDA, on_delete=models.CASCADE)  # Add Region ForeignKey
    # Personal Details
    ghana_card = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^GHA-\d{10}-\d*$',  # Matches the Ghana Card format
                message="Ghana Card should follow the format: GHA-XXXXXXXXXX-X where X is optional."
            )
        ]
    )
    first_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    contact_1 = PhoneNumberField()
    # Add other fields as require

    first_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    contact_1 = models.CharField(max_length=20)  # Adjusted length for phone numbers
    contact_2 = models.CharField(max_length=10, blank=True, null=True)  # Adjusted length
    home_town = models.CharField(max_length=50)
    home_region = models.CharField(max_length=50, choices=REGION_CHOICES)
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES)
    spouse_name = models.CharField(max_length=100)
    spouse_contact = models.CharField(max_length=10)
    neighbor_emergency_name = models.CharField(max_length=100)
    neighbor_emergency_contact = models.CharField(max_length=10)
    religion = models.CharField(max_length=50, choices=RELIGION_CHOICES)
    email= models.CharField(max_length=30)
    rooms = models.IntegerField(default=1)
   
    # Work Details
    occupation = models.CharField(max_length=50)
    name_of_place_of_work = models.CharField(max_length=50)
    location_of_place_work= models.CharField(max_length=50)
    work_place_contact=models.CharField(max_length=10)
    nature_ownership = models.CharField(max_length=100, choices=NATURE_CHOICES)

    # Facility
    house_number = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    street_name = models.CharField(max_length=100)
    area_name = models.CharField(max_length=100)
    area_zone = models.CharField(max_length=100, choices=AREA_ZONE_CHOICES)
    gps_address = models.CharField(max_length=100)
    latitude = models.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    longitude = models.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])
    electricity = models.BooleanField(default=False)
    gwcpl_supply = models.BooleanField(default=False)
    nearest_landmark = models.CharField(max_length=100)
    # Security
    criminal_activities_1 = models.CharField(max_length=50, choices=CRIMINAL_CHOICES)
    criminal_activities_2 = models.CharField(max_length=50, choices=CRIMINAL_CHOICES)
    criminal_activities_3 = models.CharField(max_length=50, choices=CRIMINAL_CHOICES)
    network_connectivity = models.CharField(max_length=20, choices=NETWORK_CHOICES)
    road_network = models.CharField(max_length=20, choices=ROAD_CHOICES)
    history = HistoricalRecords()
    #Profile Pictures/Image
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number = generate_serial_number(self.category)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.serial_number} - {self.first_name} {self.surname}"

    class Meta:
        verbose_name = "Data Capture"
        verbose_name_plural = "Data Captures"
        ordering = ['date_created']  # Optional: Order by creation date




#User = get_user_model()

class EducationCapture(models.Model):
    serial_number = models.CharField(max_length=20, unique=True, editable=False)
    category = models.CharField(max_length=10, default="EDU",editable=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    region = models.ForeignKey('Region', on_delete=models.CASCADE)
    mmda = models.ForeignKey('MMDA', on_delete=models.CASCADE)

    school_name = models.CharField(max_length=100)
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPE_CHOICES)
    school_role = models.CharField(max_length=20, choices=SCHOOL_ROLE_CHOICES)
    school_type1 = models.CharField(max_length=100, choices=SCHOOL_TYPE1_CHOICES)
    ges_approved = models.BooleanField(max_length=100,
        help_text="Select whether the facility is Ghana Education Service Approved.")

    boarding_facility = models.CharField(

        max_length=20,

        choices=BOARDING_CHOICES,

        default='day_only',  # Set a default value if needed

        help_text="Select whether the facility is for Day only or Day & Boarding."

    )
    school_contact = models.CharField(max_length=100, blank=True) 
    school_admin = models.CharField(max_length=100, blank=True)
    school_admin_contact = PhoneNumberField(blank=True)
    additional_contacts = models.JSONField(default=list)
    admin_ghana_card = models.OneToOneField('DataCapture', on_delete=models.CASCADE, related_name="education_capture", to_field="ghana_card")

    gps_address = models.CharField(max_length=100)
    latitude = models.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    longitude = models.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])
    
    area_zone = models.CharField(max_length=100, choices=AREA_ZONE_CHOICES)
    street_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    school_registered = models.BooleanField(default=False)
    registration_no = models.CharField(max_length=50, validators=[RegexValidator(regex=r'^[A-Za-z0-9\-]+$')])
    
    nature_ownership = models.CharField(max_length=100, choices=NATURE_CHOICES)
    service_type = models.CharField(max_length=100, choices=SERVICE_NATURE_CHOICES)
    emergency_name = models.CharField(max_length=100)
    emergency_contact = PhoneNumberField()
    school_buses_or_cars = models.BooleanField(default=False)

    building_type = models.CharField(max_length=50, choices=BUILDING_TYPE_CHOICES)
    number_of_floors = models.PositiveIntegerField()
    toilet_facility = models.CharField(max_length=50, choices=TOILET_CHOICES)
    parking_spaces = models.BooleanField(default=False)
    fenced = models.BooleanField(default=False)
    fencing_type = models.CharField(max_length=50, choices=FENCE_CHOICES, blank=True, null=True)
    building_condition = models.CharField(max_length=50, choices=BUILDING_CONDITION_CHOICES)
    security_features = models.JSONField(default=list)
    construction_material = models.CharField(max_length=50, choices=MATERIAL_CHOICES)
    type_of_roof = models.CharField(max_length=50, choices=ROOF_CHOICES)

    water_supply = models.CharField(max_length=50, choices=WATER_SUPPY_CHOICES)
    gwcpl_supply = models.BooleanField(default=False)
    electricity_connection = models.CharField(max_length=50, choices=ELECTRICTY_CHOICES)
    ecg_connection= models.BooleanField(default=False)
    ecg_pole_no= models.CharField(max_length=100)
    has_backup_generator = models.BooleanField(default=False)
    sewage_system = models.CharField(max_length=50, choices=SEWAGE_SYSTEM_CHOICES)
    waste_disposal_method = models.CharField(max_length=50, choices=WASTEAGE_CHOICES)
    internet_connectivity = models.CharField(max_length=50, choices=INTERNET_CHOICES)



    #Environmental Details
    proximity_to_public_infrastructure = models.CharField(max_length=50, choices=PUBLIC_INFRA_CHOICES)
    flood_risk_area = models.BooleanField(default=False)

    # Security
    criminal_activities_1 = models.CharField(max_length=50, choices=CRIMINAL_CHOICES)
    criminal_activities_2 = models.CharField(max_length=50, choices=CRIMINAL_CHOICES)
    criminal_activities_3 = models.CharField(max_length=50, choices=CRIMINAL_CHOICES)
    network_connectivity = models.CharField(max_length=50, choices=NETWORK_CHOICES)
    road_network = models.BooleanField(default=False)
    road_condition = models.CharField(max_length=50, choices=ROAD_CONDITION_CHOICES, blank=True, null=True)


    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, default='default_profile.jpg')

    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number = self.generate_serial_number()
        super().save(*args, **kwargs)

    def generate_serial_number(self):
        date_str = timezone.now().strftime('%y%m%d')
        last_count = EducationCapture.objects.filter(category=self.category).count() + 1
        return f"{self.category}{date_str}{str(last_count).zfill(4)}"

    def __str__(self):
        return f"{self.serial_number} - {self.school_name} ({self.gps_address})"

    class Meta:
        verbose_name = "Education Capture"
        verbose_name_plural = "Education Captures"
        ordering = ['-date_created', 'school_name']





from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator


class ResidentialCapture(models.Model):
    serial_number = models.CharField(max_length=20, unique=True, editable=False)
    category = models.CharField(max_length=10, default="RES", editable=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    region = models.ForeignKey('Region', on_delete=models.CASCADE)
    mmda = models.ForeignKey('MMDA', on_delete=models.CASCADE)

    # Changed to OneToOneField as per migration
    ghana_card = models.OneToOneField(
        'DataCapture',
        on_delete=models.CASCADE,
        related_name='residential_capture',
        help_text='Select a valid Ghana Card entry.'
    )
    
    principal_tenant = models.CharField(max_length=100, blank=True)
    principal_tenant_contact = PhoneNumberField(blank=True)
    number_of_occupants = models.CharField(max_length=100, blank=True)

    building_name = models.CharField(max_length=100)
    house_number = models.CharField(max_length=50)
    gps_address = models.CharField(max_length=100)
    latitude = models.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    longitude = models.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])
    area_zone = models.CharField(max_length=100, choices=AREA_ZONE_CHOICES)
    street_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    property_classification = models.CharField(max_length=100, choices=PROPERTY_CLASS_CHOICES)
    ownership_status = models.CharField(max_length=50, choices=OWNERSHIPS_STATUS_CHOICES)
    neighbor_emergency_name = models.CharField(max_length=100)
    neighbor_emergency_contact = PhoneNumberField()

    nature_ownership = models.CharField(max_length=100, choices=NATURE_CHOICES)
    building_description = models.CharField(max_length=100, choices=BUILDING_DESCRIPTION )

    building_type = models.CharField(max_length=50, choices=BUILDING_TYPE_CHOICES)
    land_size = models.CharField(max_length=50, choices=LAND_SIZE_CHOICES)
    number_of_floors = models.PositiveIntegerField()
    number_of_rooms = models.PositiveIntegerField()
    toilet_facility = models.CharField(max_length=50, choices=TOILET_CHOICES)
    parking_spaces = models.BooleanField(default=False)
    fenced = models.BooleanField(default=False)
    fencing_type = models.CharField(max_length=50, choices=FENCE_CHOICES, blank=True, null=True)
    building_condition = models.CharField(max_length=50, choices=BUILDING_CONDITION_CHOICES)
    security_features = models.JSONField(default=list)
    construction_material = models.CharField(max_length=50, choices=MATERIAL_CHOICES)
    type_of_roof = models.CharField(max_length=50, choices=ROOF_CHOICES)
    fire_hydrant_availability = models.BooleanField(default=False)
    fire_extinguishers_availability = models.BooleanField(default=False)
    water_supply = models.CharField(max_length=50, choices=WATER_SUPPY_CHOICES)
    gwcpl_supply = models.BooleanField(default=False)
    electricity_connection = models.CharField(max_length=50, choices=ELECTRICTY_CHOICES)
    ecg_connection = models.BooleanField(default=False)
    ecg_pole_no = models.CharField(max_length=100)
    has_backup_generator = models.BooleanField(default=False)
    sewage_system = models.CharField(max_length=50, choices=SEWAGE_SYSTEM_CHOICES)
    waste_disposal_method = models.CharField(max_length=50, choices=WASTEAGE_CHOICES)
    internet_connectivity = models.CharField(max_length=50, choices=INTERNET_CHOICES)

    # Environmental Details
    proximity_to_public_infrastructure = models.CharField(max_length=50, choices=PUBLIC_INFRA_CHOICES)
    name_of_public_infr = models.CharField(max_length=50)
    flood_risk_area = models.BooleanField(default=False)

    # Security
    criminal_activities_1 = models.CharField(max_length=50, choices=CRIMINAL_CHOICES)
    criminal_activities_2 = models.CharField(max_length=50, choices=CRIMINAL_CHOICES)
    criminal_activities_3 = models.CharField(max_length=50, choices=CRIMINAL_CHOICES)


    network_connectivity = models.CharField(max_length=50, choices=NETWORK_CHOICES)
    road_network = models.BooleanField(default=False)
    road_condition = models.CharField(max_length=50, choices=ROAD_CONDITION_CHOICES, blank=True, null=True)

    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number = self.generate_serial_number()
        super().save(*args, **kwargs)

    def generate_serial_number(self):
        date_str = timezone.now().strftime('%y%m%d')
        last_count = ResidentialCapture.objects.filter(category=self.category).count() + 1
        return f"{self.category}{date_str}{str(last_count).zfill(4)}"

    def __str__(self):
        return f"{self.serial_number} - {self.building_name} ({self.gps_address})"

    class Meta:
        verbose_name = "Residential Capture"
        verbose_name_plural = "Residential Captures"
        ordering = ['-date_created', 'building_name']





 #Health Captures
class HealthCapture(models.Model):
    # Account Details
    serial_number = models.CharField(max_length=20, unique=True, editable=False)
    category = models.CharField(max_length=10, default="HTH",editable=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)  # Add Region ForeignKey
    mmda = models.ForeignKey(MMDA, on_delete=models.CASCADE)  # Add Region ForeignKey

    # General Property Information
    hospital_name = models.CharField(max_length=100)
    hospital_admin = models.CharField(max_length=100, blank=True)  # Populated from Ghana Card
    hospital_admin_contact = PhoneNumberField(blank=True)          # Populated from Ghana Card
    additional_contacts = models.JSONField(default=list)           # For storing extra numbers
    #hospital_admin_ghana_card= models.OneToOneField(DataCapture, on_delete=models.CASCADE, related_name="health_capture", to_field="ghana_card")
    # One-to-One relationship with DataCapture for Ghana Card
    hospital_admin_ghana_card = models.OneToOneField(
        DataCapture,
        on_delete=models.CASCADE,
        related_name="health_capture",
        to_field="ghana_card",
        help_text="Select a valid Ghana Card entry."
    )

    gps_address = models.CharField(max_length=100)
    latitude = models.FloatField(
        validators=[
            MinValueValidator(-90.0),
            MaxValueValidator(90.0)
        ],
        help_text="Latitude must be between -90.0 and 90.0."
    )
    longitude = models.FloatField(
        validators=[
            MinValueValidator(-180.0),
            MaxValueValidator(180.0)
        ],
        help_text="Longitude must be between -180.0 and 180.0."
    )
    area_zone = models.CharField(max_length=100, choices=AREA_ZONE_CHOICES)
    street_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    hospital_reg_no = models.CharField(
        max_length=50,
        validators=[RegexValidator(regex=r'^[A-Za-z0-9\-]+$', message="Invalid registration number format.")]
    )
    ambulance = models.BooleanField(default=False)
    #average_daily_admin = models.FloatField(default=0.0, help_text="Average number of daily admissions.")
    nature_ownership = models.CharField(max_length=100, choices=NATURE_CHOICES)
    emergency_name = models.CharField(max_length=100)
    emergency_contact = PhoneNumberField()

    # Other fields remain unchanged...


    def clean(self):
        """
        Combined validation logic for the model.
        """
        if self.hospital_admin_ghana_card:
            ghana_card_data = self._parse_ghana_card(self.hospital_admin_ghana_card.ghana_card)
            if not ghana_card_data:
                raise ValidationError("Invalid Ghana Card data or lookup failed.")
            self.hospital_admin = f"{ghana_card_data['first_name']} {ghana_card_data['surname']}"
            self.hospital_admin_contact = ghana_card_data['contact']

        if self.road_network and not self.road_condition:
            raise ValidationError("If road network exists, road condition must be specified.")

        # Add more interdependent field validations as necessary...

    def _parse_ghana_card(self, ghana_card):
        """
        Fetch Ghana Card data dynamically from the database.
        """
        try:
            # Assuming 'DataCapture' contains Ghana Card data
            ghana_card_record = DataCapture.objects.get(ghana_card=ghana_card)
            return {
                "first_name": ghana_card_record.first_name,  # Replace with actual fields
                "surname": ghana_card_record.surname,        # Replace with actual fields
                "contact": ghana_card_record.contact_1         # Replace with actual fields
            }
        except DataCapture.DoesNotExist:
            return None


    # Building Information
    building_type = models.CharField(max_length=50, choices=BUILDING_TYPE_CHOICES)
    number_of_floors = models.PositiveIntegerField()
    number_of_beds = models.PositiveIntegerField()
    toilet_facility = models.CharField(max_length=50, choices=TOILET_CHOICES)
    parking_spaces = models.BooleanField(default=False)
    fenced = models.BooleanField(default=False)
    fencing_type = models.CharField(max_length=50, choices=FENCE_CHOICES, blank=True, null=True)
    building_condition = models.CharField(max_length=50, choices=BUILDING_CONDITION_CHOICES)
    security_features = models.JSONField(default=dict)  # Allows flexibility for multiple features
    construction_material = models.CharField(max_length=50, choices=MATERIAL_CHOICES)
    type_of_roof = models.CharField(max_length=50, choices=ROOF_CHOICES)

    # Utility Information
    water_supply = models.CharField(max_length=50, choices=WATER_SUPPY_CHOICES)
    gwcpl_supply = models.BooleanField(default=False)
    electricity_connection = models.CharField(max_length=50, choices=ELECTRICTY_CHOICES)
    has_backup_generator = models.BooleanField(default=False)
    sewage_system = models.CharField(max_length=50, choices=SEWAGE_SYSTEM_CHOICES)
    waste_disposal_method = models.CharField(max_length=50, choices=WASTEAGE_CHOICES)
    internet_connectivity = models.CharField(max_length=50, choices=INTERNET_CHOICES)

    # Environmental Details
    proximity_to_public_infrastructure = models.CharField(max_length=50, choices=PUBLIC_INFRA_CHOICES)
    flood_risk_area = models.BooleanField(default=False)

    # Security
    criminal_activities = models.JSONField(default=list)  # Replace multiple fields with a single JSONField
    network_connectivity = models.CharField(max_length=50, choices=NETWORK_CHOICES)
        # Road Network Section
    road_network = models.BooleanField(default=False)  # If true, road_condition should be specified
    road_condition = models.CharField(
        max_length=50,
        choices=ROAD_CONDITION_CHOICES,
        blank=True,
        null=True,
        help_text="If road network exists, specify the condition of the road."
    )

    # Profile Picture/Image
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Override save to generate a unique serial number if not set.
        """
        if not self.serial_number:
            self.serial_number = self.generate_serial_number()
        super().save(*args, **kwargs)

    def generate_serial_number(self):
        """
        Generate a unique serial number using the category and date.
        Ensures uniqueness even under concurrency.
        """
        date_str = timezone.now().strftime('%y%m%d')
        with transaction.atomic():
            count = DataCapture.objects.filter(category=self.category).count() + 1
            serial_number = f"{self.category}{date_str}{str(count).zfill(4)}"
            while HealthCapture.objects.filter(serial_number=serial_number).exists():
                count += 1
                serial_number = f"{self.category}{date_str}{str(count).zfill(4)}"
        return serial_number

    def __str__(self):
        return f"{self.serial_number} - {self.hospital_name} ({self.gps_address})"

    class Meta:
        verbose_name = "Health Capture"
        verbose_name_plural = "Health Captures"
        ordering = ['-date_created', 'hospital_name']


 #Government Captures
class GovernmentCapture(models.Model):
    # Account Details
    serial_number = models.CharField(max_length=20, unique=True, editable=False)
    category = models.CharField(max_length=10, default="GOV",editable=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)  # Add Region ForeignKey
    mmda = models.ForeignKey(MMDA, on_delete=models.CASCADE)  # Add Region ForeignKey

    # General Property Information
    institutional_name = models.CharField(max_length=100)
    institutional_contact = models.CharField(max_length=100, blank=True)     
    institutional_admin = models.CharField(max_length=100, blank=True)  # Populated from Ghana Card
    institutional_admin_contact = PhoneNumberField(blank=True)          # Populated from Ghana Card
    additional_contacts = models.JSONField(default=list)           # For storing extra numbers
    institutional_admin_ghana_card = models.OneToOneField(
        DataCapture,
        on_delete=models.CASCADE,
        related_name="government_capture",
        to_field="ghana_card",
        help_text="Select a valid Ghana Card entry."
    )

    gps_address = models.CharField(max_length=100)
    latitude = models.FloatField(
        validators=[
            MinValueValidator(-90.0),
            MaxValueValidator(90.0)
        ],
        help_text="Latitude must be between -90.0 and 90.0."
    )
    longitude = models.FloatField(
        validators=[
            MinValueValidator(-180.0),
            MaxValueValidator(180.0)
        ],
        help_text="Longitude must be between -180.0 and 180.0."
    )
    area_zone = models.CharField(max_length=100, choices=AREA_ZONE_CHOICES)
    street_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    registration_no = models.CharField(
        max_length=50,
        validators=[RegexValidator(regex=r'^[A-Za-z0-9\-]+$', message="Invalid registration number format.")]
    )

    nature_ownership = models.CharField(max_length=100, choices=NATURE_CHOICES)
    service_type = models.CharField(max_length=100, choices=SERVICE_NATURE_CHOICES)
    emergency_name = models.CharField(max_length=100)
    emergency_contact = PhoneNumberField()

    # Other fields remain unchanged...


    def clean(self):
        """
        Combined validation logic for the model.
        """
        if self.institutional_admin_ghana_card:
            ghana_card_data = self._parse_ghana_card(self.institutional_admin_ghana_card.ghana_card)
            if not ghana_card_data:
                raise ValidationError("Invalid Ghana Card data or lookup failed.")
            self.institutional_admin = f"{ghana_card_data['first_name']} {ghana_card_data['surname']}"
            self.institutional_admin_contact = ghana_card_data['contact']

        if self.road_network and not self.road_condition:
            raise ValidationError("If road network exists, road condition must be specified.")

        # Add more interdependent field validations as necessary...

    def _parse_ghana_card(self, ghana_card):
        """
        Fetch Ghana Card data dynamically from the database.
        """
        try:
            # Assuming 'DataCapture' contains Ghana Card data
            ghana_card_record = DataCapture.objects.get(ghana_card=ghana_card)
            return {
                "first_name": ghana_card_record.first_name,  # Replace with actual fields
                "surname": ghana_card_record.surname,        # Replace with actual fields
                "contact": ghana_card_record.contact_1         # Replace with actual fields
            }
        except DataCapture.DoesNotExist:
            return None


    # Building Information
    building_type = models.CharField(max_length=50, choices=BUILDING_TYPE_CHOICES)
    number_of_floors = models.PositiveIntegerField()
    toilet_facility = models.CharField(max_length=50, choices=TOILET_CHOICES)
    parking_spaces = models.BooleanField(default=False)
    fenced = models.BooleanField(default=False)
    fencing_type = models.CharField(max_length=50, choices=FENCE_CHOICES, blank=True, null=True)
    building_condition = models.CharField(max_length=50, choices=BUILDING_CONDITION_CHOICES)
    security_features = models.JSONField(default=dict)  # Allows flexibility for multiple features
    construction_material = models.CharField(max_length=50, choices=MATERIAL_CHOICES)
    type_of_roof = models.CharField(max_length=50, choices=ROOF_CHOICES)

    # Utility Information
    water_supply = models.CharField(max_length=50, choices=WATER_SUPPY_CHOICES)
    gwcpl_supply = models.BooleanField(default=False)
    electricity_connection = models.CharField(max_length=50, choices=ELECTRICTY_CHOICES)
    has_backup_generator = models.BooleanField(default=False)
    sewage_system = models.CharField(max_length=50, choices=SEWAGE_SYSTEM_CHOICES)
    waste_disposal_method = models.CharField(max_length=50, choices=WASTEAGE_CHOICES)
    internet_connectivity = models.CharField(max_length=50, choices=INTERNET_CHOICES)

    # Environmental Details
    proximity_to_public_infrastructure = models.CharField(max_length=50, choices=PUBLIC_INFRA_CHOICES)
    flood_risk_area = models.BooleanField(default=False)

    # Security
    criminal_activities = models.JSONField(default=list)  # Replace multiple fields with a single JSONField
    network_connectivity = models.CharField(max_length=50, choices=NETWORK_CHOICES)
        # Road Network Section
    road_network = models.BooleanField(default=False)  # If true, road_condition should be specified
    road_condition = models.CharField(
        max_length=50,
        choices=ROAD_CONDITION_CHOICES,
        blank=True,
        null=True,
        help_text="If road network exists, specify the condition of the road."
    )

    # Profile Picture/Image
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Override save to generate a unique serial number if not set.
        """
        if not self.serial_number:
            self.serial_number = self.generate_serial_number()
        super().save(*args, **kwargs)

    def generate_serial_number(self):
        """
        Generate a unique serial number using the category and date.
        Ensures uniqueness even under concurrency.
        """
        date_str = timezone.now().strftime('%y%m%d')
        with transaction.atomic():
            count = DataCapture.objects.filter(category=self.category).count() + 1
            serial_number = f"{self.category}{date_str}{str(count).zfill(4)}"
            while GovernmentCapture.objects.filter(serial_number=serial_number).exists():
                count += 1
                serial_number = f"{self.category}{date_str}{str(count).zfill(4)}"
        return serial_number

    def __str__(self):
        return f"{self.serial_number} - {self.institutional_name} ({self.gps_address})"

    class Meta:
        verbose_name = "Government Capture"
        verbose_name_plural = "Government Captures"
        ordering = ['-date_created', 'institutional_name']



 #BUSINESS/SME Captures
class SMECapture(models.Model):
    # Account Details
    serial_number = models.CharField(max_length=20, unique=True, editable=False)
    category = models.CharField(max_length=10, default="SME")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)  # Add Region ForeignKey
    mmda = models.ForeignKey(MMDA, on_delete=models.CASCADE)  # Add Region ForeignKey

    # General Property Information
    sme_name = models.CharField(max_length=100)
    sme_contact = models.CharField(max_length=100, blank=True) 
    sme_admin = models.CharField(max_length=100, blank=True)  # Populated from Ghana Card
    sme_admin_contact = PhoneNumberField(blank=True)          # Populated from Ghana Card
    additional_contacts = models.JSONField(default=list)           # For storing extra numbers
    sme_admin_ghana_card = models.OneToOneField(
        DataCapture,
        on_delete=models.CASCADE,
        related_name="SME_capture",
        to_field="ghana_card",
        help_text="Select a valid Ghana Card entry."
    )

    gps_address = models.CharField(max_length=100)
    latitude = models.FloatField(
        validators=[
            MinValueValidator(-90.0),
            MaxValueValidator(90.0)
        ],
        help_text="Latitude must be between -90.0 and 90.0."
    )
    longitude = models.FloatField(
        validators=[
            MinValueValidator(-180.0),
            MaxValueValidator(180.0)
        ],
        help_text="Longitude must be between -180.0 and 180.0."
    )
    area_zone = models.CharField(max_length=100, choices=AREA_ZONE_CHOICES)
    street_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    sme_registered = models.BooleanField(default=False)
    registration_no = models.CharField(
        max_length=50,
        validators=[RegexValidator(regex=r'^[A-Za-z0-9\-]+$', message="Invalid registration number format.")]
    )

    nature_ownership = models.CharField(max_length=100, choices=NATURE_CHOICES)
    service_type = models.CharField(max_length=100, choices=SERVICE_NATURE_CHOICES)
    emergency_name = models.CharField(max_length=100)
    emergency_contact = PhoneNumberField()

    # Other fields remain unchanged...



    # Building Information
    building_type = models.CharField(max_length=50, choices=BUILDING_TYPE_CHOICES)
    number_of_floors = models.PositiveIntegerField()
    toilet_facility = models.CharField(max_length=50, choices=TOILET_CHOICES)
    parking_spaces = models.BooleanField(default=False)
    fenced = models.BooleanField(default=False)
    fencing_type = models.CharField(max_length=50, choices=FENCE_CHOICES, blank=True, null=True)
    building_condition = models.CharField(max_length=50, choices=BUILDING_CONDITION_CHOICES)
    security_features = models.JSONField(default=dict)  # Allows flexibility for multiple features
    construction_material = models.CharField(max_length=50, choices=MATERIAL_CHOICES)
    type_of_roof = models.CharField(max_length=50, choices=ROOF_CHOICES)

    # Utility Information
    water_supply = models.CharField(max_length=50, choices=WATER_SUPPY_CHOICES)
    gwcpl_supply = models.BooleanField(default=False)
    electricity_connection = models.CharField(max_length=50, choices=ELECTRICTY_CHOICES)
    has_backup_generator = models.BooleanField(default=False)
    sewage_system = models.CharField(max_length=50, choices=SEWAGE_SYSTEM_CHOICES)
    waste_disposal_method = models.CharField(max_length=50, choices=WASTEAGE_CHOICES)
    internet_connectivity = models.CharField(max_length=50, choices=INTERNET_CHOICES)

    # Environmental Details
    proximity_to_public_infrastructure = models.CharField(max_length=50, choices=PUBLIC_INFRA_CHOICES)
    flood_risk_area = models.BooleanField(default=False)

    # Security
    criminal_activities = models.JSONField(default=list)  # Replace multiple fields with a single JSONField
    network_connectivity = models.CharField(max_length=50, choices=NETWORK_CHOICES)
        # Road Network Section
    road_network = models.BooleanField(default=False)  # If true, road_condition should be specified
    road_condition = models.CharField(
        max_length=50,
        choices=ROAD_CONDITION_CHOICES,
        blank=True,
        null=True,
        help_text="If road network exists, specify the condition of the road."
    )

    # Profile Picture/Image
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, default='default_profile.jpg')

    def save(self, *args, **kwargs):
        """
        Override save to generate a unique serial number if not set.
        """
        if not self.serial_number:
            self.serial_number = self.generate_serial_number()
        super().save(*args, **kwargs)

    def generate_serial_number(self):
        """
        Generate a unique serial number using the category and date.
        Ensures uniqueness even under concurrency.
        """
        date_str = timezone.now().strftime('%y%m%d')
        with transaction.atomic():
            count = DataCapture.objects.filter(category=self.category).count() + 1
            serial_number = f"{self.category}{date_str}{str(count).zfill(4)}"
            while SMECapture.objects.filter(serial_number=serial_number).exists():
                count += 1
                serial_number = f"{self.category}{date_str}{str(count).zfill(4)}"
        return serial_number

    def __str__(self):
        return f"{self.serial_number} - {self.sme_name} ({self.gps_address})"

    class Meta:
        verbose_name = "SME Capture"
        verbose_name_plural = "SME Captures"
        ordering = ['-date_created', 'sme_name']

def clean(self):
    """
    Combined validation logic for the model.
    """
    if self.sme_admin_ghana_card:
        ghana_card_data = self._parse_ghana_card(self.sme_admin_ghana_card.ghana_card)
        if not ghana_card_data:
            raise ValidationError("Invalid Ghana Card data or lookup failed.")
        self.sme_admin = f"{ghana_card_data['first_name']} {ghana_card_data['surname']}"
        self.sme_admin_contact = ghana_card_data['contact']

    if hasattr(self, 'road_network') and self.road_network and not getattr(self, 'road_condition', None):
        raise ValidationError("If road network exists, road condition must be specified.")

    # Add more interdependent field validations as necessary...

    def _parse_ghana_card(self, ghana_card):
        """
        Fetch Ghana Card data dynamically from the database.
        """
        try:
            # Assuming 'DataCapture' contains Ghana Card data
            ghana_card_record = DataCapture.objects.get(ghana_card=ghana_card)
            return {
                "first_name": ghana_card_record.first_name,  # Replace with actual fields
                "surname": ghana_card_record.surname,        # Replace with actual fields
                "contact": ghana_card_record.contact_1         # Replace with actual fields
            }
        except DataCapture.DoesNotExist:
            return None