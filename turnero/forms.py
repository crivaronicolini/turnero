from allauth.account.forms import SignupForm
from django import forms
from .models import Especialidad, ObraSocial, Plan
from turnero import widgets


class PacienteSignUpForm(SignupForm):
    nombre = forms.CharField(label="Nombre", max_length=255)
    apellidos = forms.CharField(label="Apellidos", max_length=255)
    dni = forms.CharField(label="DNI", max_length=20)
    fecha_nac = forms.DateField(
        label="Fecha de nacimiento",
        widget=forms.DateInput(
            attrs={"placeholder": "dd/mm/aaaa", "type": "date", "class": "input"}
        ),
    )
    nro_afiliado = forms.CharField(label="Nro. de afiliado", max_length=20)

    obra_social = forms.ModelChoiceField(
        label="Obra Social",
        queryset=ObraSocial.objects.all(),
        empty_label="Seleccione una Obra Social",
    )
    plan = forms.ModelChoiceField(
        label="Plan", queryset=Plan.objects.all(), empty_label="Seleccione un Plan"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        field_order = [
            "email",
            "password1",
            "nombre",
            "apellidos",
            "dni",
            "fecha_nac",
            "nro_afiliado",
            "obra_social",
            "plan",
        ]
        self.order_fields(field_order)


class DoctorSignUpForm(SignupForm):
    nombre = forms.CharField(label="Nombre", max_length=255)
    apellidos = forms.CharField(label="Apellidos", max_length=255)
    dni = forms.CharField(label="DNI", max_length=20)
    fecha_nac = forms.DateField(
        label="Fecha de nacimiento",
        widget=forms.DateInput(
            attrs={"placeholder": "dd/mm/aaaa", "type": "date", "class": "input"}
        ),
    )
    matricula = forms.CharField(label="Matrícula", max_length=30)
    especialidades = forms.ModelMultipleChoiceField(
        queryset=Especialidad.objects.all(),
        widget=widgets.MultiSelectWidget(
            attrs={"placeholder": "Seleccione las Especialidades que atiende"}
        ),
        label="Especialidades",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        field_order = [
            "email",
            "password1",
            "nombre",
            "apellidos",
            "dni",
            "fecha_nac",
            "matricula",
            "especialidades",
        ]
        self.order_fields(field_order)


class SecretarioSignUpForm(SignupForm):
    dni = forms.CharField(label="DNI", max_length=20)
    fecha_nac = forms.DateField(label="Fecha de nacimiento")
