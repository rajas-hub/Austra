from django import forms
from .models import Patient, MedShelfMapper, Doctor, ScannedPrescription, Prescription, PrescriptionMedicine
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'gender', 'address', 'mobno', 'email', 'medical_history']

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['doc_name', 'doc_mob_no', 'signature', 'specialization']

class ScannedPrescriptionForm(forms.ModelForm):
    class Meta:
        model = ScannedPrescription
        fields = ['patient', 'doctor', 'prescription_image', 'extracted_data']

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient', 'doctor', 'scanned_prescription']

class PrescriptionMedicineForm(forms.ModelForm):
    class Meta:
        model = PrescriptionMedicine
        fields = ['prescription', 'medicine', 'quantity']

class MedShelfMapperForm(forms.ModelForm):
    class Meta:
        model = MedShelfMapper
        fields = ['shelfno', 'medname', 'avail_quantity', 'price_per_unit']
