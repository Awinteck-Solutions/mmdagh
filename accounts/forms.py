from django import forms
from .models import DataCapture, EducationCapture, ResidentialCapture, HealthCapture, GovernmentCapture,SMECapture,UserAssignment, Region, MMDA
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=63, widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)



class ContactForm(forms.Form):
    message_name = forms.CharField(
        label='Full Name',
        max_length=100,
        widget=forms.TextInput(attrs={
            'id': 'message-name',
            'required': True
        })
    )
    
    message_email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'id': 'message-email',
            'required': True
        })
    )
    
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={
            'id': 'message',
            'required': True
        })
    )




class DataCaptureForm(forms.ModelForm):
    class Meta:
        model = DataCapture
        fields = '__all__'  # Include all fields from DataCapture model
        '''widgets = {
            'region': forms.HiddenInput(),  # Default hidden
            'mmda': forms.HiddenInput(),    # Default hidden
        }'''

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)

        self.user = user  # Store user for later reference

        if user:
            if user.is_superuser:
                # Superusers can select any region and MMDA
                self.fields['region'].queryset = Region.objects.all()
                self.fields['mmda'].queryset = MMDA.objects.all()
            else:
                try:
                    # Retrieve the user's assigned region and MMDA
                    user_assignment = UserAssignment.objects.get(user=user)
                    user_region = user_assignment.region
                    user_mmda = user_assignment.mmda

                    # Set fields to the assigned region and MMDA
                    self.fields['region'].queryset = Region.objects.filter(id=user_region.id)
                    self.fields['region'].initial = user_region
                    self.fields['mmda'].queryset = MMDA.objects.filter(region=user_region)
                    self.fields['mmda'].initial = user_mmda

                    # Lock fields to prevent modification
                    self.fields['region'].widget.attrs.update({'readonly': True})
                    self.fields['region'].disabled = True
                    self.fields['mmda'].widget.attrs.update({'readonly': True})
                    self.fields['mmda'].disabled = True

                except UserAssignment.DoesNotExist:
                    # If no assignment is found, restrict selection
                    self.fields['region'].queryset = Region.objects.none()
                    self.fields['mmda'].queryset = MMDA.objects.none()
                    self.fields['region'].widget.attrs.update({'readonly': True})
                    self.fields['region'].disabled = True
                    self.fields['mmda'].widget.attrs.update({'readonly': True})
                    self.fields['mmda'].disabled = True

    def clean(self):
        """Ensure users do not modify their assigned region and MMDA."""
        cleaned_data = super().clean()
        region = cleaned_data.get('region')
        mmda = cleaned_data.get('mmda')

        if self.user and not self.user.is_superuser:
            try:
                user_assignment = UserAssignment.objects.get(user=self.user)
                if region != user_assignment.region:
                    self.add_error('region', f"You are not allowed to assign this record to the {region.name} region.")
                if mmda != user_assignment.mmda:
                    self.add_error('mmda', f"You are not allowed to assign this record to the {mmda.name} MMDA.")
            except UserAssignment.DoesNotExist:
                raise forms.ValidationError("Region and MMDA assignment is missing for your account.")

        return cleaned_data





