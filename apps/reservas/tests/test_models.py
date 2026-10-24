from datetime import datetime, timedelta

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.espacios.models import Espacio
from apps.reservas.models import Reserva
from apps.usuarios.models import Usuario

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def crear_datos_base():
    usuario = Usuario.objects.create_user(
        email="solicitante@example.edu",
        nombre="Solicitante",
        password="clave-segura-123",
    )
    espacio = Espacio.objects.create(
        nombre="Laboratorio 201",
        tipo=Espacio.Tipo.LABORATORIO,
        ubicacion="Bloque B",
        capacidad=25,
    )
    return usuario, espacio


def test_reserva_se_persiste_con_estado_pendiente_y_fecha_de_creacion():
    usuario, espacio = crear_datos_base()
    inicio = timezone.make_aware(datetime(2026, 11, 2, 8, 0))

    reserva = Reserva.objects.create(
        solicitante=usuario,
        espacio=espacio,
        inicio=inicio,
        fin=inicio + timedelta(hours=2),
    )

    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.PENDIENTE
    assert reserva.fecha_creacion is not None
    assert reserva.solicitante == usuario
    assert reserva.espacio == espacio


def test_base_de_datos_rechaza_fin_igual_o_anterior_al_inicio():
    usuario, espacio = crear_datos_base()
    inicio = timezone.make_aware(datetime(2026, 11, 2, 8, 0))

    for fin in (inicio, inicio - timedelta(minutes=1)):
        with pytest.raises(IntegrityError), transaction.atomic():
            Reserva.objects.create(
                solicitante=usuario,
                espacio=espacio,
                inicio=inicio,
                fin=fin,
            )


def test_relaciones_protegidas_impiden_borrar_datos_referenciados():
    usuario, espacio = crear_datos_base()
    inicio = timezone.make_aware(datetime(2026, 11, 2, 8, 0))
    Reserva.objects.create(
        solicitante=usuario,
        espacio=espacio,
        inicio=inicio,
        fin=inicio + timedelta(hours=1),
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        Usuario.objects.filter(pk=usuario.pk).delete()
    with pytest.raises(IntegrityError), transaction.atomic():
        Espacio.objects.filter(pk=espacio.pk).delete()
