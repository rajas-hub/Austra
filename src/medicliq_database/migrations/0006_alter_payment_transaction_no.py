# Generated by Django 4.2.17 on 2025-01-07 19:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('medicliq_database', '0005_remove_payment_payment_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='transaction_no',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='medicliq_database.transaction'),
        ),
    ]
