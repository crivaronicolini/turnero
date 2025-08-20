from django.contrib import admin
from .models import User, Especialidad, Doctor, Paciente, Secretario
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

admin.site.register(Especialidad)
admin.site.register(Doctor)
admin.site.register(Paciente)
admin.site.register(Secretario)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Extra info", {"fields": ("rol", "dni", "fecha_nac")}),
    )
    list_display = ("username", "email", "rol", "dni", "fecha_nac", "is_staff")
    search_fields = ("username", "email", "dni")
