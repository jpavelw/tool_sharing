import string
import random
from django import forms
from .models import Tool
from utils.utilities import is_empty


class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = ['name', 'status', 'shared_from', 'category', 'description', 'picture']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'shared_from': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control resize-text-area-none'}),
            'picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

    '''def clean_id(self):
        return self.cleaned_data["id"]'''

    def clean_name(self):
        if is_empty(self.cleaned_data["name"]):
            raise forms.ValidationError("Invalid name.")
        return self.cleaned_data["name"]

    def clean_status(self):
        return self.cleaned_data["status"]

    def clean_description(self):
        if is_empty(self.cleaned_data["description"]):
            raise forms.ValidationError("Invalid description.")
        return self.cleaned_data["description"]

    def clean_is_shared_from_home(self):
        return self.cleaned_data["is_shared_from_home"]

    def clean_category(self):
        return self.cleaned_data["category"]

    def clean_picture(self):
        if 'picture' in self.cleaned_data:
            file_name = str(self.cleaned_data['picture']).lower()
            file_parts = file_name.split(".")
            if not file_parts[-1] in ['jpeg', 'png', 'bmp', 'gif', 'jpg']:
                raise forms.ValidationError("Invalid image format.")
            try:
                if self.cleaned_data['picture'].size > 3*1024*1024:
                    raise forms.ValidationError("Image file too large (> 3MB).")
            except AttributeError:
                pass
        return self.cleaned_data["picture"]

    def set_owner(self, owner):
        self.instance.owner = owner

    def generate_code(self):
        while True:
            new_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            try:
                Tool.objects.get(code=new_code)
            except:
                self.instance.code = new_code
                break