class EducationForm(forms.ModelForm):
    class Meta:
        model = EducationCapture
        fields = '__all__'  # Include all fields from EducationCapture model
        widgets = {
            'region': forms.HiddenInput(),  # Default hidden
            'mmda': forms.HiddenInput(),    # Default hidden
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)

        if user:
            if user.is_superuser:
                # Superusers can select any region and MMDA
                self.fields['region'].queryset = Region.objects.all()
                self.fields['mmda'].queryset = MMDA.objects.all()
                self.fields['region'].widget.attrs['readonly'] = False
                self.fields['region'].disabled = False
                self.fields['mmda'].widget.attrs['readonly'] = False
                self.fields['mmda'].disabled = False
            else:
                try:
                    # Retrieve the user's assigned region and MMDA
                    user_assignment = UserAssignment.objects.get(user=user)
                    user_region = user_assignment.region
                    user_mmda = user_assignment.mmda

                    # Limit regions to the user's assigned region
                    self.fields['region'].queryset = Region.objects.filter(id=user_region.id)
                    self.fields['region'].initial = user_region
                    self.fields['region'].widget.attrs['readonly'] = True
                    self.fields['region'].disabled = True

                    # Limit MMDAs to those in the user's assigned region
                    self.fields['mmda'].queryset = MMDA.objects.filter(region=user_region)
                    self.fields['mmda'].initial = user_mmda
                    self.fields['mmda'].widget.attrs['readonly'] = True
                    self.fields['mmda'].disabled = True

                except UserAssignment.DoesNotExist:
                    # For users without an assignment, restrict access
                    self.fields['region'].queryset = Region.objects.none()
                    self.fields['region'].widget.attrs['readonly'] = True
                    self.fields['region'].disabled = True
                    self.fields['mmda'].queryset = MMDA.objects.none()
                    self.fields['mmda'].widget.attrs['readonly'] = True
                    self.fields['mmda'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get('region')
        mmda = cleaned_data.get('mmda')
        user = self.initial.get('user')

        # Ensure a region is selected
        if not region:
            raise forms.ValidationError("Region selection is required.")

        # Ensure the selected region and MMDA belong to the user
        if user and not user.is_superuser:
            try:
                user_assignment = UserAssignment.objects.get(user=user)
                if region != user_assignment.region:
                    raise forms.ValidationError(f"You are not allowed to assign this account to the {region.name} region.")
                if mmda != user_assignment.mmda:
                    raise forms.ValidationError(f"You are not allowed to assign this account to the {mmda.name} MMDA.")
            except UserAssignment.DoesNotExist:
                raise forms.ValidationError("Region and MMDA assignment is missing for your account.")

        return cleaned_data



'''class EducationForm(forms.ModelForm):
    class Meta:
        model = EducationCapture
        fields = '__all__'  # Include all fields from DataCapture model
        #exclude = ['region', 'mmda']  # Exclude region and mmda since they are set automatically

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)

        if user:
            if user.is_superuser:
                # Superusers can select any region
                self.fields['region'].queryset = Region.objects.all()
                self.fields['region'].widget.attrs['readonly'] = False
                self.fields['region'].disabled = False
            else:
                try:
                    # Retrieve the user's assigned region and MMDA
                    user_assignment = UserAssignment.objects.get(user=user)
                    user_region = user_assignment.region
                    user_mmda = user_assignment.mmda

                    # Limit regions to the user's assigned region
                    self.fields['region'].queryset = Region.objects.filter(id=user_region.id)
                    self.fields['region'].initial = user_region
                    self.fields['region'].widget.attrs['readonly'] = True
                    self.fields['region'].disabled = True

                    # Limit MMDAs to those in the user's assigned region
                    self.fields['mmda'].queryset = MMDA.objects.filter(region=user_region)
                    self.fields['mmda'].initial = user_mmda
                    self.fields['mmda'].widget.attrs['readonly'] = True
                    self.fields['mmda'].disabled = True

                except UserAssignment.DoesNotExist:
                    # For users without an assignment, restrict access
                    self.fields['region'].queryset = Region.objects.none()
                    self.fields['region'].widget.attrs['readonly'] = True
                    self.fields['region'].disabled = True
                    self.fields['mmda'].queryset = MMDA.objects.none()
                    self.fields['mmda'].widget.attrs['readonly'] = True
                    self.fields['mmda'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get('region')
        mmda = cleaned_data.get('mmda')
        user = self.initial.get('user')

        # Ensure a region is selected
        if not region:
            raise forms.ValidationError("Region selection is required.")

        # Ensure the selected region and MMDA belong to the user
        if user and not user.is_superuser:
            try:
                user_assignment = UserAssignment.objects.get(user=user)
                if region != user_assignment.region:
                    raise forms.ValidationError(f"You are not allowed to assign this account to the {region.name} region.")
                if mmda != user_assignment.mmda:
                    raise forms.ValidationError(f"You are not allowed to assign this account to the {mmda.name} MMDA.")
            except UserAssignment.DoesNotExist:
                raise forms.ValidationError("Region and MMDA assignment is missing for your account.")

        return cleaned_data'''




class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Search...'})
    )


