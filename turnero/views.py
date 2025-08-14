import logging
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import PacienteSignUpForm
from .utils import get_planes_por_obra_social
from allauth.account.adapter import get_adapter

# Temporary basic config for debugging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s'
)

logger = logging.getLogger(__name__)

def index(request):
    return HttpResponse(b"hola, esto es el index")

def doctores(request):
    return HttpResponse(b"hola, esto es la pagina de doctores")

def pacientes(request):
    return HttpResponse(b"hola, esto es la pagina de pacientes")

def paciente_registro_view(request):
    if request.method == 'POST':
        logger.info(f"Received POST request to paciente_registro_view: {request.POST}")
        form = PacienteSignUpForm(request.POST)
        if form.is_valid():
            # try:
            logger.info(f"Form is valid. Cleaned data: {form.cleaned_data}")
            user = form.save(request)
            user.backend = 'allauth.account.auth_backends.AuthenticationBackend'
            login(request, user)
            logger.info(f"User {user.email} created and logged in. Redirecting.")
            return redirect(get_adapter(request).get_signup_redirect_url(request))
            # except IntegrityError as e:
            #     logger.error(f"IntegrityError during user save: {e}")
            #     form.add_error(None, "A user with this username or email may already exist, or another database error occurred.")
        else:
            logger.warning("Form is invalid.")
            logger.warning(f"Form errors: {form.errors.as_json()}")
    else:
        logger.info("Received GET request to paciente_registro_view")
        form = PacienteSignUpForm()

    obras_sociales_data, planes_por_obra_social = get_planes_por_obra_social()

    context = {
        'form': form,
        'obras_sociales_data': obras_sociales_data,
        'planes_data': dict(planes_por_obra_social),
    }
    return render(request, 'signup_pacientes.html', context)

def secretaria(request):
    return HttpResponse(b"hola, esto es la pagina de secretaria")

def aber(request):
    return render(request, "dashboard.html")
