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
    usuarios = [
        Usuario.objects.create_user(
            email=f"usuario{indice}@example.edu",
            nombre=f"Usuario {indice}",
            password="clave-segura-123",
        )
        for indice in range(2)
    ]
    espacio = Espacio.objects.create(
        nombre="Laboratorio Exclusión",
        tipo=Espacio.Tipo.LABORATORIO,
        ubicacion="Bloque G",
        capacidad=12,
    )
    inicio = datetime(2031, 2, 3, 10, 0, tzinfo=BOGOTA)
    return usuarios, espacio, inicio


def crear(usuario, espacio, inicio, fin, estado=Reserva.Estado.APROBADA):
    return Reserva.objects.create(
        solicitante=usuario,
        espacio=espacio,
        inicio=inicio,
        fin=fin,
        estado=estado,
    )


def test_postgresql_rechaza_aprobadas_superpuestas_para_el_mismo_espacio():
    usuarios, espacio, inicio = escenario()
    crear(usuarios[0], espacio, inicio, inicio + timedelta(hours=2))

    with pytest.raises(IntegrityError), transaction.atomic():
        crear(
            usuarios[1],
            espacio,
            inicio + timedelta(hours=1),
            inicio + timedelta(hours=3),
        )


def test_postgresql_permite_aprobadas_adyacentes_para_el_mismo_espacio():
    usuarios, espacio, inicio = escenario()
    crear(usuarios[0], espacio, inicio, inicio + timedelta(hours=2))
    crear(
        usuarios[1],
        espacio,
        inicio + timedelta(hours=2),
        inicio + timedelta(hours=3),
    )
    assert Reserva.objects.filter(estado=Reserva.Estado.APROBADA).count() == 2


def test_restriccion_parcial_no_bloquea_solicitudes_pendientes_superpuestas():
    usuarios, espacio, inicio = escenario()
    crear(usuarios[0], espacio, inicio, inicio + timedelta(hours=2))
    crear(
        usuarios[1],
        espacio,
        inicio + timedelta(hours=1),
        inicio + timedelta(hours=3),
        estado=Reserva.Estado.PENDIENTE,
    )
    assert Reserva.objects.count() == 2