'''class ResidentialCaptureForm(forms.ModelForm):
    class Meta:
        model = ResidentialCapture
        fields = '__all__'  # Include all fields from ResidentialCapture model

    contact_1 = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'placeholder': 'eg: 0244877620 or 0207046614'  # Placeholder text
        })
    )

    gps_address = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'eg: AB-0001-5514 or GA-0045-2545564'  # Placeholder text
        }),
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z]{2}-\d{4}-\d{4,}$',
                message="GPS Address should follow the format: XX-XXXX-XXXX where X is a number."
            )
        ]
    )

    ghana_card = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'GHA-XXXXXXXXXX-X'  # Placeholder text
        }),
        validators=[
            RegexValidator(
                regex=r'^GHA-\d{10}-\d*$',  # This pattern matches "GHA-" followed by 10 digits and optionally a number after the hyphen
                message="Ghana Card should follow the format: GHA-XXXXXXXXXX-X where X is optional."
            )
        ]
    )

    def clean(self):
        cleaned_data = super().clean()
        electricity_access = cleaned_data.get('electricity_access')
        ecg_pole_no = cleaned_data.get('ecg_pole_no')

        if electricity_access and not ecg_pole_no:
            raise forms.ValidationError("If electricity access is Yes, ECG Pole No. is required.")

        return cleaned_data'''

