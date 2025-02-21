from django import forms
from .models import ContractorProfile

class ContractorProfileForm(forms.ModelForm):
    class Meta:
        model = ContractorProfile
        fields = ['full_name', 'contact', 'specialization', 'work_radius', 'documents'] 