import random
from collections import defaultdict
from datetime import date, datetime, time, timedelta

from django.db import transaction
from django.utils import timezone

from .models import (
    Doctor,
    Doctor_especialidad,
    Especialidad,
    ObraSocial,
    Paciente,
    Plan,
    Sede,
    Turno,
    User,
)


def get_planes_por_obra_social():
    planes_por_obra_social = defaultdict(list)
    obras_sociales_data = []

    for obra in ObraSocial.objects.all().order_by("nombre"):
        obras_sociales_data.append(
            {
                "title": obra.nombre,
                "value": obra.id,
                "disabled": False,
            }
        )

    for plan in Plan.objects.all().order_by("nombre"):
        planes_por_obra_social[plan.obra_social_id].append(
            {
                "value": plan.id,
                "title": plan.nombre,
                "disabled": False,
            }
        )

    return obras_sociales_data, planes_por_obra_social


def seed_database():
    """
    Populates the database with a complete set of test data.
    This function is designed to be safe to run multiple times.
    """
    with transaction.atomic():
        print("--- Starting Database Seeding ---")

        # 1. Seed Obras Sociales and Planes
        print("\nSeeding Obras Sociales and Planes...")
        obras_sociales_y_planes = {
            "Galeno": ("Oro", "Plata", "Bronce"),
            "Swiss Medical": ("SMG 20", "SMG 30", "SMG 40"),
            "Medicus": ("AZUL", "BLANCO", "AMARILLO"),
            "OSDE": ("210", "310", "410", "510"),
            "Sancor Salud": ("Plan 1000", "Plan 2000", "Plan 3000"),
            "Omint": ("Clásico", "Global", "Maxi"),
            "Accord Salud": ("3000", "5000", "7000"),
            "Hospital Alemán": ("Plan Clásico", "Plan Integral"),
            "Plan de Salud del Hospital Italiano": (
                "Plan Joven",
                "Plan Mayor",
                "Plan Familiar",
            ),
            "Llamando al Doctor": ("Plan A", "Plan B", "Plan C"),
            "Avalian": ("Plan Cerca", "Plan Integral", "Plan Superior", "Plan Selecta"),
        }
        for nombre_os, planes_list in obras_sociales_y_planes.items():
            obra_social, _ = ObraSocial.objects.get_or_create(nombre=nombre_os)
            for nombre_plan in planes_list:
                Plan.objects.get_or_create(nombre=nombre_plan, obra_social=obra_social)
        print("Obras Sociales and Planes are ready.")
        all_plans = list(Plan.objects.all())

        # 2. Seed Especialidades
        print("\nSeeding Especialidades...")
        especialidades_nombres = [
            "Cardiología",
            "Traumatología",
            "Pediatría",
            "Neurología",
            "Dermatología",
            "Ginecología",
            "Oftalmología",
            "Otorrinolaringología",
            "Oncología",
            "Endocrinología",
            "Gastroenterología",
            "Reumatología",
            "Nefrología",
            "Urología",
            "Neumonología",
            "Hematología",
            "Psiquiatría",
            "Medicina General",
            "Cirugía General",
            "Medicina Intensiva",
        ]
        especialidades_objects = [
            Especialidad.objects.get_or_create(especialidad=nombre)[0]
            for nombre in especialidades_nombres
        ]
        print(f"{len(especialidades_objects)} Especialidades are ready.")

        # 3. Seed Sedes
        print("\nSeeding Sedes...")
        sedes_data = [
            {
                "nombre": "Abasto",
                "direccion": "Av. Corrientes 3220",
                "telefono": "4883123",
                "horarios": "9 a 22hs, Lunes a Sabado",
            },
            {
                "nombre": "Palermo",
                "direccion": "Av. Santa Fe 3047",
                "telefono": "4299121",
                "horarios": "9 a 22hs, Lunes a Sabado",
            },
            {
                "nombre": "Microcentro",
                "direccion": "Viamonte 1355",
                "telefono": "4988191",
                "horarios": "9 a 22hs, Lunes a Sabado",
            },
            {
                "nombre": "Caballito",
                "direccion": "Av. Rivadavia 5010",
                "telefono": "4903333",
                "horarios": "9 a 22hs, Lunes a Sabado",
            },
            {
                "nombre": "Online",
                "direccion": "Online",
                "telefono": "49991121",
                "horarios": "9 a 22hs, Lunes a Sabado",
            },
        ]
        for data in sedes_data:
            Sede.objects.get_or_create(nombre=data["nombre"], defaults=data)
        all_sedes = list(Sede.objects.all())
        print(f"{len(all_sedes)} Sedes are ready.")

        # 4. Seed test Pacientes
        print("\nSeeding test Pacientes...")
        for i in range(1, 6):
            username = f"paciente{i}"
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password="password123",
                    email=f"paciente{i}@example.com",
                    first_name=f"PacienteNombre{i}",
                    last_name=f"PacienteApellido{i}",
                    dni=f"20000{i}",
                    rol=User.Roles.ROL_PACIENTE,
                    fecha_nac=date(1990, 1, 1),
                )
                Paciente.objects.create(
                    user=user,
                    nro_afiliado=f"P{2000 + i}",
                    plan=random.choice(all_plans),
                )
        print("Test Pacientes created.")

        # 5. Ensure Doctors and their Specialties exist
        print("\nEnsuring Doctors and Specialties exist...")
        for i in range(1, 11):
            user, user_created = User.objects.get_or_create(
                username=f"doctor{i}",
                defaults={
                    "email": f"doctor{i}@example.com",
                    "first_name": f"DoctorNombre{i}",
                    "last_name": f"DoctorApellido{i}",
                    "dni": f"10000{i}",
                    "rol": User.Roles.ROL_DOCTOR,
                    "fecha_nac": date(1980, 1, 1),
                },
            )
            if user_created:
                user.set_password("password123")
                user.save()

            doctor, doctor_created = Doctor.objects.get_or_create(
                user=user, defaults={"matricula": f"M{1000 + i}"}
            )

            if doctor_created:
                specialties_to_assign = random.sample(
                    especialidades_objects, k=random.randint(2, 3)
                )
                relations_to_create = [
                    Doctor_especialidad(id_doctor=doctor, id_especialidad=esp)
                    for esp in specialties_to_assign
                ]
                Doctor_especialidad.objects.bulk_create(relations_to_create)

        # 6. Generate Turnos for ALL doctors for the next month
        print("\nGenerating Turnos for all doctors...")
        deleted_count, _ = Turno.objects.filter(
            estado="pendiente", fecha__lt=timezone.now()
        ).delete()
        if deleted_count:
            print(f"Deleted {deleted_count} old pending appointments.")

        turnos_to_create = []
        all_doctors = Doctor.objects.all()
        today = date.today()

        for doctor in all_doctors:
            doctor_specialties = [
                rel.id_especialidad
                for rel in Doctor_especialidad.objects.filter(id_doctor=doctor)
            ]
            if not doctor_specialties:
                print(
                    f"Skipping Turno generation for Dr. {doctor.user.apellidos} as they have no specialties."
                )
                continue

            for day_offset in range(30):
                current_date = today + timedelta(days=day_offset)
                if current_date.weekday() == 6:
                    continue  # Skip Sundays

                time_ranges = [
                    {"start": time(9, 0), "end": time(12, 0)},
                    {"start": time(14, 0), "end": time(17, 0)},
                ]
                for r in time_ranges:
                    duration = timedelta(minutes=30)
                    start_dt = timezone.make_aware(
                        datetime.combine(current_date, r["start"])
                    )
                    end_dt = timezone.make_aware(
                        datetime.combine(current_date, r["end"])
                    )

                    current_slot = start_dt
                    while current_slot < end_dt:
                        turnos_to_create.append(
                            Turno(
                                fecha=current_slot,
                                id_doctor=doctor,
                                id_sede=random.choice(all_sedes),
                                id_especialidad=random.choice(doctor_specialties),
                                duracion=30,
                            )
                        )
                        current_slot += duration

        # 7. Bulk create all the generated Turno objects
        if turnos_to_create:
            print(f"\nCreating {len(turnos_to_create)} new Turno objects...")
            Turno.objects.bulk_create(turnos_to_create)

        print("\n--- Database Seeding Complete! ---")
