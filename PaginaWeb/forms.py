from django import forms
from django.forms.fields import CharField
from Tablas.models import Comentario, CustomUser, Cliente, Viaje
from django.contrib.auth.forms import UserCreationForm

class ExtendedUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=100)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class DateInput(forms.DateInput):
    input_type = 'date'

class ClienteCreationForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ('dni', 'fecha_nacimiento','gold','tarjeta_nombre_titular','tarjeta_numero','tarjeta_cod_seguridad','tarjeta_fecha_vencimiento',)
        widgets = {
            'fecha_nacimiento': DateInput(),
            'tarjeta_fecha_vencimiento': DateInput(),
        } 

class AgregarComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ('contenido',)
        widgets = {
            'contenido': forms.Textarea(attrs={'class': 'form-control'})
        }