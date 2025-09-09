from django.db import models
from django.contrib.auth.models import UserManager as DjangoUserManager


class PacienteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("plan__obra_social")


class UserManager(DjangoUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("El usuario no puede ser nulo")
        if not email:
            raise ValueError("El email no puede ser nulo")

        email = self.normalize_email(email)
        username = self.model.normalize_username(username)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        extra_fields.setdefault("rol", self.model.Roles.ROL_PACIENTE)
        if "dni" not in extra_fields:
            raise ValueError("El dni no puede ser nulo")
        if "fecha_nac" not in extra_fields:
            raise ValueError("La fecha de nacimiento no puede ser nulo")

        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        extra_fields.setdefault("rol", self.model.Roles.ROL_ADMIN)

        return self._create_user(username, email, password, **extra_fields)
