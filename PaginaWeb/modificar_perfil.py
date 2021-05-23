from django.contrib.auth.models import User
from django import forms

class ModificarNombre(forms.ModelForm):
    nombre = forms.CharField(required=True, max_length=50, help_text="Requerido. 50 caracteres como máximo.")

    class Meta:
        model = User
        fields = ["nombre"]

    # def clean_nombre(self):
    #     nombre = self.cleaned_data.get("nombre")
    #     if "nombre" in self.changed_data:
    #         return nombre
    #     raise forms.ValidationError(u"No ha modificado el nombre")