from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError

from apps.espacios.models import Espacio, HorarioEspacio
from apps.reservas.models import Reserva
from apps.reservas.services import esta_disponible
from apps.usuarios.models import Usuario

pytestmark = [pytest.mark.integration, pytest.mark.django_db]
BOGOTA = ZoneInfo("America/Bogota")


def escenario(*, activo=True, con_horario=True):
    usuario = Usuario.objects.create_user(
        email="disponibilidad@example.edu",
        nombre="Solicitante",
        password="clave-segura-123",
    )
    espacio = Espacio.objects.create(
        nombre="Sala Disponible",
        tipo=Espacio.Tipo.SALA_COMPUTO,
        ubicacion="Bloque F",
        capacidad=30,
        activo=activo,
    )
    if con_horario:
        HorarioEspacio.objects.create(
            espacio=espacio,
            dia_semana=HorarioEspacio.DiaSemana.LUNES,
            hora_inicio=time(8),
            hora_fin=time(18),
        )
    inicio = datetime(2030, 11, 4, 10, 0, tzinfo=BOGOTA)
    return usuario, espacio, inicio


@pytest.mark.parametrize(
    "estado",
    [Reserva.Estado.PENDIENTE, Reserva.Estado.RECHAZADA, Reserva.Estado.CANCELADA],
)
def test_estados_no_aprobados_no_bloquean(estado):
    usuario, espacio, inicio = escenario()
    Reserva.objects.create(
        solicitante=usuario,
        espacio=espacio,
        inicio=inicio,
        fin=inicio + timedelta(hours=2),
        estado=estado,
    )
    assert esta_disponible(
        espacio=espacio,
        inicio=inicio + timedelta(hours=1),
        fin=inicio + timedelta(hours=3),
    )


def test_reserva_aprobada_superpuesta_bloquea_pero_adyacente_no():
    usuario, espacio, inicio = escenario()
    Reserva.objects.create(
        solicitante=usuario,
        espacio=espacio,
        inicio=inicio,
        fin=inicio + timedelta(hours=2),
        estado=Reserva.Estado.APROBADA,
    )
    assert not esta_disponible(
        espacio=espacio,
        inicio=inicio + timedelta(hours=1),
        fin=inicio + timedelta(hours=3),
    )
    assert esta_disponible(
        espacio=espacio,
        inicio=inicio + timedelta(hours=2),
        fin=inicio + timedelta(hours=3),
    )


def test_disponibilidad_acepta_intervalo_de_exactamente_cuatro_horas():
    _, espacio, inicio = escenario()

    assert esta_disponible(
        espacio=espacio,
        inicio=inicio,
        fin=inicio + timedelta(hours=4),
    )


def test_disponibilidad_rechaza_mas_de_cuatro_horas_dentro_del_horario():
    _, espacio, inicio = escenario()

    with pytest.raises(ValidationError, match="máxima es de cuatro horas"):
        esta_disponible(
            espacio=espacio,
            inicio=inicio,
            fin=inicio + timedelta(hours=4, minutes=1),
        )


@pytest.mark.parametrize(
    ("activo", "con_horario"),
    [(False, True), (True, False)],
)
def test_espacio_inactivo_o_sin_horario_no_esta_disponible(activo, con_horario):
    _, espacio, inicio = escenario(activo=activo, con_horario=con_horario)
    with pytest.raises(ValidationError):
        esta_disponible(
            espacio=espacio, inicio=inicio, fin=inicio + timedelta(hours=1)
        )
