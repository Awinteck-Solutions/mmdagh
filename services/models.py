from django.db import models
from django.contrib.auth.models import User  # Used for linking models to users
from accounts.models import Region,MMDA,AREA_ZONE_CHOICES,NATURE_CHOICES  # Importing from account ap



POLICE_REGIONS = [
    ("GP00", "National HQ, Accra - Cantonment"),
    ("Greater Accra Regional Police Command - Nima, Accra","Greater Accra Regional Police Command - Nima, Accra"),
    ("GP0010", "Central North Regional Police Command - Assin Fosu"),
    ("GP0011", "Tema Regional Police Command - Tema"),
    ("GP0012", "Eastern Regional Police Command - Koforidua"),
    ("GP0013", "Eastern North Regional Police Command - Mpraeso"),
    ("GP0014", "Eastern South Regional Police Command - Kibi"),
    ("GP0015", "Northern Regional Police Command - Tamale"),
    ("GP0016", "North-East Regional Police Command - Nalerigu"),
    ("GP0017", "Savannah Regional Police Command - Damongo"),
    ("GP0018", "Upper East Regional Police Command - Bolgatanga"),
    ("GP0019", "Upper West Regional Police Command - Wa"),
    ("GP002", "Ashanti Regional Police Command - Kumasi"),
    ("GP0020", "Volta Regional Police Command - Ho"),
    ("GP0021", "Volta North Regional Police Command - Hohoe"),
    ("GP0022", "Oti Regional Police Command - Dambai"),
    ("GP0023", "Western Regional Police Command - Takoradi"),
    ("GP0024", "Western Central Regional Police Command - Tarkwa"),
    ("GP0025", "Western North Regional Police Command - Sefwi Wiawso"),
    ("GP003", "Ashanti North Regional Police Command - Mampong"),
    ("GP004", "Ashanti South Regional Police Command - Bekwai"),
    ("GP005", "Ahafo Regional Police Command - Goaso"),
    ("GP006", "Bono Regional Police Command - Sunyani"),
    ("GP007", "Bono East Regional Police Command - Techiman"),
    ("GP008", "Central Regional Police Command - Cape Coast"),
    ("GP009", "Central East Regional Police Command - Kasoa"),
]



SERVICES_CHOICES = [

    ('GPS', 'Ghana Police Service (GPS)'),('PS', 'Prisons Service (PS)'),
    ('GNFS', 'Ghana National Fire Service(GNFS) )'),('GIS', 'Ghana Immigration Service (GIS)'),
    ('GHS', 'Ghana Health Service (GHS)'),('GMF', 'Ghana Medical Facility (GMF)')]


# Service Data Model
class Service(models.Model):
    name = models.CharField(max_length=255, choices=SERVICES_CHOICES,unique=True)
    #name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name

# Police Regional Data Model
''''class PoliceRegion(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='region')    
    name = models.CharField(max_length=255, unique=True,choices=POLICE_REGIONS)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name'''

def form_valid(self, form):
    print("Form data:", form.cleaned_data)  # Debug line
    # ... rest of your code



class PoliceRegion(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE,  null=False, related_name='region')    
    name = models.CharField(max_length=255, unique=True, choices=POLICE_REGIONS)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.code} - {dict(POLICE_REGIONS).get(self.code, self.name)}"


class Division(models.Model):
    police_region = models.ForeignKey(PoliceRegion, on_delete=models.CASCADE, related_name='divisions')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.police_region.name} - {self.name}"

class District(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.division.name} - {self.name}"

class PoliceStation(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='stations')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    

    def get_full_hierarchy(self):
        return {
            'station': self.name,
            'district': self.district.name,
            'division': self.district.division.name,
            'region': self.district.division.police_region.name
        }

    def __str__(self):
        return f"{self.district.name} - {self.name}"







# models.py
from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import Region, MMDA, AREA_ZONE_CHOICES

