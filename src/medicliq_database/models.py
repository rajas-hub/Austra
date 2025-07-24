from django.db import models
from datetime import date
# Patient Model


from django.db import models

class Payment(models.Model):
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    cart_data = models.JSONField(default=dict)  # Add this line
    ispaid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - ₹{self.amount_paid}"
    
    
class Patient(models.Model):
    mobno = models.CharField(max_length=15, default='UNKNOWN')  # or any other default value you prefer
    name = models.CharField(max_length=100)
    email = models.EmailField()
    age = models.PositiveIntegerField(default=25)
    gender = models.CharField(max_length=10,default='Not Specified')
    address = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# Doctor Model
class Doctor(models.Model):
    doc_id = models.AutoField(primary_key=True)  # Auto-generated unique doctor ID
    doc_name = models.CharField(max_length=100)
    doc_mob_no = models.CharField(max_length=15)
    signature = models.ImageField(upload_to='signatures/')
    specialization = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.doc_name
    
# MedShelfMapper Model (Replaces Medicine table)
from django.db import models, transaction

class MedShelfMapper(models.Model):
    shelfno = models.CharField(max_length=10, primary_key=True)  # Unique shelf number
    medname = models.CharField(max_length=100)
    avail_quantity = models.PositiveIntegerField()  # Total available units (not strips)
    strip_size = models.PositiveIntegerField()  # Number of units per strip
    price_per_unit = models.FloatField()

    def __str__(self):
        return f"{self.medname} - Shelf {self.shelfno}"

    def dispense_medicine(self, num_strips):
        """
        Dispenses the medicine based on the number of strips requested.
        Automatically reduces `avail_quantity` accordingly.
        """
        units_to_dispense = num_strips * self.strip_size  # Convert strips to units
        if units_to_dispense > self.avail_quantity:
            raise ValueError("Not enough stock available!")

        # Atomic transaction to ensure data integrity
        with transaction.atomic():
            self.avail_quantity -= units_to_dispense
            self.save()  # Save the updated quantity

        return f"Dispensed {num_strips} strips ({units_to_dispense} units) of {self.medname}"


# track stock additions and deductions
class StockMovement(models.Model):
    movement_id = models.AutoField(primary_key=True)  # Unique identifier for the stock movement
    shelfno = models.ForeignKey(MedShelfMapper, on_delete=models.CASCADE)  # Medicine shelf number
    movement_type = models.CharField(
        max_length=20,
        choices=[('Addition', 'Addition'), ('Deduction', 'Deduction')],
        default='Deduction'
    )  # Type of movement (addition or deduction)
    quantity = models.PositiveIntegerField()  # Quantity added or deducted
    movement_date_time = models.DateTimeField(auto_now_add=True)  # Date and time of the movement
    reason = models.TextField(blank=True, null=True)  # Reason for stock change (e.g., restocking, sale, etc.)

    def __str__(self):
        return f"{self.movement_type} of {self.quantity} units from {self.shelfno}"

# to store scanned prescription data    
class ScannedPrescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,default=1)  # Default to patient with ID 1
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    prescription_image = models.ImageField(upload_to='scanned_prescriptions/')
    extracted_data = models.JSONField()  # To store parsed data like medicine, dosage, etc.
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scanned Prescription for {self.patient.name}"

# This table will track detailed prescriptions for a patient. It links scanned prescriptions with actual medicines and quantities
class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, default=1)  # Default to doctor with ID 1
    medicines = models.ManyToManyField(
        MedShelfMapper,
        through='PrescriptionMedicine',
        related_name='prescriptions'
    )
    date_prescribed = models.DateField(auto_now_add=True)
    scanned_prescription = models.OneToOneField(ScannedPrescription, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"Prescription for {self.patient.name}"

# Tracks medicine quantities prescribed per prescription.
class PrescriptionMedicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    medicine = models.ForeignKey(MedShelfMapper, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.medicine.medname} x {self.quantity} for {self.prescription}"

# Transaction Table
class Transaction(models.Model):
    transaction_no = models.AutoField(primary_key=True, default=1)  # Default value for existing rows
    patient_mob_no = models.ForeignKey(Patient, on_delete=models.CASCADE, default=1)  # Added default for migration
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, default=1)  # Default to doctor with ID 1
    transaction_date_time = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_status = models.CharField(
        max_length=20,
        choices=[('Completed', 'Completed'), ('Pending', 'Pending'), ('Failed', 'Failed')],
        default='Pending'
    )
    prescription = models.ImageField(upload_to='prescriptions/', blank=True, null=True)
    medicines_dispensed = models.JSONField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.transaction_no} - {self.transaction_status}"

# Payment Table
class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    transaction_no = models.ForeignKey(Transaction, null=True, on_delete=models.SET_NULL)  # ForeignKey to Transaction
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)  # Add razorpay_order_id field
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    ispaid = models.BooleanField(default=False)
    payment_date_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment {self.payment_id} - Paid: {self.ispaid}"
    
class tentrans(models.Model):
    srno= models.IntegerField(default=0)
    payment_id = models.CharField(max_length=100, unique=True, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    time_date = models.DateTimeField(auto_now_add=True)
    medastock= models.IntegerField(default=0)
    medbstock= models.IntegerField(default=0)
    medcstock= models.IntegerField(default=0)
    meddstock= models.IntegerField(default=0)
    medestock= models.IntegerField(default=0)
    medfstock= models.IntegerField(default=0)
    medgstock= models.IntegerField(default=0)
    medhstock= models.IntegerField(default=0)


