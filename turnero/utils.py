from collections import defaultdict
from .models import Plan, ObraSocial


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