# Helper function for serial generation
def generate_service_serial_number(category):
    """
    Generate unique serial numbers in format: [PREFIX][YYMMDD][0001]
    - GPS: Ghana Police Service
    - GFS: Ghana Fire Station
    - FH: Fire Hydrant
    - GMF: Ghana Medical Facility
    """
    date_str = timezone.now().strftime('%y%m%d')  # YYMMDD format
    prefix_map = {
        'GhanaPoliceService': 'GPS',
        'GhanaFireStation': 'GFS',
        'firehydrant': 'FH',
        'ghmedicalfacility': 'GMF'
    }
    
    with transaction.atomic():
        # Get current count for the category
        if category == 'GhanaPoliceService':
            count = GhanaPoliceService.objects.count() + 1
        elif category == 'GhanaFireStation':
            count = GhanaFireStation.objects.count() + 1
        elif category == 'firehydrant':
            count = firehydrant.objects.count() + 1
        elif category == 'ghmedicalfacility':
            count = ghmedicalfacility.objects.count() + 1
        else:
            raise ValueError("Invalid service category")

        prefix = prefix_map[category]
        serial_number = f"{prefix}{date_str}{count:04d}"
        
        # Ensure global uniqueness across all models
        while (GhanaPoliceService.objects.filter(serial_number=serial_number).exists() or
               GhanaFireStation.objects.filter(serial_number=serial_number).exists() or
               firehydrant.objects.filter(serial_number=serial_number).exists() or 
               ghmedicalfacility.objects.filter(serial_number=serial_number).exists()):
            count += 1
            serial_number = f"{prefix}{date_str}{count:04d}"
    
    return serial_number



# Ghana Police Service Model
class GhanaPoliceService(models.Model):
    serial_number = models.CharField(
        max_length=15, 
        unique=True,
        editable=False,
        help_text="Auto-generated: GPSyymmddXXXX"
    )
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    police_region = models.ForeignKey(PoliceRegion, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    mmda = models.ForeignKey(MMDA, on_delete=models.CASCADE, related_name="police")  # MMDA Reference
    station = models.ForeignKey(PoliceStation, on_delete=models.CASCADE)
    gps_location = models.CharField(max_length=255)
    geo_coordinate = models.CharField(max_length=255)
    area_name = models.CharField(max_length=255)
    area_zone = models.CharField(max_length=255)
    contact = models.CharField(max_length=15)
    additional_contact = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    description = models.TextField()
    landmark = models.CharField(max_length=255, blank=True, null=True)
    road_network = models.CharField(max_length=255)
    nature_of_building = models.CharField(max_length=10, choices=[('Good', 'Good'), ('Moderate', 'Moderate'), ('Bad', 'Bad')])
    cell_type = models.CharField(max_length=30, choices=[('Female Only', 'Female Only'), ('Male Only', 'Male Only'), ('Both', 'Both')])
    crime_rate = models.IntegerField()
    nature_of_crime = models.CharField(max_length=255)
    image1 = models.ImageField(upload_to='gps_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='gps_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='gps_images/', blank=True, null=True)
    image4 = models.ImageField(upload_to='gps_images/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='gps_created')
    date_created = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='gps_updated')
    date_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number = generate_service_serial_number('GhanaPoliceService')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.station.name} - {self.area_name}"



#signals
# models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SignalMessage(models.Model):

    PRIORITY_CHOICES = [
        ('HIGH', 'High Classified'),
        ('MODERATE', 'Moderate'),
        ('NORMAL', 'Normal'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
    ]

    # Sender Information
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_signals')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_signals')
    
    # Recipient Hierarchy
    '''regions = models.ManyToManyField(PoliceRegion, blank=True, related_name='region_signals')
    divisions = models.ManyToManyField(Division, blank=True, related_name='division_signals')
    districts = models.ManyToManyField(District, blank=True, related_name='district_signals')
    stations = models.ManyToManyField(PoliceStation, blank=True, related_name='station_signals')'''
    
    '''regions = models.ForeignKey(PoliceRegion, null=True, on_delete=models.SET_NULL)
    divisions = models.ForeignKey(Division, null=True, on_delete=models.SET_NULL)
    districts = models.ForeignKey(District, null=True, on_delete=models.SET_NULL)
    stations = models.ForeignKey(PoliceStation, null=True, on_delete=models.SET_NULL)'''


