from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Sede, User, ObraSocial, Plan, Paciente, Doctor,
    Especialidad, Doctor_especialidad, Secretario, Turno
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for the User model."""
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Extra info", {"fields": ("rol", "dni", "fecha_nac")}),
    )
    list_display = ("username", "email", "nombre", "apellidos", "rol", "is_staff")
    list_filter = ("rol", "is_staff", "is_superuser")
    search_fields = ("username", "email", "dni", "nombre", "apellidos")


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    """Custom admin for the Paciente model."""
    list_display = ('get_nombre', 'get_apellidos', 'get_dni', 'plan', 'nro_afiliado')
    search_fields = ('user__nombre', 'user__apellidos', 'user__dni', 'nro_afiliado')
    # Performance optimization to fetch related user and plan in one query
    list_select_related = ('user', 'plan')

    @admin.display(description='Nombre', ordering='user__nombre')
    def get_nombre(self, obj):
        return obj.user.nombre

    @admin.display(description='Apellidos', ordering='user__apellidos')
    def get_apellidos(self, obj):
        return obj.user.apellidos

    @admin.display(description='DNI', ordering='user__dni')
    def get_dni(self, obj):
        return obj.user.dni


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Custom admin for the Doctor model."""
    list_display = ('get_nombre', 'get_apellidos', 'get_dni', 'matricula')
    search_fields = ('user__nombre', 'user__apellidos', 'user__dni', 'matricula')
    list_select_related = ('user',)

    @admin.display(description='Nombre', ordering='user__nombre')
    def get_nombre(self, obj):
        return obj.user.nombre

    @admin.display(description='Apellidos', ordering='user__apellidos')
    def get_apellidos(self, obj):
        return obj.user.apellidos

    @admin.display(description='DNI', ordering='user__dni')
    def get_dni(self, obj):
        return obj.user.dni


@admin.register(Secretario)
class SecretarioAdmin(admin.ModelAdmin):
    """Custom admin for the Secretario model."""
    list_display = ('get_nombre', 'get_apellidos', 'get_dni')
    search_fields = ('user__nombre', 'user__apellidos', 'user__dni')
    list_select_related = ('user',)

    @admin.display(description='Nombre', ordering='user__nombre')
    def get_nombre(self, obj):
        return obj.user.nombre

    @admin.display(description='Apellidos', ordering='user__apellidos')
    def get_apellidos(self, obj):
        return obj.user.apellidos

    @admin.display(description='DNI', ordering='user__dni')
    def get_dni(self, obj):
        return obj.user.dni


# --- Other admin classes from before ---

@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion", "telefono")
    search_fields = ("nombre", "direccion")

@admin.register(ObraSocial)
class ObraSocialAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("nombre", "obra_social")
    list_filter = ("obra_social",)
    search_fields = ("nombre",)

@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ("especialidad",)
    search_fields = ("especialidad",)

@admin.register(Doctor_especialidad)
class DoctorEspecialidadAdmin(admin.ModelAdmin):
    list_display = ("id_doctor", "id_especialidad")
    autocomplete_fields = ("id_doctor", "id_especialidad")

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ("fecha", "id_doctor", "id_paciente", "id_sede", "estado")
    list_filter = ("estado", "id_sede", "id_doctor", "id_especialidad")
    search_fields = ("id_paciente__user__apellidos", "id_doctor__user__apellidos")
    date_hierarchy = "fecha"
    autocomplete_fields = ("id_doctor", "id_paciente", "id_sede", "id_especialidad")