import json
import logging
from collections import defaultdict
from datetime import datetime, time, timedelta
from functools import lru_cache

from allauth.account.views import SignupView, login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import DoctorSignUpForm, DoctorTurnosForm, PacienteSignUpForm
from .models import (
    Doctor,
    Doctor_especialidad,
    Especialidad,
    ObraSocial,
    Sede,
    Turno,
    Paciente,
)

from django.shortcuts import get_object_or_404

from django.core.paginator import Paginator

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


def get_initial_context():
    """Helper function to get the context for the main page."""
    return {
        "sedes": Sede.objects.all(),
        "especialidades": Especialidad.objects.all(),
        "doctores": Doctor.objects.select_related("user").all(),
    }


@login_required
def revisar_turno(request):
    turno_id = request.GET.get("turno_id")
    turno = get_object_or_404(
        Turno.objects.select_related("id_doctor__user", "id_sede", "id_especialidad"),
        id=turno_id,
    )

    context = {"turno": turno}

    if request.htmx:
        return render(request, "pacientes/partials/revisar_turno.html", context)

    context.update(get_initial_context())
    return render(request, "pacientes/reservar_turno_inicio.html", context)


@login_required
def confirmar_reserva(request):
    if request.method != "POST":
        return HttpResponse("Método de solicitud no válido.", status=405)

    turno_id = request.POST.get("turno_id")

    try:
        paciente = request.user.paciente
    except Paciente.DoesNotExist:
        return HttpResponse(
            "<div class='alert alert-error'>No tiene un perfil de paciente para reservar un turno.</div>",
            status=403,
        )

    try:
        with transaction.atomic():
            turno = Turno.objects.select_for_update().get(
                id=turno_id, estado="pendiente"
            )
            turno.id_paciente = paciente
            turno.estado = "ocupado"
            turno.save()
            return render(
                request, "pacientes/partials/reserva_confirmada.html", {"turno": turno}
            )
    except Turno.DoesNotExist:
        return HttpResponse(
            "<div class='alert alert-warning'>Lo sentimos, este turno ya no está disponible. Por favor, seleccione otro.</div>"
        )
    except Exception as e:
        logger.error("Error al confirmar la reserva: %s", e)
        return HttpResponse(
            "<div class='alert alert-error'>Ocurrió un error inesperado al confirmar su turno.</div>",
            status=500,
        )


@login_required
def turno_list_view(request):
    """
    This view handles both the initial page load and HTMX filtering
    for the main appointment list.
    """
    # Get filter parameters from the request
    sede_id = request.GET.get("sede")
    especialidad_id = request.GET.get("especialidad")
    doctor_id = request.GET.get("doctor")

    # Start with all available appointments in the future
    now = timezone.now()
    turnos_qs = (
        Turno.objects.filter(estado="pendiente", fecha__gte=now)
        .select_related("id_doctor__user", "id_sede", "id_especialidad")
        .order_by("fecha")
    )

    # Apply filters based on query parameters
    if sede_id:
        turnos_qs = turnos_qs.filter(id_sede_id=sede_id)
    if especialidad_id:
        turnos_qs = turnos_qs.filter(id_especialidad_id=especialidad_id)
    if doctor_id:
        turnos_qs = turnos_qs.filter(id_doctor_id=doctor_id)

    # Paginate the results
    paginator = Paginator(turnos_qs, 20)  # Show 20 appointments per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "selected_sede": sede_id,
        "selected_especialidad": especialidad_id,
        "selected_doctor": doctor_id,
    }

    # For HTMX requests, return only the partial template with the list
    if request.htmx:
        return render(request, "pacientes/partials/lista_turnos.html", context)

    # For initial page load, get all filter options and render the full page
    context["sedes"] = Sede.objects.all()
    context["especialidades"] = Especialidad.objects.all()

    # Prepare doctors data for the custom select component
    all_doctores = Doctor.objects.select_related("user").all()
    doctores_data = [
        {"title": doc.user.get_full_name() or doc.user.username, "value": doc.id}
        for doc in all_doctores
    ]
    context["doctores_json"] = json.dumps(doctores_data)

    return render(request, "pacientes/turno_list_page.html", context)
