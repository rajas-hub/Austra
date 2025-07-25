# Generated by Django 4.2.17 on 2025-01-07 09:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medicliq_database', '0003_doctor_medshelfmapper_payment_prescriptionmedicine_and_more'),
        ('medicliq_payment', '0002_payments_delete_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='payments',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='medicliq_database.transaction'),
        ),
    ]
