from django import forms
from medicliq_database.models import Payment
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
class medicinePaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        exclude = ['payment_date_time','ispaid']  # Exclude the non-editable field
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper=FormHelper(self)
        self.helper.layout = Layout(
        
            Row(
                Column('amount_paid', css_class='form-group col-md-6 mb-0'),
                Column('payment_method', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            Submit('submit','Go To Payment', css_class='btn btn-primary')  # Add a submit button
        )