class SignalMessage(models.Model):
    PRIORITY_CHOICES = [
        ('HIGH', 'High Classified'),
        ('MODERITY', 'Moderate'),
        ('NORMAL', 'Normal'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
    ]

    # Sender Information
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_signals')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_signals')
    
    # Recipient Hierarchy
    police_region = models.ForeignKey(PoliceRegion, null=True, blank=True, on_delete=models.SET_NULL)
    division = models.ForeignKey(Division, null=True, blank=True, on_delete=models.SET_NULL)
    district = models.ForeignKey(District, null=True, blank=True, on_delete=models.SET_NULL)
    station = models.ForeignKey(PoliceStation, null=True, blank=True, on_delete=models.SET_NULL)

    # Message Content
    subject = models.CharField(max_length=255)
    content = models.TextField()
    priority = models.CharField(max_length=30, choices=PRIORITY_CHOICES, default='NORMAL')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DRAFT')
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_report = models.OneToOneField('DeliveryReport', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.subject} - {self.get_priority_display()}"

class DeliveryReport(models.Model):
    message = models.ForeignKey(SignalMessage, on_delete=models.CASCADE, related_name='reports')
    recipient_unit = models.ForeignKey(PoliceRegion, on_delete=models.CASCADE)  # Can be any hierarchy level
    received_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('message', 'recipient_unit')

    def __str__(self):
        return f"Report for {self.message.subject} - {self.recipient_unit}"





# Regional Data Model


class FireStation(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='stations')
    mmda = models.ForeignKey(MMDA, on_delete=models.CASCADE, related_name="FireStation")  # MMDA Reference
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.region.name} - {self.name}"

# Ghana Fire Service Model
class GhanaFireStation(models.Model):

    serial_number = models.CharField(
        max_length=15, 
        unique=True,
        editable=False,
        help_text="Auto-generated: GFSyymmddXXXX"
        )

    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    mmda = models.ForeignKey(MMDA, on_delete=models.CASCADE, related_name="gnfs")  # MMDA Reference
    #division = models.ForeignKey(Division, on_delete=models.CASCADE)
    #district = models.ForeignKey(District, on_delete=models.CASCADE)
    fire_station = models.ForeignKey(FireStation, on_delete=models.CASCADE)
    gps_location = models.CharField(max_length=255)
    geo_coordinate = models.CharField(max_length=255)
    area_name = models.CharField(max_length=255)
    area_zone = models.CharField(max_length=100, choices=AREA_ZONE_CHOICES)
    contact = models.CharField(max_length=15)
    additional_contact = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    description = models.TextField()
    landmark = models.CharField(max_length=255, blank=True, null=True)
    road_network = models.CharField(max_length=255)
    nature_of_building = models.CharField(max_length=10, choices=[('Good', 'Good'), ('Moderate', 'Moderate'), ('Bad', 'Bad')])
    accessibility_of_hydrant= models.CharField(max_length=30, choices=[('Difficult', 'Difficult'), ('Easy', 'Easy'), ('Encouraged', 'Encouraged')])
    station_picture_1 = models.ImageField(upload_to='gps_images/', blank=True, null=True)
    station_picture_2 = models.ImageField(upload_to='gps_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='gps_images/', blank=True, null=True)
    image4 = models.ImageField(upload_to='gps_images/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='gnfs_created')
    date_created = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='gnfs_updated')
    date_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number = generate_service_serial_number('GhanaFireStation')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fire_station} - {self.area_name}"



