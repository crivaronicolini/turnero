from django.urls import path
from allauth.account.views import SignupView
from .forms import PacienteSignUpForm, DoctorSignUpForm, SecretarioSignUpForm

urlpatterns = [
    path("signup/paciente/", SignupView.as_view(form_class=PacienteSignUpForm), name="paciente_signup"),
    path("signup/doctor/", SignupView.as_view(form_class=DoctorSignUpForm), name="doctor_signup"),
    path("signup/secretario/", SignupView.as_view(form_class=SecretarioSignUpForm), name="secretario_signup"),
]
