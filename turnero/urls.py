# fmt: off
from django.urls import path
from allauth.account.views import SignupView
import turnero.forms as forms
import turnero.views as views

app_name = "turnero"

urlpatterns = [
    path("", views.index, name="index"),
    # pacientes
    path("turnos/", views.turnos),
    path("pacientes/", views.pacientes),
    path("pacientes/signup", views.PacienteSignupView.as_view(), name="pacientes_signup"),

    # Agent
    path("agent/", views.agent_view, name="agent_view"),
    path("agent/chat/", views.agent_chat, name="agent_chat"),

    # Main patient-facing view to find and book appointments
    path('turnos-disponibles/', views.turno_list_view, name='turno_list_view'),

    # # The rest of the booking flow (partials loaded by HTMX)
    path('revisar-turno/', views.revisar_turno, name='revisar_turno'),
    path('confirmar-reserva/', views.confirmar_reserva, name='confirmar_reserva'),

    # doctores
    path("doctores/", views.doctores),
    path("doctores/signup", views.DoctorSignupView.as_view(), name="doctores_signup"),
    path("doctores/turnos", views.doctores_turnos, name="doctores_turnos"),

    # secretaria
    path("secretaria/", views.secretaria),
    path("secretaria/signup", SignupView.as_view(form_class=forms.SecretarioSignUpForm), name="secretario_signup"),
]
