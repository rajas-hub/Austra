# Generated by Django 4.2.17 on 2025-01-07 13:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('medicliq_payment', '0003_payments_transaction'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Payments',
        ),
    ]
