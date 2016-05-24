from django import forms
from .models import SharedZone
from utils.utilities import is_empty


class SharedZoneForm(forms.ModelForm):
    class Meta:
        model = SharedZone
        fields = ['name', 'address', 'description']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control resize-text-area-none'}),
            'address': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_name(self):
        if is_empty(self.cleaned_data["name"]):
            raise forms.ValidationError("Invalid name.")
        return self.cleaned_data['name']

    def clean_description(self):
        if is_empty(self.cleaned_data["description"]):
            raise forms.ValidationError("Invalid description.")
        return self.cleaned_data['description']

    def clean_address(self):
        if is_empty(self.cleaned_data["address"]):
            raise forms.ValidationError("Invalid address.")
        return self.cleaned_data['address']

    def __init__(self, *args, **kwargs):
        super(SharedZoneForm, self).__init__(*args, **kwargs)
        self.fields['address'].label = "Community Shed Address"