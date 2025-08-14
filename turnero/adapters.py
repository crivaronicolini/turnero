import logging
from allauth.account.adapter import DefaultAccountAdapter
from django.db import transaction
from .models import Paciente, Doctor, Secretario, User, Doctor_especialidad, Plan
from .forms import PacienteSignUpForm, DoctorSignUpForm, SecretarioSignUpForm

# Temporary basic config for debugging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s'
)

logger = logging.getLogger(__name__)


class UserAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user.dni = form.cleaned_data.get("dni")
        user.fecha_nac = form.cleaned_data.get("fecha_nac")
        logger.info(f"UserAccountAdapter usuario: {user}")

        user = super().save_user(request, user, form, commit=False)

        if isinstance(form, PacienteSignUpForm):
            user.rol = User.Roles.ROL_PACIENTE
        elif isinstance(form, DoctorSignUpForm):
            user.rol = User.Roles.ROL_DOCTOR
        elif isinstance(form, SecretarioSignUpForm):
            user.rol = User.Roles.ROL_SECTRETARIO

        if commit:
            with transaction.atomic():
                user.save()

                if user.rol == User.Roles.ROL_PACIENTE:
                    plan_id = form.cleaned_data.get("plan")
                    plan_instance = Plan.objects.get(id = plan_id)
                    Paciente.objects.create(
                        user=user,
                        nro_afiliado=form.cleaned_data["nro_afiliado"],
                        plan=plan_instance,
                    )
                elif user.rol == User.Roles.ROL_DOCTOR:
                    doctor = Doctor.objects.create(
                        user=user,
                        matricula=form.cleaned_data["matricula"],
                    )

                    for esp in form.cleaned_data["especialidades"]:
                        Doctor_especialidad.objects.create(
                            id_doctor = doctor,
                            id_especialidad = esp
                        )

                elif user.rol == User.Roles.ROL_SECTRETARIO:
                    Secretario.objects.create(user=user)

        return user

    def get_login_redirect_url(self, request):
        user_rol = request.user.rol
        if user_rol == User.Roles.ROL_PACIENTE:
            path = "/turnos"
        elif user_rol == User.Roles.ROL_DOCTOR:
            path = "/doctores"
        elif user_rol == User.Roles.ROL_SECTRETARIO:
            path = "/secretaria"
        else:
            path = "/"
        return path

    def get_signup_redirect_url(self, request):
        user_rol = request.user.rol
        if user_rol == User.Roles.ROL_PACIENTE:
            path = "/turnos"
        elif user_rol == User.Roles.ROL_DOCTOR:
            path = "/doctores"
        elif user_rol == User.Roles.ROL_SECTRETARIO:
            path = "/secretaria"
        else:
            path = "/"
        return path
