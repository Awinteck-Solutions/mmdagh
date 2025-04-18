# Generated by Django 5.1.6 on 2025-04-07 22:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('services', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ghmedicalfacility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(editable=False, help_text='Auto-generated: GMFyymmddXXXX', max_length=15, unique=True)),
                ('type_facility', models.CharField(choices=[('Chip Compound', 'Chip Compound'), ('Hospital', 'Hospital'), ('Vertinary', 'Vertnary')], max_length=30)),
                ('ambulance', models.BooleanField(default=False)),
                ('number_of_beds', models.PositiveIntegerField()),
                ('average_daily_admission', models.FloatField(default=0.0, help_text='Average number of daily admissions.')),
                ('nature_ownership', models.CharField(choices=[('Govt', 'Govt'), ('Private', 'Private'), ('Govt/Private', 'Govt/Private'), ('Religious', 'Religious')], max_length=100)),
                ('gps_location', models.CharField(max_length=255)),
                ('geo_coordinate', models.CharField(max_length=255)),
                ('area_name', models.CharField(max_length=255)),
                ('area_zone', models.CharField(max_length=255)),
                ('contact', models.CharField(max_length=15)),
                ('additional_contact', models.CharField(blank=True, max_length=15, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('description_of_facility', models.TextField()),
                ('landmark', models.CharField(blank=True, max_length=255, null=True)),
                ('road_network', models.CharField(max_length=255)),
                ('nature_of_building', models.CharField(choices=[('Good', 'Good'), ('Moderate', 'Moderate'), ('Bad', 'Bad')], max_length=10)),
                ('facility_picture_1', models.ImageField(blank=True, null=True, upload_to='ghis_images/')),
                ('facility_picture_2', models.ImageField(blank=True, null=True, upload_to='ghis_images/')),
                ('area_view_3', models.ImageField(blank=True, null=True, upload_to='ghis_images/')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ghis_created', to=settings.AUTH_USER_MODEL)),
                ('facility_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.firestation')),
                ('mmda', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medicalfacility', to='accounts.mmda')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.region')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ghis_updated', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Ghis',
        ),
    ]
