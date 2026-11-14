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


class FightForm(forms.Form):
    fighter_one = forms.ModelChoiceField(queryset=Unit.objects.none(), label='First fighter')
    fighter_two = forms.ModelChoiceField(queryset=Unit.objects.none(), label='Second fighter')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        living_units = Unit.objects.filter(health__gt=0)
        self.fields['fighter_one'].queryset = living_units
        self.fields['fighter_two'].queryset = living_units
        self.fields['fighter_one'].label_from_instance = self._fighter_label
        self.fields['fighter_two'].label_from_instance = self._fighter_label
        self.fields['fighter_one'].widget.attrs.update({'class': 'fight-select'})
        self.fields['fighter_two'].widget.attrs.update({'class': 'fight-select'})

    @staticmethod
    def _fighter_label(unit):
        return f'{unit.name} · {unit.team} · {unit.health} HP'

    def clean(self):
        cleaned_data = super().clean()
        fighter_one = cleaned_data.get('fighter_one')
        fighter_two = cleaned_data.get('fighter_two')
        if fighter_one and fighter_two:
            if fighter_one.pk == fighter_two.pk:
                self.add_error('fighter_two', 'Choose two different fighters.')
            elif fighter_one.team == fighter_two.team:
                self.add_error('fighter_two', 'Fighters must be from different teams.')
        return cleaned_data
