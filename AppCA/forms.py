from django import forms

class KeyGenerationRandomForm(forms.Form):
    number_of_keys = forms.IntegerField(
        label='Number of Keys',
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'type': 'number', 'min': 0, 'max': 100}),
    )

    generation_type = forms.ChoiceField(
        label='Generation Type',
        choices=[('random', 'Random'), ('sequential', 'Sequential')],
        initial='random',
        widget=forms.RadioSelect,
    )

    first_value = forms.IntegerField(
        label='First Value (for sequential generation)',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'type': 'number', 'min': 0}),
    )