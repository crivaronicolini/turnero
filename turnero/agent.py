from typing import Optional

from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from django.utils import timezone
from .models import Turno

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langsmith import traceable

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
checkpointer = InMemorySaver()


@tool
@traceable
def find_available_appointments(
    doctor_name: Optional[str] = None,
    sede_name: Optional[str] = None,
    especialidad_name: Optional[str] = None,
) -> str:
    """
    Finds available future appointments (turnos). Can be filtered by doctor's full name,
    sede (location) name, and especialidad (specialty) name.
    Returns a list of available appointments with their details, or a message if none are found.
    The return markup should be plain, as for a message, don't use Markdown or HTML.
    Separate turnos by a newline. Example:
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
                F("id_doctor__user__nombre"),
                Value(" "),
                F("id_doctor__user__apellidos"),
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
            f"ID: {turno.id}"
            f"Fecha: {turno.fecha.strftime('%Y-%m-%d %H:%M')}, "
            f"Doctor: {turno.id_doctor.user.get_full_name()}, "
            f"Especialidad: {turno.id_especialidad.especialidad}, "
            f"Sede: {turno.id_sede.nombre}"
        )

    return "\n".join(results)


tools = [find_available_appointments]

agent = create_react_agent(
    model=model,
    checkpointer=checkpointer,
    tools=tools,
    debug=True,
)
