# Generated by Django 5.1.6 on 2025-04-12 02:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_alter_ghmedicalfacility_type_facility'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('received_at', models.DateTimeField(auto_now_add=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('recipient_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.policeregion')),
            ],
        ),
        migrations.CreateModel(
            name='SignalMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('priority', models.CharField(choices=[('HIGH', 'High Classified'), ('MODERATE', 'Moderate'), ('NORMAL', 'Normal')], default='NORMAL', max_length=10)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('SENT', 'Sent'), ('DELIVERED', 'Delivered'), ('READ', 'Read')], default='DRAFT', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('delivery_report', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.deliveryreport')),
                ('districts', models.ManyToManyField(blank=True, related_name='district_signals', to='services.district')),
                ('divisions', models.ManyToManyField(blank=True, related_name='division_signals', to='services.division')),
                ('regions', models.ManyToManyField(blank=True, related_name='region_signals', to='services.policeregion')),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_signals', to=settings.AUTH_USER_MODEL)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_signals', to='services.service')),
                ('stations', models.ManyToManyField(blank=True, related_name='station_signals', to='services.policestation')),
            ],
        ),
        migrations.AddField(
            model_name='deliveryreport',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='services.signalmessage'),
        ),
        migrations.AlterUniqueTogether(
            name='deliveryreport',
            unique_together={('message', 'recipient_unit')},
        ),
    ]
