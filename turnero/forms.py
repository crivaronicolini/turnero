from allauth.account.forms import SignupForm
from django import forms
from .models import Especialidad


class PacienteSignUpForm(SignupForm):
    dni = forms.CharField(label="DNI", max_length=20)
    fecha_nac = forms.DateField(label="Fecha de nacimiento")
    nro_afiliado = forms.CharField(label="Nro. de afiliado", max_length=20)
    obra_social = forms.CharField( label="Obra Social")
    plan = forms.CharField(label="Plan")

class DoctorSignUpForm(SignupForm):
    dni = forms.CharField(label="DNI", max_length=20)
    fecha_nac = forms.DateField(label="Fecha de nacimiento")
    matricula = forms.CharField(label="Matrícula", max_length=30)
    especialidades = forms.ModelMultipleChoiceField(
        queryset=Especialidad.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Especialidades"
    )


class SecretarioSignUpForm(SignupForm):
    dni = forms.CharField(label="DNI", max_length=20)
    fecha_nac = forms.DateField(label="Fecha de nacimiento")
