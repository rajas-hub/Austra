# Generated by Django 5.1.3 on 2025-02-25 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicliq_database', '0007_payment_razorpay_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='medshelfmapper',
            name='strip_size',
            field=models.PositiveIntegerField(default=5),
            preserve_default=False,
        ),
    ]
