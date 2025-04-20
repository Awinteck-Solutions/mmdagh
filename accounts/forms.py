from django import forms
from .models import DataCapture, EducationCapture, ResidentialCapture, HealthCapture, GovernmentCapture, SMECapture, UserAssignment, Region, MMDA
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)

class ContactForm(forms.Form):
    message_name = forms.CharField(
        label='Full Name',
        max_length=100,
        widget=forms.TextInput(attrs={'id': 'message-name'})
    )
    message_email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'id': 'message-email'})
    )
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={'id': 'message'})
    )

class DataCaptureForm(forms.ModelForm):
    class Meta:
        model = DataCapture
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.is_superuser:
                self.fields['region'].queryset = Region.objects.all()
                self.fields['mmda'].queryset = MMDA.objects.all()
            else:
                try:
                    user_assignment = UserAssignment.objects.get(user=self.user)
                    user_region = user_assignment.region
                    user_mmda = user_assignment.mmda

                    self.fields['region'].queryset = Region.objects.filter(id=user_region.id)
                    self.fields['region'].initial = user_region
                    self.fields['region'].disabled = True
                    self.fields['mmda'].queryset = MMDA.objects.filter(region=user_region)
                    self.fields['mmda'].initial = user_mmda
                    self.fields['mmda'].disabled = True

                except UserAssignment.DoesNotExist:
                    self.fields['region'].queryset = Region.objects.none()
                    self.fields['mmda'].queryset = MMDA.objects.none()
                    self.fields['region'].disabled = True
                    self.fields['mmda'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        if self.user and not self.user.is_superuser:
            try:
                user_assignment = UserAssignment.objects.get(user=self.user)
                if cleaned_data.get('region') != user_assignment.region:
                    self.add_error('region', "Invalid region assignment.")
                if cleaned_data.get('mmda') != user_assignment.mmda:
                    self.add_error('mmda', "Invalid MMDA assignment.")
            except UserAssignment.DoesNotExist:
                raise ValidationError("Region/MMDA assignment missing for your account.")
        return cleaned_data

class EducationForm(forms.ModelForm):
    class Meta:
        model = EducationCapture
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.is_superuser:
                self.fields['region'].queryset = Region.objects.all()
                self.fields['mmda'].queryset = MMDA.objects.all()
            else:
                try:
                    user_assignment = UserAssignment.objects.get(user=self.user)
                    user_region = user_assignment.region
                    user_mmda = user_assignment.mmda

                    self.fields['region'].queryset = Region.objects.filter(id=user_region.id)
                    self.fields['region'].initial = user_region
                    self.fields['region'].disabled = True
                    self.fields['mmda'].queryset = MMDA.objects.filter(region=user_region)
                    self.fields['mmda'].initial = user_mmda
                    self.fields['mmda'].disabled = True

                except UserAssignment.DoesNotExist:
                    self.fields['region'].queryset = Region.objects.none()
                    self.fields['mmda'].queryset = MMDA.objects.none()
                    self.fields['region'].disabled = True
                    self.fields['mmda'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        if self.user and not self.user.is_superuser:
            try:
                user_assignment = UserAssignment.objects.get(user=self.user)
                if cleaned_data.get('region') != user_assignment.region:
                    self.add_error('region', "Invalid region assignment.")
                if cleaned_data.get('mmda') != user_assignment.mmda:
                    self.add_error('mmda', "Invalid MMDA assignment.")
            except UserAssignment.DoesNotExist:
                raise ValidationError("Region/MMDA assignment missing for your account.")
        return cleaned_data

class HealthCaptureForm(forms.ModelForm):
    class Meta:
        model = HealthCapture
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.is_superuser:
                self.fields['region'].queryset = Region.objects.all()
                self.fields['mmda'].queryset = MMDA.objects.all()
            else:
                try:
                    user_assignment = UserAssignment.objects.get(user=self.user)
                    user_region = user_assignment.region
                    user_mmda = user_assignment.mmda

                    self.fields['region'].queryset = Region.objects.filter(id=user_region.id)
                    self.fields['region'].initial = user_region
                    self.fields['region'].disabled = True
                    self.fields['mmda'].queryset = MMDA.objects.filter(region=user_region)
                    self.fields['mmda'].initial = user_mmda
                    self.fields['mmda'].disabled = True

                except UserAssignment.DoesNotExist:
                    self.fields['region'].queryset = Region.objects.none()
                    self.fields['mmda'].queryset = MMDA.objects.none()
                    self.fields['region'].disabled = True
                    self.fields['mmda'].disabled = True

    def clean_government_admin_ghana_card(self):
        ghana_card_number = self.cleaned_data.get('government_admin_ghana_card')
        if ghana_card_number:
            try:
                record = DataCapture.objects.get(ghana_card=ghana_card_number)
                self.instance.government_admin = f"{record.first_name} {record.surname}"
                self.instance.government_admin_contact = record.contact_1
            except DataCapture.DoesNotExist:
                raise ValidationError("No record found for this Ghana Card number")
        return ghana_card_number

class GovernmentCaptureForm(forms.ModelForm):
    class Meta:
        model = GovernmentCapture
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.is_superuser:
                self.fields['region'].queryset = Region.objects.all()
                self.fields['mmda'].queryset = MMDA.objects.all()
            else:
                try:
                    user_assignment = UserAssignment.objects.get(user=self.user)
                    user_region = user_assignment.region
                    user_mmda = user_assignment.mmda

                    self.fields['region'].queryset = Region.objects.filter(id=user_region.id)
                    self.fields['region'].initial = user_region
                    self.fields['region'].disabled = True
                    self.fields['mmda'].queryset = MMDA.objects.filter(region=user_region)
                    self.fields['mmda'].initial = user_mmda
                    self.fields['mmda'].disabled = True

                except UserAssignment.DoesNotExist:
                    self.fields['region'].queryset = Region.objects.none()
                    self.fields['mmda'].queryset = MMDA.objects.none()
                    self.fields['region'].disabled = True
                    self.fields['mmda'].disabled = True

    def clean_government_admin_ghana_card(self):
        ghana_card_number = self.cleaned_data.get('government_admin_ghana_card')
        if ghana_card_number:
            try:
                record = DataCapture.objects.get(ghana_card=ghana_card_number)
                self.instance.government_admin = f"{record.first_name} {record.surname}"
                self.instance.government_admin_contact = record.contact_1
            except DataCapture.DoesNotExist:
                raise ValidationError("No record found for this Ghana Card number")
        return ghana_card_number

class SMECaptureForm(forms.ModelForm):
    class Meta:
        model = SMECapture
        fields = '__all__'
        widgets = {
            'category': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.is_superuser:
                self.fields['region'].widget = forms.Select()
                self.fields['mmda'].widget = forms.Select()
                self.fields['region'].queryset = Region.objects.all()
                self.fields['mmda'].queryset = MMDA.objects.all()
            else:
                try:
                    user_assignment = UserAssignment.objects.get(user=self.user)
                    user_region = user_assignment.region
                    user_mmda = user_assignment.mmda

                    self.fields['region'].queryset = Region.objects.filter(id=user_region.id)
                    self.fields['region'].initial = user_region
                    self.fields['region'].disabled = True
                    self.fields['mmda'].queryset = MMDA.objects.filter(region=user_region)
                    self.fields['mmda'].initial = user_mmda
                    self.fields['mmda'].disabled = True

                except UserAssignment.DoesNotExist:
                    self.fields['region'].queryset = Region.objects.none()
                    self.fields['mmda'].queryset = MMDA.objects.none()
                    self.fields['region'].disabled = True
                    self.fields['mmda'].disabled = True

    def clean_sme_admin_ghana_card(self):
        ghana_card_number = self.cleaned_data.get('sme_admin_ghana_card')
        if ghana_card_number:
            try:
                record = DataCapture.objects.get(ghana_card=ghana_card_number)
                self.instance.sme_admin = f"{record.first_name} {record.surname}"
                self.instance.sme_admin_contact = record.contact_1
            except DataCapture.DoesNotExist:
                raise ValidationError("No record found for this Ghana Card number")
        return ghana_card_number

class ResidentialCaptureForm(forms.ModelForm):
    class Meta:
        model = ResidentialCapture
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.is_superuser:
                self.fields['region'].queryset = Region.objects.all()
                self.fields['mmda'].queryset = MMDA.objects.all()
            else:
                try:
                    user_assignment = UserAssignment.objects.get(user=self.user)
                    user_region = user_assignment.region
                    user_mmda = user_assignment.mmda

                    self.fields['region'].queryset = Region.objects.filter(id=user_region.id)
                    self.fields['region'].initial = user_region
                    self.fields['region'].disabled = True
                    self.fields['mmda'].queryset = MMDA.objects.filter(region=user_region)
                    self.fields['mmda'].initial = user_mmda
                    self.fields['mmda'].disabled = True

                except UserAssignment.DoesNotExist:
                    self.fields['region'].queryset = Region.objects.none()
                    self.fields['mmda'].queryset = MMDA.objects.none()
                    self.fields['region'].disabled = True
                    self.fields['mmda'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        if self.user and not self.user.is_superuser:
            try:
                user_assignment = UserAssignment.objects.get(user=self.user)
                if cleaned_data.get('region') != user_assignment.region:
                    self.add_error('region', "Invalid region assignment.")
                if cleaned_data.get('mmda') != user_assignment.mmda:
                    self.add_error('mmda', "Invalid MMDA assignment.")
            except UserAssignment.DoesNotExist:
                raise ValidationError("User assignment missing.")
        return cleaned_data

class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Search...'}))