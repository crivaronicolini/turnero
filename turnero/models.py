# # pyright: basic
# from django.db import models
#
#
# class Sedes(models.Model):
#     nombre = models.CharField(max_length=50)
#     direccion = models.CharField(max_length=255)
#     horarios = models.CharField(max_length=255)
#     telefono = models.CharField(max_length=20)
#
#
# class Especialidades(models.Model):
#     especialidad = models.CharField(max_length=255)
#
#
# class Doctores(models.Model):
#     nombre = models.CharField(max_length=255)
#     apellido = models.CharField(max_length=255)
#     dni = models.CharField(max_length=20, unique=True)
#
#
# class Doctor_especialidad(models.Model):
#     id_doctor = models.ForeignKey(Doctores, on_delete=models.CASCADE, related_name = "doctor_especialidad")
#     id_especialidad = models.ForeignKey(Especialidades, on_delete=models.CASCADE, related_name = "especialidad_doctor")
#
#
# class Pacientes(models.Model):
#     nombre = models.CharField(max_length=255)
#     apellido = models.CharField(max_length=255)
#     dni = models.CharField(max_length=20, unique=True)
#     fecha_nac = models.DateField()
#     email = models.EmailField(unique=True)
#     passwd = models.CharField(max_length=255)
#     rol = models.CharField(
#         max_length=20, choices={"pac": "Paciente", "sec": "Secretario"}
#     )
#     telefono = models.phoneNumberField()
#
#
# class Turnos(models.Model):
#     id_sede = models.ForeignKey(Sedes, on_delete=models.CASCADE, related_name="turnos_por_sede")
#     id_doctor = models.ForeignKey(Doctores, on_delete=models.CASCADE, related_name="turnos_por_doctor")
#     id_paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE, related_name="turnos_por_paciente")
#     id_especialidad = models.ForeignKey(
#         Especialidades, on_delete=models.CASCADE, related_name="turnos_por_especialidad"
#     )
#     horario = models.DateTimeField()
#     modalidad = models.CharField(
#         max_length=20, choices={"prescencial": "Prescencial", "online": "Online"}
#     )
#     estado = models.CharField(
#         max_length=50,
#         choices={
#             "cancelado": "Cancelado",
#             "pendiente": "Pendiente",
#             "ocupado": "Ocupado",
#             "completado": "Completado",
#             "no_asistio": "No asistió",
#         },
#         default="pendiente",
#     )
#
#     class Meta:
#         constraints = [
#             # un doctor no puede tener varios turnos en el mismo horario
#             models.UniqueConstraint(
#                 fields=["id_doctor", "horario", "id_sede"],
#                 name="unique_doctor_horario_turnos",
#             )
#         ]
