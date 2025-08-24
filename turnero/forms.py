from datetime import date, timedelta
from allauth.account.forms import SignupForm
from django import forms
from .models import Especialidad, ObraSocial, Plan
from turnero import widgets
from django.forms import ValidationError


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


class DoctorTurnosForm(forms.Form):
    date_range_data = forms.JSONField(
        label="Rango de fechas",
        error_messages={"required": "Por favor, seleccione un rango de fechas."},
    )
    working_hours_data = forms.JSONField(
        label="Horarios de trabajo",
        error_messages={
            "required": "Por favor, defina al menos un horario de trabajo."
        },
    )

    def clean_working_hours_data(self):
        data = self.cleaned_data.get("working_hours_data")

        if not isinstance(data, list):
            raise ValidationError("Working hours data must be a list.")

        for day_data in data:
            if not isinstance(day_data, dict) or not all(
                key in day_data for key in ["day", "timeRanges"]
            ):
                raise ValidationError(
                    "Each item in working hours must be a dictionary with 'day' and 'timeRanges'."
                )

            for time_range in day_data["timeRanges"]:
                if not all(
                    key in time_range
                    for key in ["start", "end", "appointmentDuration", "sede"]
                ):
                    raise ValidationError(
                        f"Incomplete time range data for {day_data.get('day')}."
                    )

        return data

    def clean_date_range_data(self):
        data = self.cleaned_data.get("date_range_data")
        if not isinstance(data, dict) or not all(
            key in data for key in ["startDate", "endDate"]
        ):
            raise ValidationError(
                "Date range must be a dictionary with 'startDate' and 'endDate' keys."
            )

        try:
            # pasa del iso format de javascript a un date de python
            start_date_str = data.get("startDate").split("T")[0]
            end_date_str = data.get("endDate").split("T")[0]
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
            data["start_date"] = start_date
            data["end_date"] = end_date

            dates_list = [start_date]
            one_day_delta = timedelta(days=1)
            current = start_date
            while current != end_date:
                if current.weekday != 6:
                    dates_list.append(current)
                current = current + one_day_delta

            data["dates_list"] = dates_list

        except (TypeError, ValueError):
            raise ValidationError("Invalid date format. Expected ISO format string.")

        if data["start_date"] >= data["end_date"]:
            raise ValidationError("The start date must be before the end date.")

        return data


class SecretarioSignUpForm(SignupForm):
    dni = forms.CharField(label="DNI", max_length=20)
    fecha_nac = forms.DateField(label="Fecha de nacimiento")
