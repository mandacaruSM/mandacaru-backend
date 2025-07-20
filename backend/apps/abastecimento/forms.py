from django import forms
from .models import RegistroAbastecimento

class AbastecimentoForm(forms.ModelForm):
    class Meta:
        model = RegistroAbastecimento
        fields = '__all__'
