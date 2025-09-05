# pyright: basic
from django.db import models
from django.contrib.auth.models import AbstractUser

from turnero.managers import UserManager


class Sede(models.Model):
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255)
    horarios = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre


class User(AbstractUser):
    class Roles(models.TextChoices):
        ROL_PACIENTE = "PA", "Paciente"
        ROL_DOCTOR = "DR", "Doctor"
        ROL_SECTRETARIO = "SE", "Secretario"
        ROL_MANAGER = "MG", "Manager"
        ROL_ADMIN = "AD", "Admininistrador"

    rol = models.CharField(
        max_length=20,
        choices=Roles,
        default=Roles.ROL_PACIENTE,
    )

    dni = models.CharField(max_length=20, unique=True)
    # nombre = models.CharField(max_length=255)
    # apellidos = models.CharField(max_length=255)
    fecha_nac = models.DateField()
    fecha_creado = models.DateField(auto_now_add=True)

    objects = UserManager()
    REQUIRED_FIELDS = ["email", "dni", "fecha_nac", "rol"]

    # def __str__(self):
    #     return f"{self.nombre}, {self.apellidos} - dni: {self.dni}"

    # def get_full_name(self):
    #     return f"{self.nombre} {self.apellidos}".strip()


class ObraSocial(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Plan(models.Model):
    nombre = models.CharField(max_length=100)
    obra_social = models.ForeignKey(
        ObraSocial, on_delete=models.CASCADE, related_name="planes"
    )

    def __str__(self):
        return self.nombre

    class Meta:
        constraints = [
            # un paciente no puede tener varias obras sociales
            models.UniqueConstraint(
                fields=("nombre", "obra_social"),
                name="unique_paciente_obra_social",
            )
        ]


class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nro_afiliado = models.CharField(max_length=20)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="pacientes")

    def __str__(self):
        return f"{self.user}"


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.user} - {self.matricula}"


class Especialidad(models.Model):
    especialidad = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.especialidad


class Doctor_especialidad(models.Model):
    id_doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="doctor_especialidad"
    )
    id_especialidad = models.ForeignKey(
        Especialidad, on_delete=models.CASCADE, related_name="especialidad_doctor"
    )

    def __str__(self):
        return f"{self.id_doctor} - {self.id_especialidad}"


class Secretario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # TODO: manejo de doctores


class Turno(models.Model):
    id_sede = models.ForeignKey(
        Sede, on_delete=models.CASCADE, related_name="turnos_por_sede"
    )
    id_doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="turnos_por_doctor"
    )
    id_paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="turnos_por_paciente",
        null=True,
        blank=True,
    )
    id_especialidad = models.ForeignKey(
        Especialidad, on_delete=models.CASCADE, related_name="turnos_por_especialidad"
    )
    fecha = models.DateTimeField()

    duracion = models.IntegerField()

    estado = models.CharField(
        max_length=50,
        choices={
            "cancelado": "Cancelado",
            "pendiente": "Pendiente",
            "ocupado": "Ocupado",
            "completado": "Completado",
            "no_asistio": "No asistió",
        },
        default="pendiente",
    )

    class Meta:
        constraints = [
            # un doctor no puede tener varios turnos en el mismo horario
            models.UniqueConstraint(
                fields=["id_doctor", "fecha", "id_sede"],
                name="unique_doctor_horario_turnos",
            )
        ]
