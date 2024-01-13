from django import forms

class KeyGenerationForm(forms.Form):
    number_of_keys = forms.IntegerField(
        label='Number of Keys',
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'type': 'number', 'min': 0, 'max': 100}),
    )
