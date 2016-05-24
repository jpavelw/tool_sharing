from django import forms
from .models import User
from utils.utilities import check_password, is_number, contains_number, is_empty, contains_space


class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(label='Confirm password', max_length=30, widget=forms.PasswordInput(attrs={
        'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'phone_number', 'password', 'confirm_password',
                  'address', 'state', 'city', 'zipcode']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "your@mail.com"}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ex.: 2225559988"}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ex.: 12345"}),
        }

    def clean_first_name(self):
        if contains_number(self.cleaned_data['first_name']) or is_empty(self.cleaned_data["first_name"]):
            raise forms.ValidationError("Invalid first name.")
        return self.cleaned_data["first_name"]

    def clean_middle_name(self):
        if contains_number(self.cleaned_data['middle_name']) or (self.cleaned_data['middle_name'] != "" and is_empty(self.cleaned_data["middle_name"])):
            raise forms.ValidationError("Invalid middle name.")
        return self.cleaned_data["middle_name"]

    def clean_last_name(self):
        if contains_number(self.cleaned_data['last_name']) or is_empty(self.cleaned_data["last_name"]):
            raise forms.ValidationError("Invalid last name.")
        return self.cleaned_data["last_name"]

    def clean_email(self):
        return self.cleaned_data["email"]

    def clean_phone_number(self):
        if not is_number(self.cleaned_data["phone_number"]) or len(str(self.cleaned_data["phone_number"])) < 10:
            raise forms.ValidationError("Invalid phone number.")
        return self.cleaned_data["phone_number"]

    def clean_password(self):
        if len(str(self.cleaned_data["password"])) < 3 or contains_space(self.cleaned_data["password"]):
            raise forms.ValidationError("Invalid password.")
        return self.cleaned_data["password"]

    def clean_confirm_password(self):
        if not self.cleaned_data["password"] == self.cleaned_data["confirm_password"]:
            raise forms.ValidationError("Passwords do not match.")
        return self.cleaned_data["confirm_password"]

    def clean_address(self):
        if is_empty(self.cleaned_data["address"]):
            raise forms.ValidationError("Invalid address.")
        return self.cleaned_data["address"]

    def clean_state(self):
        return self.cleaned_data["state"]

    def clean_city(self):
        if contains_number(self.cleaned_data['city']) or is_empty(self.cleaned_data["city"]):
            raise forms.ValidationError("Invalid city name.")
        return self.cleaned_data["city"]

    def clean_zipcode(self):
        if not is_number(self.cleaned_data["zipcode"]) or not len(str(self.cleaned_data["zipcode"])) == 5:
            raise forms.ValidationError("Invalid zip code.")
        return self.cleaned_data["zipcode"]


