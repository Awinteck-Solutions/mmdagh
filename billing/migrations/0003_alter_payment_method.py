# Generated by Django 5.1.6 on 2025-04-12 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_payment_dr_account_payment_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='method',
            field=models.CharField(choices=[('cash', 'Cash'), ('mobile_money', 'Mobile Money'), ('bank_transfer', 'Bank Transfer')], default='cash', max_length=20),
        ),
    ]
