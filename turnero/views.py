from datetime import time, timedelta, datetime
from functools import lru_cache
import logging
import json
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import PacienteSignUpForm, DoctorSignUpForm, DoctorTurnosForm
from allauth.account.views import SignupView, login_required
from .models import ObraSocial, Doctor_especialidad, Sede, Turno


# Temporary basic config for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
)

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse(b"hola, esto es el index")


def turnos(request):
    return HttpResponse(b"hola, esto es la pagina de turnos")


def doctores(request):
    return HttpResponse(b"hola, esto es la pagina de doctores")


day_to_iso = {
    "Lunes": 0,
    "Martes": 1,
    "Miércoles": 2,
    "Jueves": 3,
    "Viernes": 4,
    "Sábado": 5,
    "Domingo": 6,
}


@lru_cache
def get_sedes():
    return {sede.nombre: sede for sede in Sede.objects.all()}


@login_required
def doctores_turnos(request):
    sedes = get_sedes()
    print(sedes)
    if request.method == "POST":
        form = DoctorTurnosForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            logger.debug("Form data is valid: %s", cleaned_data)

            try:
                doctor = request.user.doctor
            except Doctor.DoesNotExist:
                return render(
                    request,
                    "doctores/turnos.html",
                    {"error": "No estás registrado como doctor."},
                )

            doctor_especialidades = Doctor_especialidad.objects.filter(id_doctor=doctor)
            if not doctor_especialidades.exists():
                return render(
                    request,
                    "doctores/turnos.html",
                    {"error": "No tenes especialidades asignadas."},
                )

            especialidad = doctor_especialidades.first().id_especialidad

            dates_list = cleaned_data.get("date_range_data").get("dates_list")
            working_hours = cleaned_data.get("working_hours_data")

            working_hours_by_day = {
                day_to_iso[day["day"]]: day["timeRanges"] for day in working_hours
            }

            # para cada dia en los dias del rango se fija que horarios hay que cubrir,
            # empezando con el primero crea turnos de la duracion especificada hasta llegar
            # al ultimo turno del dia
            turnos_to_create = []
            for current_date in dates_list:
                weekday_key = current_date.weekday()
                if weekday_key in working_hours_by_day:
                    time_ranges = working_hours_by_day[weekday_key]
                    for time_range in time_ranges:
                        try:
                            sede_str = time_range["sede"]
                            sede_obj = sedes.get(sede_str)
                            if not sede_obj:
                                logger.warning(
                                    "Sede '%s' not found, skipping time range.",
                                    sede_str,
                                )
                                continue

                            duration_str = time_range["appointmentDuration"]
                            duration = timedelta(minutes=int(duration_str))
                            start_time = time.fromisoformat(time_range["start"])
                            end_time = time.fromisoformat(time_range["end"])
                            start_timedate = timezone.make_aware(
                                datetime.combine(current_date, start_time)
                            )
                            end_timedate = timezone.make_aware(
                                datetime.combine(current_date, end_time)
                            )
                            current_slot = start_timedate
                            while current_slot <= end_timedate:
                                turnos_to_create.append(
                                    Turno(
                                        fecha=current_slot,
                                        id_doctor=doctor,
                                        id_sede=sede_obj,
                                        id_especialidad=especialidad,
                                        duracion=duration_str,
                                    )
                                )
                                current_slot += duration
                        except (ValueError, KeyError, TypeError) as e:
                            logger.error(
                                "Skipping invalid time range data: %s. Error: %s",
                                time_range,
                                e,
                            )

            with transaction.atomic():
                try:
                    Turno.objects.bulk_create(turnos_to_create)
                    logger.info(
                        "Successfully created %d turnos for %s",
                        len(turnos_to_create),
                        doctor,
                    )
                    return redirect("/index.html")
                except Exception:
                    # TODO: redirect a error
                    logger.exception(msg="Exception during database transaction")

            return redirect("/index.html")
        else:
            logger.error("Form validation failed: %s", form.errors.as_json())
            return render(request, "doctores/turnos.html", {"form": form})

    return render(
        request, "doctores/turnos.html", {"sedes": [nombre for nombre in sedes.keys()]}
    )


def pacientes(request):
    return HttpResponse(b"hola, esto es la pagina de pacientes")


class DoctorSignupView(SignupView):
    template_name = "account/signup_doctores.html"
    form_class = DoctorSignUpForm


class PacienteSignupView(SignupView):
    template_name = "account/signup_pacientes.html"
    form_class = PacienteSignUpForm

    def get_context_data(self, form=None):
        context = super().get_context_data()
        mapping = {
            obra_social.id: list(obra_social.planes.values("id", "nombre"))
            for obra_social in ObraSocial.objects.all()
        }
        context["obra_social_planes_json"] = json.dumps(mapping)
        return context


def secretaria(request):
    return HttpResponse(b"hola, esto es la pagina de secretaria")


def aber(request):
    return render(request, "dashboard.html")
