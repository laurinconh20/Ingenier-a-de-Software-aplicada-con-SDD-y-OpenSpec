from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.db import IntegrityError, transaction

from apps.espacios.models import Espacio
from apps.reservas.models import Reserva
from apps.usuarios.models import Usuario

pytestmark = [pytest.mark.integration, pytest.mark.django_db]
BOGOTA = ZoneInfo("America/Bogota")


def escenario():
    usuario = Usuario.objects.create_user(
        email="ocupado@example.edu",
        nombre="Usuario Ocupado",
        password="clave-segura-123",
    )
    espacios = [
        Espacio.objects.create(
            nombre=f"Espacio {indice}",
            tipo=Espacio.Tipo.AUDITORIO,
            ubicacion=f"Bloque {indice}",
            capacidad=40,
        )
        for indice in range(2)
    ]
    inicio = datetime(2031, 2, 3, 10, 0, tzinfo=BOGOTA)
    return usuario, espacios, inicio


def crear(usuario, espacio, inicio, fin):
    return Reserva.objects.create(
        solicitante=usuario,
        espacio=espacio,
        inicio=inicio,
        fin=fin,
        estado=Reserva.Estado.APROBADA,
    )


def test_postgresql_rechaza_solape_del_solicitante_en_espacios_distintos():
    usuario, espacios, inicio = escenario()
    crear(usuario, espacios[0], inicio, inicio + timedelta(hours=2))

    with pytest.raises(IntegrityError), transaction.atomic():
        crear(
            usuario,
            espacios[1],
            inicio + timedelta(hours=1),
            inicio + timedelta(hours=3),
        )


def test_postgresql_permite_reservas_adyacentes_del_solicitante():
    usuario, espacios, inicio = escenario()
    crear(usuario, espacios[0], inicio, inicio + timedelta(hours=2))
    crear(
        usuario,
        espacios[1],
        inicio + timedelta(hours=2),
        inicio + timedelta(hours=3),
    )
    assert Reserva.objects.filter(estado=Reserva.Estado.APROBADA).count() == 2


def test_usuarios_distintos_pueden_coincidir_en_espacios_distintos():
    usuario, espacios, inicio = escenario()
    otro = Usuario.objects.create_user(
        email="otro@example.edu", nombre="Otro", password="clave-segura-123"
    )
    crear(usuario, espacios[0], inicio, inicio + timedelta(hours=2))
    crear(otro, espacios[1], inicio, inicio + timedelta(hours=2))
    assert Reserva.objects.filter(estado=Reserva.Estado.APROBADA).count() == 2