class LogInForm(forms.Form):
    email = forms.EmailField(label='', max_length=30, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': "Email address", 'autofocus': "true"}))
    password = forms.CharField(label='', max_length=30,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Password"}))

    def clean_email(self):
        if not User.objects.filter(email=self.cleaned_data["email"]).exists():
            raise forms.ValidationError("User does not exist.")
        return self.cleaned_data["email"]

    def clean_password(self):
        if "email" in self.cleaned_data:
            if User.objects.filter(email=self.cleaned_data["email"], enabled=1).exists():
                user = User.objects.get(email=self.cleaned_data["email"], enabled=1)
                if not check_password(user.password, self.cleaned_data["password"]):
                    raise forms.ValidationError("Invalid password.")
        return self.cleaned_data["password"]


class UpdateProfileForm(forms.ModelForm):
    confirm_password = forms.CharField(label='Enter password to confirm changes', max_length=30,
                                       widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'phone_number', 'address', 'state',
                  'city', 'zipcode', 'confirm_password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "your@mail.com"}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ex.: 2225559988"}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ex.: 12345"}),
        }

    def clean_first_name(self):
        if contains_number(self.cleaned_data['first_name']) or is_empty(self.cleaned_data["first_name"]):
            raise forms.ValidationError("Invalid first name.")
        return self.cleaned_data["first_name"]

    def clean_middle_name(self):
        if contains_number(self.cleaned_data['middle_name']) or (self.cleaned_data['middle_name'] != "" and is_empty(self.cleaned_data["middle_name"])):
            raise forms.ValidationError("Invalid middle name.")
        return self.cleaned_data["middle_name"]

    def clean_last_name(self):
        if contains_number(self.cleaned_data['last_name']) or is_empty(self.cleaned_data["last_name"]):
            raise forms.ValidationError("Invalid last name.")
        return self.cleaned_data["last_name"]

    def clean_email(self):
        return self.cleaned_data["email"]

    def clean_phone_number(self):
        if not is_number(self.cleaned_data["phone_number"]) or len(str(self.cleaned_data["phone_number"])) < 10:
            raise forms.ValidationError("Invalid phone number.")
        return self.cleaned_data["phone_number"]

    def clean_address(self):
        if is_empty(self.cleaned_data["address"]):
            raise forms.ValidationError("Invalid address.")
        return self.cleaned_data["address"]

    def clean_state(self):
        return self.cleaned_data["state"]

    def clean_city(self):
        if contains_number(self.cleaned_data['city']):
            raise forms.ValidationError("Invalid city name")
        return self.cleaned_data["city"]

    def clean_zipcode(self):
        if not is_number(self.cleaned_data["zipcode"]) or not len(str(self.cleaned_data["zipcode"])) == 5:
            raise forms.ValidationError("Invalid zip code.")
        return self.cleaned_data["zipcode"]

    def clean_confirm_password(self):
        if self.instance:
            if not check_password(self.instance.password, self.cleaned_data["confirm_password"]):
                raise forms.ValidationError("Invalid password.")
        return self.cleaned_data["confirm_password"]


class UpdatePasswordForm(forms.Form):
    current_password = None
    password = forms.CharField(label='', max_length=30, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': "Current password", 'autofocus': "true"}))
    new_password = forms.CharField(label='', max_length=30, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': "New password"}))
    confirm_password = forms.CharField(label='', max_length=30, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': "Confirm new password"}))

    def clean_password(self):
        if self.current_password is not None:
            if not check_password(self.current_password, self.cleaned_data["password"]):
                raise forms.ValidationError("Invalid password.")
            else:
                return self.cleaned_data["password"]
        raise forms.ValidationError("Password not provided.")

    def clean_new_password(self):
        if len(str(self.cleaned_data["new_password"])) < 3 or contains_space(self.cleaned_data["new_password"]):
            raise forms.ValidationError("Invalid password.")
        return self.cleaned_data["new_password"]

    def clean_confirm_password(self):
        if "password" in self.cleaned_data:
            if not (self.cleaned_data["confirm_password"] == self.cleaned_data["new_password"]):
                raise forms.ValidationError("Passwords must match.")
            else:
                return self.cleaned_data["confirm_password"]

    def set_current_password(self, current_password):
        self.current_password = current_password


class PickupArrangementForm(forms.Form):
    DAYS = (('Monday', 'Monday'),
            ('Tuesday', 'Tuesday'),
            ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'),
            ('Friday', 'Friday'),
            ('Saturday', 'Saturday'),
            ('Sunday', 'Sunday'))

    days = forms.MultipleChoiceField(choices=DAYS)
    time_from = forms.CharField(max_length=25)
    time_to = forms.CharField(max_length=25)

    def clean(self):
        time_from = self.cleaned_data.get('time_from')
        time_to = self.cleaned_data.get('time_to')

        if time_from is None or time_to is None:
            raise forms.ValidationError("Please provide time information")

        time_from = int(time_from.replace(":", ""))
        time_to = int(time_to.replace(":", ""))

        if time_from > time_to:
            raise forms.ValidationError("Invalid time range")

        return True

    def week_days(self):
        days = []
        for day in self.DAYS:
            days.append(day[0])

        return days


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='', max_length=30, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': "Email address", 'autofocus': "true"}))

    def clean_email(self):
        if not User.objects.filter(email=self.cleaned_data["email"]).exists():
            raise forms.ValidationError("User does not exist.")
        return self.cleaned_data["email"]
