# /databse/admin.py file
from django.contrib import admin
from .models import Patient, Doctor, MedShelfMapper, StockMovement, ScannedPrescription, Prescription,tentrans, PrescriptionMedicine, Transaction, Payment

admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(MedShelfMapper)
admin.site.register(StockMovement)
admin.site.register(ScannedPrescription)
admin.site.register(Prescription)
admin.site.register(PrescriptionMedicine)
admin.site.register(Transaction)
admin.site.register(Payment)
admin.site.register(tentrans)
