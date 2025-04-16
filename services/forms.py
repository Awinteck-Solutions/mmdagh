# Forms
from django import forms
from .models import SignalMessage,GhanaPoliceService,GhanaFireStation,firehydrant,ghmedicalfacility,PoliceStation,PoliceRegion,Division,District

class GhanaPoliceServiceForm(forms.ModelForm):
    class Meta:
        model = GhanaPoliceService
        fields = '__all__'


class GNFSForm(forms.ModelForm):
    class Meta:
        model = GhanaFireStation
        fields = '__all__'

class FirehydrantForm(forms.ModelForm):
    class Meta:
        model = firehydrant
        fields = '__all__'

class FirehydrantForm(forms.ModelForm):
    class Meta:
        model = ghmedicalfacility
        fields = '__all__'


#from django import forms
#from .models import PoliceStation

'''class PoliceStationForm(forms.ModelForm):
    class Meta:
        model = PoliceStation
        fields = ["police_region"]'''


# forms.py
# forms.py
# forms.py
from django import forms
from .models import PoliceRegion, Division, District, PoliceStation
from django import forms
from .models import PoliceStation, PoliceRegion, Division, District

class PoliceStationForm(forms.ModelForm):
    police_region = forms.ModelChoiceField(
        queryset=PoliceRegion.objects.all(),
        required=False,
        label="Select Region",
        widget=forms.Select(attrs={'class': 'form-control region-select'})
    )

    division = forms.ModelChoiceField(
        queryset=Division.objects.none(),
        required=False,
        label="Select Division",
        widget=forms.Select(attrs={'class': 'form-control division-select'})
    )

    district = forms.ModelChoiceField(
        queryset=District.objects.none(),
        required=True,
        label="Select District",
        widget=forms.Select(attrs={'class': 'form-control district-select'})
    )

    class Meta:
        model = PoliceStation
        fields = ['district', 'name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize fields from instance if editing
        if self.instance and self.instance.pk:
            try:
                region = self.instance.district.division.police_region
                division = self.instance.district.division
                self.fields['division'].queryset = Division.objects.filter(police_region=region)
                self.fields['district'].queryset = District.objects.filter(division=division)
            except AttributeError:
                pass  # In case related fields are not fully populated

        # Handle dynamic data from POST
        if 'police_region' in self.data:
            try:
                region_id = int(self.data.get('police_region'))
                self.fields['division'].queryset = Division.objects.filter(police_region_id=region_id)
            except (ValueError, TypeError):
                pass

        if 'division' in self.data:
            try:
                division_id = int(self.data.get('division'))
                self.fields['district'].queryset = District.objects.filter(division_id=division_id)
            except (ValueError, TypeError):
                pass

    def clean_code(self):
        code = self.cleaned_data['code']
        if PoliceStation.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This code is already in use.")
        return code


from django import forms
from .models import SignalMessage, Service  # Assuming Service is the model for `service`

class SignalMessageForm(forms.ModelForm):
    class Meta:
        model = SignalMessage
        fields = ['service', 'police_region', 'division', 'district', 'station', 'subject', 'content', 'priority']
        widgets = {
            'police_region': forms.Select(attrs={'class': 'form-control'}),
            'division': forms.Select(attrs={'class': 'form-control'}),
            'district': forms.Select(attrs={'class': 'form-control'}),
            'station': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial empty choices for dependent fields
        self.fields['division'].queryset = Division.objects.none()
        self.fields['district'].queryset = District.objects.none()
        self.fields['station'].queryset = PoliceStation.objects.none()
