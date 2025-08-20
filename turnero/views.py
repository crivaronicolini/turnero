import logging
import json
from django.http import HttpResponse
from django.shortcuts import render
from .forms import PacienteSignUpForm, DoctorSignUpForm
from allauth.account.views import SignupView
from .models import ObraSocial


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
