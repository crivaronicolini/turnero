from turnero.models import ObraSocial, Plan

# Diccionario donde la clave es el nombre de la obra social y el valor es una tupla de planes
obras_sociales_y_planes = {
    'Galeno': ('Oro', 'Plata', 'Bronce'),
    'Swiss Medical': ('SMG 20', 'SMG 30', 'SMG 40'),
    'Medicus': ('AZUL', 'BLANCO', 'AMARILLO'),
    'OSDE': ('210', '310', '410', '510'),
    'Sancor Salud': ('Plan 1000', 'Plan 2000', 'Plan 3000'),
    'Omint': ('Clásico', 'Global', 'Maxi'),
    'Accord Salud': ('3000', '5000', '7000'),
    'Hospital Alemán': ('Plan Clásico', 'Plan Integral'),
    'Plan de Salud del Hospital Italiano': ('Plan Joven', 'Plan Mayor', 'Plan Familiar'),
    'Llamando al Doctor': ('Plan A', 'Plan B', 'Plan C'),
    'Avalian': ('Plan Cerca', 'Plan Integral', 'Plan Superior', 'Plan Selecta'),
}

# Itera sobre el diccionario para crear las instancias en la base de datos
for nombre_os, planes_list in obras_sociales_y_planes.items():
    obra_social, created = ObraSocial.objects.get_or_create(nombre=nombre_os)
    if created:
        print(f"Obra Social '{obra_social.nombre}' creada.")
    else:
        print(f"Obra Social '{obra_social.nombre}' ya existe.")
    for nombre_plan in planes_list:
        plan, created_plan = Plan.objects.get_or_create(nombre=nombre_plan, obra_social=obra_social)
        if created_plan:
            print(f"Plan '{plan.nombre}' para '{obra_social.nombre}' creado.")
        else:
            print(f"Plan '{plan.nombre}' para '{obra_social.nombre}' ya existe.")

print("\nListo")

print("\nPlanes existentes:")
for plan in Plan.objects.all():
    print(f"- {plan.nombre} ({plan.obra_social.nombre})")
