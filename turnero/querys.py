from .models import ObraSocial, Sede
from functools import lru_cache


# TODO: limpiar el cache cuando esto se actualiza
@lru_cache
def get_planes():
    return {
        obra_social.id: list(obra_social.planes.values("id", "nombre"))
        for obra_social in ObraSocial.objects.all()
    }


@lru_cache
def get_sedes():
    return {sede.nombre: sede for sede in Sede.objects.all()}
