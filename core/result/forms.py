from django import forms

from core.models import Result


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        exclude = ['points']
