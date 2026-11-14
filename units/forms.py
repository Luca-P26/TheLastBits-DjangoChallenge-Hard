from django import forms

from .models import Unit


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ('name', 'type', 'team', 'health', 'attack_points', 'profile_image_link')
        labels = {
            'type': 'Fighter type',
            'team': 'Team',
            'health': 'Health',
            'attack_points': 'Attack points',
            'profile_image_link': 'Profile image URL',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. General Deadlock'}),
            'type': forms.Select(),
            'team': forms.Select(),
            'health': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 1}),
            'attack_points': forms.NumberInput(attrs={'min': 0, 'max': 50, 'step': 1}),
            'profile_image_link': forms.URLInput(attrs={'placeholder': 'https://example.com/fighter.jpg'}),
        }
