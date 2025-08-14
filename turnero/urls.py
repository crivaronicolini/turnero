from django.urls import path
from allauth.account.views import SignupView
from .forms import DoctorSignUpForm, SecretarioSignUpForm
import turnero.views as views

urlpatterns = [
    path("", views.index, name="index"),

    path("pacientes/", views.pacientes),
    path("pacientes/signup", views.paciente_registro_view, name="pacientes_signup"),

    path("doctores/", views.doctores),
    path("doctores/signup", SignupView.as_view(form_class=DoctorSignUpForm), name="doctores_signup"),

    path("secretaria/", views.secretaria),
    path("secretaria/signup", SignupView.as_view(form_class=SecretarioSignUpForm), name="secretario_signup"),


    path("aber/", views.aber),
]