# Ghana Fire Service Model
class firehydrant(models.Model):
    serial_number = models.CharField(
        max_length=15, 
        unique=True,
        editable=False,
        help_text="Auto-generated: FHyymmddXXXX"
    )
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    mmda = models.ForeignKey(MMDA, on_delete=models.CASCADE, related_name="hydrants")  # MMDA Reference  
    station = models.ForeignKey(FireStation, on_delete=models.CASCADE)
    firehydrant_name= models.CharField(max_length=255)
    gps_location = models.CharField(max_length=255)
    geo_coordinate = models.CharField(max_length=255)
    area_name = models.CharField(max_length=255)
    area_zone = models.CharField(max_length=100, choices=AREA_ZONE_CHOICES)
    contact = models.CharField(max_length=15)
    additional_contact = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    description_of_hydrant = models.TextField()
    landmark = models.CharField(max_length=255, blank=True, null=True)
    road_network = models.CharField(max_length=255)
    nature_of_firehydrant= models.CharField(max_length=10, choices=[('Good', 'Good'), ('Moderate', 'Moderate'), ('Bad', 'Bad')])
    Accessibility_of_hydrant= models.CharField(max_length=30, choices=[('Difficult', 'Difficult'), ('Easy', 'Easy'), ('Encouraged', 'Encouraged')])
    hydrant_picture_1= models.ImageField(upload_to='hydrants_images/', blank=True, null=True)
    hydrant_picture_2= models.ImageField(upload_to='hydrants_images/', blank=True, null=True)
    area_view_3 = models.ImageField(upload_to='hydrants_images/', blank=True, null=True)
    area_view_4 = models.ImageField(upload_to='hydrants_images/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='gnfs_hydrants_created')
    date_created = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='gnfs_hydrants_updated')
    date_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number = generate_service_serial_number('firehydrant')
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.firehydrant_name} - {self.area_name}"



# Ghana Fire Service Model
class ghmedicalfacility(models.Model):
    serial_number = models.CharField(
        max_length=15, 
        unique=True,
        editable=False,
        help_text="Auto-generated: GMFyymmddXXXX"
    )

    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    mmda = models.ForeignKey(MMDA, on_delete=models.CASCADE, related_name="medicalfacility")  # MMDA Reference  
    facility_name = models.ForeignKey(FireStation, on_delete=models.CASCADE)
    type_facility= models.CharField(max_length=30, choices=[('Chip Compound', 'Chip Compound'),('Clinic', 'Clinic'),('Hospital', 'Hospital'), ('Maternity Home', 'Maternity Home'),('Pharmarcy', 'Pharmarcy'),('other', 'other')])
    ambulance = models.BooleanField(default=False)
    number_of_beds = models.PositiveIntegerField()
    average_daily_admission = models.FloatField(default=0.0, help_text="Average number of daily admissions.")
    nature_ownership = models.CharField(max_length=100, choices=NATURE_CHOICES)
    gps_location = models.CharField(max_length=255)
    geo_coordinate = models.CharField(max_length=255)
    area_name = models.CharField(max_length=255)
    area_zone = models.CharField(max_length=255)
    contact = models.CharField(max_length=15)
    additional_contact = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    description_of_facility = models.TextField()
    landmark = models.CharField(max_length=255, blank=True, null=True)
    road_network = models.CharField(max_length=255)
    Accessibility_of_facility= models.CharField(max_length=30, choices=[('Difficult', 'Difficult'), ('Easy', 'Easy'), ('Encouraged', 'Encouraged')])
    nature_of_building = models.CharField(max_length=10, choices=[('Good', 'Good'), ('Moderate', 'Moderate'), ('Bad', 'Bad')])
    facility_picture_1 = models.ImageField(upload_to='ghis_images/', blank=True, null=True)
    facility_picture_2= models.ImageField(upload_to='ghis_images/', blank=True, null=True)
    area_view_3 = models.ImageField(upload_to='ghis_images/', blank=True, null=True)
    area_view_3 = models.ImageField(upload_to='ghis_images/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ghis_created')
    date_created = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ghis_updated')
    date_updated = models.DateTimeField(auto_now=True)



    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number = generate_service_serial_number('ghmedicalfacility')
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.facility_name} - {self.area_name}"
