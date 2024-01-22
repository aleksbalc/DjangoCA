from django import forms

class KeyGenerationRandomForm(forms.Form):
    number_of_keys = forms.IntegerField(
        label='Number of N_IDs',
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={'type': 'number', 'min': 0, 'max': 100, 'placeholder': '1-100'}),
    )


class KeyGenerationSequentialForm(forms.Form):
    number_of_keys = forms.IntegerField(
        label='Number of N_IDs',
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={'type': 'number', 'min': 0, 'max': 100, 'placeholder': '1-100'}),
    )

    first_value = forms.IntegerField(
        label='First Value (for sequential generation)',
        required=False,
        min_value=0,
        max_value=9999,
        widget=forms.NumberInput(attrs={'type': 'number', 'min': 0, 'max': 9999, 'placeholder': '0000'}),
    )
    
class KeyGenerationFileUploadForm(forms.Form):
    file = forms.FileField(
        label='Upload .txt File',
        widget=forms.ClearableFileInput(attrs={'accept': '.txt'}),
    )