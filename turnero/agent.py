from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.db import transaction
from django.db.models import CharField, F, Value
from django.db.models.functions import Concat
from django.template.defaultfilters import date as _date
from django.utils import timezone
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import AnyMessage
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.runtime import get_runtime
from langsmith import traceable

from .models import Doctor, Especialidad, Sede, Turno, User

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
checkpointer = InMemorySaver()


@dataclass
class ContextSchema:
    user: User


@tool
@traceable
def find_available_appointments(
    appointment_id: Optional[str | int] = None,
    doctor_name: Optional[str] = None,
    sede_name: Optional[str] = None,
    especialidad_name: Optional[str] = None,
) -> str:
    """
    Finds available future appointments (turnos). Can be filtered by doctor's full name,
    sede (location) name, and especialidad (specialty) name.
    Returns a list of available appointments with their details, or a message if none are found.
    The return markup should be plain, as for a message, don't use Markdown or HTML.
    Separate turnos by a newline and do not include the appointment_id, that is an internal field you will save for future tool calls.
    Example:
    user: hola! quería saber si tienen turnos de urología en caballito
    agent: { nice friendly message }
        Fecha: 11 de septiembre 12:45 horas
        Doctor: Ramón Dominguez
        Especialidad: Urología
        Sede: Caballito

        Fecha: 20 de septiembre 10:30 horas
        Doctor: Juan Gonzalez
        Especialidad: Urología
        Sede: Caballito
    """
    now = timezone.now()
    turnos_qs = (
        Turno.objects.filter(estado="pendiente", fecha__gte=now)
        .select_related("id_doctor__user", "id_sede", "id_especialidad")
        .order_by("fecha")
    )

    if appointment_id:
        turnos_qs = turnos_qs.filter(id=appointment_id)

    if sede_name:
        turnos_qs = turnos_qs.filter(id_sede__nombre__icontains=sede_name)

    if especialidad_name:
        turnos_qs = turnos_qs.filter(
            id_especialidad__especialidad__icontains=especialidad_name
        )

    if doctor_name:
        # Annotate with a full name field to search against
        turnos_qs = turnos_qs.annotate(
            doctor_full_name=Concat(
                F("id_doctor__user__first_name"),
                Value(" "),
                F("id_doctor__user__last_name"),
                output_field=CharField(),
            )
        ).filter(doctor_full_name__icontains=doctor_name)

    # Limit the results to avoid overwhelming the agent
    turnos_qs = turnos_qs[:10]

    if not turnos_qs.exists():
        return "No se encontraron turnos disponibles con los criterios especificados."

    # Format the output for the agent
    results = []
    for turno in turnos_qs:
        results.append(
            f"appointment_id: {turno.id}, "
            f"Fecha: {_date(turno.fecha, 'D j de M, H:i')}, "
            f"Doctor: {turno.id_doctor.user.get_full_name()}, "
            f"Especialidad: {turno.id_especialidad.especialidad}, "
            f"Sede: {turno.id_sede.nombre}"
        )

    return "\n".join(results)


@tool
@traceable
def book_appointment(appointment_id: str):
    """Book an appointment for the user.
    Args:
    appointment_id: str
    """
    runtime = get_runtime(ContextSchema)
    paciente = runtime.context.user.paciente
    try:
        with transaction.atomic():
            turno = Turno.objects.select_for_update().get(
                id=appointment_id, estado="pendiente"
            )
            turno.id_paciente = paciente
            turno.estado = "ocupado"
            turno.save()
            return "Reserva confirmada."
    except Turno.DoesNotExist:
        return "Este turno ya no está disponible."
    except Exception as e:
        return "Ocurrió un error, por favor contacte a soporte."


def fill_prompt_details() -> str:
    """Fetches choices from the DB to fill prompt details for the agent."""
    try:
        doctors = list(
            Doctor.objects.annotate(
                full_name=Concat("user__first_name", Value(" "), "user__last_name")
            ).values_list("full_name", flat=True)
        )
        especialidades = list(
            Especialidad.objects.values_list("especialidad", flat=True)
        )
        sedes = list(Sede.objects.values())
    except Exception:
        # This can happen when running initial migrations before the DB is ready.
        # Fallback to empty lists.
        doctors = []
        especialidades = []
        sedes = []

    return f"""What follows is the current list of sedes (locations), doctors and especialidades that exist at this moment.
    doctors: Full or partial name of the doctor. Must be one of {doctors}.
    sedes: The details of each sede (location) {sedes}.
    especialidades: The exact name of the specialty. Must be one of {especialidades}.
"""


tools = [find_available_appointments, book_appointment]


def prompt(state: AgentState) -> list[AnyMessage]:
    runtime = get_runtime(ContextSchema)
    system_msg = f"""You are Felio, a helpful AI assistant. You help manage health centers around the city of Capital Federal, Buenos Aires, Argentina.
    You will adress every logged in user as {runtime.context.user.first_name}.
    {fill_prompt_details()}
    You will use this information to answer user queries and, if you deem appropiate, use it verbatim as search parameters.

    Appointment booking flow:
        1 - The user asks about available appointments, using the find tool you give them available appointments.
        2 - The user selects an appointment, using the find tool you will search that appointment_id and give them the appointment details so that it may confirm or cancel. 
        3 - Only and only if the user confirms, you will use the booking tool to actually book the appointment an give a success message.
            If the user cancels you will return to the initial state, offering actionable suggestions.

    You will answer and chat only about things concerning our health centers, appointments, and patient management. You must not enternain questions or dialogue about politics, famous figures and historic events."""
    return [{"role": "system", "content": system_msg}] + state["messages"]


agent = create_react_agent(
    model=model,
    checkpointer=checkpointer,
    tools=tools,
    debug=settings.DEBUG,
    prompt=prompt,
    context_schema=ContextSchema,
)