class HealthCaptureForm(forms.ModelForm):
    class Meta:
        model = HealthCapture
        fields = '__all__'  # Include all fields from DataCapture model
        ''''widgets = {
            'region': forms.HiddenInput(),  # Default hidden
            'mmda': forms.HiddenInput(),    # Default hidden
        }'''

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)

        if user:
            if user.is_superuser:
                # Superusers can select any region
                self.fields['region'].queryset = Region.objects.all()
                self.fields['region'].widget.attrs['readonly'] = False
                self.fields['region'].disabled = False
            else:
                try:
                    # Retrieve the user's assigned region and MMDA
                    user_assignment = UserAssignment.objects.get(user=user)
                    user_region = user_assignment.region
                    user_mmda = user_assignment.mmda

                    # Limit regions to the user's assigned region
                    self.fields['region'].queryset = Region.objects.filter(id=user_region.id)
                    self.fields['region'].initial = user_region
                    self.fields['region'].widget.attrs['readonly'] = True
                    self.fields['region'].disabled = True

                    # Limit MMDAs to those in the user's assigned region
                    self.fields['mmda'].queryset = MMDA.objects.filter(region=user_region)
                    self.fields['mmda'].initial = user_mmda
                    self.fields['mmda'].widget.attrs['readonly'] = True
                    self.fields['mmda'].disabled = True

                except UserAssignment.DoesNotExist:
                    # For users without an assignment, restrict access
                    self.fields['region'].queryset = Region.objects.none()
                    self.fields['region'].widget.attrs['readonly'] = True
                    self.fields['region'].disabled = True
                    self.fields['mmda'].queryset = MMDA.objects.none()
                    self.fields['mmda'].widget.attrs['readonly'] = True
                    self.fields['mmda'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get('region')
        mmda = cleaned_data.get('mmda')
        user = self.initial.get('user')

        # Ensure a region is selected
        if not region:
            raise forms.ValidationError("Region selection is required.")

        # Ensure the selected region and MMDA belong to the user
        if user and not user.is_superuser:
            try:
                user_assignment = UserAssignment.objects.get(user=user)
                if region != user_assignment.region:
                    raise forms.ValidationError(f"You are not allowed to assign this account to the {region.name} region.")
                if mmda != user_assignment.mmda:
                    raise forms.ValidationError(f"You are not allowed to assign this account to the {mmda.name} MMDA.")
            except UserAssignment.DoesNotExist:
                raise forms.ValidationError("Region and MMDA assignment is missing for your account.")

        return cleaned_data

    def clean_government_admin_ghana_card(self):
        ghana_card_entry = self.cleaned_data.get('government_admin_ghana_card')

        if ghana_card_entry:
            # Simulate fetching data from the DataCapture model
            try:
                ghana_card_data = DataCapture.objects.get(ghana_card=ghana_card_entry.ghana_card)
                self.instance.government_admin = f"{ghana_card_data.first_name} {ghana_card_data.surname}"
                self.instance.government_admin_contact = ghana_card_data.contact_1
            except DataCapture.DoesNotExist:
                raise ValidationError("Invalid Ghana Card: No matching record found.")
        return ghana_card_entry

    def _parse_ghana_card(self, ghana_card_number):
        """
        Mock function to simulate looking up Ghana Card details.
        Replace with actual lookup if connected to an API/database.
        """
        sample_data = {
            "GHA-123456789-0": {
                "first_name": "John",
                "surname": "Doe",
                "contact": "+233123456789"
            },
            "GHA-987654321-0": {
                "first_name": "Jane",
                "surname": "Smith",
                "contact": "+233987654321"
            }
        }
        return sample_data.get(ghana_card_number)



class GovernmentCaptureForm(forms.ModelForm):
    class Meta:
        model = GovernmentCapture
        fields = '__all__'  # Include all fields from DataCapture model
        widgets = {
            'region': forms.HiddenInput(),  # Default hidden
            'mmda': forms.HiddenInput(),    # Default hidden
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)

        if user:
            if user.is_superuser:
                # Superusers can select any region
                self.fields['region'].queryset = Region.objects.all()
                self.fields['region'].widget.attrs['readonly'] = False
                self.fields['region'].disabled = False
            else:
                try:
                    # Retrieve the user's assigned region and MMDA
                    user_assignment = UserAssignment.objects.get(user=user)
                    user_region = user_assignment.region
                    user_mmda = user_assignment.mmda

                    # Limit regions to the user's assigned region
                    self.fields['region'].queryset = Region.objects.filter(id=user_region.id)
                    self.fields['region'].initial = user_region
                    self.fields['region'].widget.attrs['readonly'] = True
                    self.fields['region'].disabled = True

                    # Limit MMDAs to those in the user's assigned region
                    self.fields['mmda'].queryset = MMDA.objects.filter(region=user_region)
                    self.fields['mmda'].initial = user_mmda
                    self.fields['mmda'].widget.attrs['readonly'] = True
                    self.fields['mmda'].disabled = True

                except UserAssignment.DoesNotExist:
                    # For users without an assignment, restrict access
                    self.fields['region'].queryset = Region.objects.none()
                    self.fields['region'].widget.attrs['readonly'] = True
                    self.fields['region'].disabled = True
                    self.fields['mmda'].queryset = MMDA.objects.none()
                    self.fields['mmda'].widget.attrs['readonly'] = True
                    self.fields['mmda'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get('region')
        mmda = cleaned_data.get('mmda')
        user = self.initial.get('user')

        # Ensure a region is selected
        if not region:
            raise forms.ValidationError("Region selection is required.")

        # Ensure the selected region and MMDA belong to the user
        if user and not user.is_superuser:
            try:
                user_assignment = UserAssignment.objects.get(user=user)
                if region != user_assignment.region:
                    raise forms.ValidationError(f"You are not allowed to assign this account to the {region.name} region.")
                if mmda != user_assignment.mmda:
                    raise forms.ValidationError(f"You are not allowed to assign this account to the {mmda.name} MMDA.")
            except UserAssignment.DoesNotExist:
                raise forms.ValidationError("Region and MMDA assignment is missing for your account.")

        return cleaned_data

    def clean_government_admin_ghana_card(self):
        ghana_card_entry = self.cleaned_data.get('government_admin_ghana_card')

        if ghana_card_entry:
            # Simulate fetching data from the DataCapture model
            try:
                ghana_card_data = DataCapture.objects.get(ghana_card=ghana_card_entry.ghana_card)
                self.instance.government_admin = f"{ghana_card_data.first_name} {ghana_card_data.surname}"
                self.instance.government_admin_contact = ghana_card_data.contact_1
            except DataCapture.DoesNotExist:
                raise ValidationError("Invalid Ghana Card: No matching record found.")
        return ghana_card_entry

    def _parse_ghana_card(self, ghana_card_number):
        """
        Mock function to simulate looking up Ghana Card details.
        Replace with actual lookup if connected to an API/database.
        """
        sample_data = {
            "GHA-123456789-0": {
                "first_name": "John",
                "surname": "Doe",
                "contact": "+233123456789"
            },
            "GHA-987654321-0": {
                "first_name": "Jane",
                "surname": "Smith",
                "contact": "+233987654321"
            }
        }
        return sample_data.get(ghana_card_number)



class SMECaptureForm(forms.ModelForm):
    class Meta:
        model = SMECapture
        fields = '__all__'  # Include all fields from DataCapture model
        widgets = {
            'region': forms.HiddenInput(),  # Default hidden
            'mmda': forms.HiddenInput(),    # Default hidden
            'category': forms.HiddenInput(),  # Default hidden
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)

        if user:
            if user.is_superuser:
                # Superusers can select any region
                self.fields['region'].queryset = Region.objects.all()
                self.fields['region'].widget.attrs['readonly'] = False
                self.fields['region'].disabled = False
            else:
                try:
                    # Retrieve the user's assigned region and MMDA
                    user_assignment = UserAssignment.objects.get(user=user)
                    user_region = user_assignment.region
                    user_mmda = user_assignment.mmda

                    # Limit regions to the user's assigned region
                    self.fields['region'].queryset = Region.objects.filter(id=user_region.id)
                    self.fields['region'].initial = user_region
                    self.fields['region'].widget.attrs['readonly'] = True
                    self.fields['region'].disabled = True

                    # Limit MMDAs to those in the user's assigned region
                    self.fields['mmda'].queryset = MMDA.objects.filter(region=user_region)
                    self.fields['mmda'].initial = user_mmda
                    self.fields['mmda'].widget.attrs['readonly'] = True
                    self.fields['mmda'].disabled = True

                except UserAssignment.DoesNotExist:
                    # For users without an assignment, restrict access
                    self.fields['region'].queryset = Region.objects.none()
                    self.fields['region'].widget.attrs['readonly'] = True
                    self.fields['region'].disabled = True
                    self.fields['mmda'].queryset = MMDA.objects.none()
                    self.fields['mmda'].widget.attrs['readonly'] = True
                    self.fields['mmda'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get('region')
        mmda = cleaned_data.get('mmda')
        user = self.initial.get('user')

        # Ensure a region is selected
        if not region:
            raise forms.ValidationError("Region selection is required.")

        # Ensure the selected region and MMDA belong to the user
        if user and not user.is_superuser:
            try:
                user_assignment = UserAssignment.objects.get(user=user)
                if region != user_assignment.region:
                    raise forms.ValidationError(f"You are not allowed to assign this account to the {region.name} region.")
                if mmda != user_assignment.mmda:
                    raise forms.ValidationError(f"You are not allowed to assign this account to the {mmda.name} MMDA.")
            except UserAssignment.DoesNotExist:
                raise forms.ValidationError("Region and MMDA assignment is missing for your account.")

        return cleaned_data


    def clean_sme_admin_ghana_card(self):
        ghana_card_entry = self.cleaned_data.get('sme_admin_ghana_card')

        if ghana_card_entry:
            # Simulate fetching data from the DataCapture model
            try:
                ghana_card_data = DataCapture.objects.get(ghana_card=ghana_card_entry.ghana_card)
                self.instance.sme_admin = f"{ghana_card_data.first_name} {ghana_card_data.surname}"
                self.instance.sme_admin_contact = ghana_card_data.contact_1
            except DataCapture.DoesNotExist:
                raise ValidationError("Invalid Ghana Card: No matching record found.")
        return ghana_card_entry

    def _parse_ghana_card(self, ghana_card_number):
        """
        Mock function to simulate looking up Ghana Card details.
        Replace with actual lookup if connected to an API/database.
        """
        sample_data = {
            "GHA-123456789-0": {
                "first_name": "John",
                "surname": "Doe",
                "contact": "+233123456789"
            },
            "GHA-987654321-0": {
                "first_name": "Jane",
                "surname": "Smith",
                "contact": "+233987654321"
            }
        }
        return sample_data.get(ghana_card_number)




class ResidentialCaptureForm(forms.ModelForm):
    class Meta:
        model = ResidentialCapture
        fields = '__all__'  
        '''widgets = {
            'region': forms.HiddenInput(),  # Default hidden
            'mmda': forms.HiddenInput(),    # Default hidden
        }'''


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract 'user' before calling super()
        super().__init__(*args, **kwargs)

        if user:
            if user.is_superuser:
                self.fields['region'].queryset = Region.objects.all()
                self.fields['mmda'].queryset = MMDA.objects.all()
            else:
                try:
                    user_assignment = UserAssignment.objects.get(user=user)
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
