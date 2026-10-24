from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError

from apps.espacios.models import Espacio, HorarioEspacio
from apps.reservas.services import validar_espacio_y_horario

pytestmark = [pytest.mark.integration, pytest.mark.django_db]
BOGOTA = ZoneInfo("America/Bogota")


def crear_espacio(*, activo=True):
    return Espacio.objects.create(
        nombre="Auditorio Central",
        tipo=Espacio.Tipo.AUDITORIO,
        ubicacion="Bloque C",
        capacidad=100,
        activo=activo,
    )


def intervalo(hora_inicio, hora_fin, *, dia=4):
    return (
        datetime(2030, 11, dia, hora_inicio, 0, tzinfo=BOGOTA),
        datetime(2030, 11, dia, hora_fin, 0, tzinfo=BOGOTA),
    )


def habilitar_lunes(espacio):
    HorarioEspacio.objects.create(
        espacio=espacio,
        dia_semana=HorarioEspacio.DiaSemana.LUNES,
        hora_inicio=time(8),
        hora_fin=time(18),
    )


@pytest.mark.parametrize("horas", [(8, 18), (10, 12)])
def test_acepta_intervalo_contenido_incluidos_limites_exactos(horas):
    espacio = crear_espacio()
    habilitar_lunes(espacio)
    validar_espacio_y_horario(espacio, *intervalo(*horas))


def test_rechaza_intervalo_parcialmente_fuera_del_horario():
    espacio = crear_espacio()
    habilitar_lunes(espacio)
    with pytest.raises(ValidationError, match="excede el horario"):
        validar_espacio_y_horario(espacio, *intervalo(17, 19))


def test_rechaza_dia_sin_horario_habilitado():
    espacio = crear_espacio()
    habilitar_lunes(espacio)
    with pytest.raises(ValidationError, match="excede el horario"):
        validar_espacio_y_horario(espacio, *intervalo(10, 12, dia=5))


def test_rechaza_espacio_inactivo_aunque_tenga_horario():
    espacio = crear_espacio(activo=False)
    habilitar_lunes(espacio)
    with pytest.raises(ValidationError, match="no está disponible"):
        validar_espacio_y_horario(espacio, *intervalo(10, 12))
