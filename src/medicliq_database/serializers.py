from rest_framework import serializers
from .models import Patient, Medicine

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

class paymentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()
    medicine = MedicineSerializer()

    class Meta:
        model = payment
        fields = '__all__'

    # Optional: Custom validation for the payment, e.g., checking if stock is available
    def validate(self, data):
        medicine = data['medicine']
        quantity = data['quantity']
        if medicine.quantity_available < quantity:
            raise serializers.ValidationError("Not enough stock available.")
        return data
