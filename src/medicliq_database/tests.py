from django.test import TestCase
from .models import Medicine, Prescription
from django.urls import reverse
from datetime import date

class paymentTestCase(TestCase):
    def setUp(self):
        # Create a medicine with an initial quantity
        self.medicine = Medicine.objects.create(name="Aspirin", quantity_available=10,price_per_unit=5.00,expiration_date=date(2025, 12, 31))
        # Create a prescription for the medicine
        self.prescription = Prescription.objects.create(medicine=self.medicine, quantity=5)

    def test_payment_success(self):
        # Mock a successful payment
        response = self.client.post(reverse('payment', kwargs={'prescription_id': self.prescription.id}), data={'payment_status': 'success'})

        # Check if the stock was updated
        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.quantity, 5)  # Stock should be reduced by 5

        # Check for a successful response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment successful')

    def test_payment_insufficient_stock(self):
        # Create a prescription for more quantity than available in stock
        self.prescription.quantity = 20
        self.prescription.save()

        response = self.client.post(reverse('payment', kwargs={'prescription_id': self.prescription.id}), data={'payment_status': 'success'})

        # Ensure stock remains unchanged
        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.quantity, 10)  # Stock should not change due to insufficient stock

        # Check for an error message
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Insufficient stock')

    def test_payment_payment_failed(self):
        # Mock a failed payment
        response = self.client.post(reverse('payment', kwargs={'prescription_id': self.prescription.id}), data={'payment_status': 'failed'})

        # Ensure stock remains unchanged
        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.quantity, 10)  # Stock should remain unchanged due to payment failure

        # Check for an error message
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Payment failed')
