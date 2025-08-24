from django.urls import path
from allauth.account.views import SignupView
import turnero.forms as forms
import turnero.views as views

urlpatterns = [
    path("", views.index, name="index"),
    path("turnos/", views.turnos),
    path("pacientes/", views.pacientes),
    path(
        "pacientes/signup", views.PacienteSignupView.as_view(), name="pacientes_signup"
    ),
    path("doctores/", views.doctores),
    path("doctores/signup", views.DoctorSignupView.as_view(), name="doctores_signup"),
    path("doctores/turnos", views.doctores_turnos, name="doctores_turnos"),
    path("secretaria/", views.secretaria),
    path(
        "secretaria/signup",
        SignupView.as_view(form_class=forms.SecretarioSignUpForm),
        name="secretario_signup",
    ),
    path("aber/", views.aber),
]
