from allauth.account.forms import SignupForm
from django import forms
from .models import ObraSocial, Plan, Especialidad


class PacienteSignUpForm(SignupForm):
    dni = forms.CharField(label="DNI", max_length=20)
    fecha_nac = forms.DateField(label="Fecha de nacimiento")
    nro_afiliado = forms.CharField(label="Nro. de afiliado", max_length=20)
    obra_social = forms.ModelChoiceField(queryset=ObraSocial.objects.all(), label="Obra Social")
    plan = forms.ModelChoiceField(queryset=Plan.objects.none(), label="Plan")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "obra_social" in self.data:
            try:
                obra_id = int(self.data.get("obra_social"))
                self.fields["plan"].queryset = Plan.objects.filter(obra_social_id=obra_id)
            except (ValueError, TypeError):
                pass
        elif self.initial.get("obra_social"):
            obra = self.initial.get("obra_social")
            self.fields["plan"].queryset = Plan.objects.filter(obra_social=obra)



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
