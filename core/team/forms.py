# forms.py
from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from core.models import Team, Participant


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'captain', 'vice_captain']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'captain': forms.Select(attrs={'class': 'form-control'}),
            'vice_captain': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        captain = cleaned_data.get('captain')
        vice_captain = cleaned_data.get('vice_captain')

        if captain and vice_captain and captain == vice_captain:
            raise forms.ValidationError("Captain and Vice Captain cannot be the same person.")

        return cleaned_data


class ParticipantForm(forms.ModelForm):
    name = forms.ModelChoiceField(queryset=User.objects.all())

    class Meta:
        model = Participant
        exclude = ['points']


ParticipantFormSet = inlineformset_factory(
    Team,
    Participant,
    ParticipantForm,
    extra=1,
    can_delete=True,
    widgets={
        'name': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Participant Name'}),
        'chest_no': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Chest No'}),
        'points': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Points'}),
    }
)
