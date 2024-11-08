# user_management/forms.py
from django import forms

class PurchaseForm(forms.Form):
    unique_id = forms.CharField(max_length=12)
    bottle_count = forms.IntegerField(min_value=1, max_value=3)
