from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, time, timedelta
from threading import Barrier
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth.models import Group
from django.db import close_old_connections

from apps.espacios.models import Espacio, HorarioEspacio
from apps.reservas.models import Reserva
from apps.reservas.services import ConflictoReserva, aprobar_reserva
from apps.usuarios.models import Usuario
from apps.usuarios.roles import GESTOR

pytestmark = [pytest.mark.concurrency, pytest.mark.django_db(transaction=True)]
BOGOTA = ZoneInfo("America/Bogota")


def crear_usuario(email, *, gestor=False):
    usuario = Usuario.objects.create_user(
        email=email, nombre=email.split("@")[0], password="clave-segura-123"
    )
    if gestor:
        usuario.groups.add(Group.objects.get(name=GESTOR))
    return usuario


def preparar_carrera(indice):
    actor = crear_usuario(f"gestor{indice}@example.edu", gestor=True)
    espacio = Espacio.objects.create(
        nombre=f"Sala Carrera {indice}",
        tipo=Espacio.Tipo.SALA_COMPUTO,
        ubicacion=f"Bloque C{indice}",
        capacidad=25,
    )
    HorarioEspacio.objects.create(
        espacio=espacio,
        dia_semana=HorarioEspacio.DiaSemana.LUNES,
        hora_inicio=time(8),
        hora_fin=time(18),
    )
    inicio = datetime(2031, 2, 3, 10, 0, tzinfo=BOGOTA)
    reservas = [
        Reserva.objects.create(
            solicitante=crear_usuario(f"solicitante{indice}-{numero}@example.edu"),
            espacio=espacio,
            inicio=inicio,
            fin=inicio + timedelta(hours=2),
        )
        for numero in range(2)
    ]
    return actor.pk, [reserva.pk for reserva in reservas]


def preparar_carrera_mismo_solicitante(indice):
    actor = crear_usuario(f"gestor-solicitante-{indice}@example.edu", gestor=True)
    solicitante = crear_usuario(f"solicitante-compartido-{indice}@example.edu")
    inicio = datetime(2031, 2, 3, 10, 0, tzinfo=BOGOTA)
    reservas = []
    for numero in range(2):
        espacio = Espacio.objects.create(
            nombre=f"Sala Solicitante {indice}-{numero}",
            tipo=Espacio.Tipo.SALA_COMPUTO,
            ubicacion=f"Bloque S{indice}-{numero}",
            capacidad=25,
        )
        HorarioEspacio.objects.create(
            espacio=espacio,
            dia_semana=HorarioEspacio.DiaSemana.LUNES,
            hora_inicio=time(8),
            hora_fin=time(18),
        )
        reservas.append(
            Reserva.objects.create(
                solicitante=solicitante,
                espacio=espacio,
                inicio=inicio,
                fin=inicio + timedelta(hours=2),
            )
        )
    return actor.pk, [reserva.pk for reserva in reservas]


def competir(reserva_id, actor_id, barrera):
    close_old_connections()
    try:
        barrera.wait(timeout=10)
        actor = Usuario.objects.get(pk=actor_id)
        aprobar_reserva(reserva_id=reserva_id, actor=actor)
        return "aprobada"
    except ConflictoReserva as error:
        return f"conflicto:{error.messages[0]}"
    finally:
        close_old_connections()


@pytest.mark.parametrize("repeticion", range(3))
def test_aprobaciones_simultaneas_dejan_como_maximo_una_aprobada(repeticion):
    actor_id, reserva_ids = preparar_carrera(repeticion)
    barrera = Barrier(2)

    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        resultados = list(
            ejecutor.map(
                lambda reserva_id: competir(reserva_id, actor_id, barrera),
                reserva_ids,
            )
        )

    estados = list(
        Reserva.objects.filter(pk__in=reserva_ids).values_list("estado", flat=True)
    )
    assert resultados.count("aprobada") == 1
    assert sum(estado == Reserva.Estado.APROBADA for estado in estados) == 1
    assert sum(estado == Reserva.Estado.PENDIENTE for estado in estados) == 1
    conflicto = next(resultado for resultado in resultados if resultado != "aprobada")
    assert conflicto.startswith("conflicto:")
    assert "constraint" not in conflicto.lower()


@pytest.mark.parametrize("repeticion", range(3))
def test_aprobaciones_simultaneas_del_mismo_solicitante_en_espacios_distintos(
    repeticion,
):
    actor_id, reserva_ids = preparar_carrera_mismo_solicitante(repeticion)
    barrera = Barrier(2)

    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        resultados = list(
            ejecutor.map(
                lambda reserva_id: competir(reserva_id, actor_id, barrera),
                reserva_ids,
            )
        )

    estados = list(
        Reserva.objects.filter(pk__in=reserva_ids).values_list("estado", flat=True)
    )
    assert resultados.count("aprobada") == 1
    assert estados.count(Reserva.Estado.APROBADA) == 1
    assert estados.count(Reserva.Estado.PENDIENTE) == 1
    conflicto = next(resultado for resultado in resultados if resultado != "aprobada")
    assert conflicto.startswith("conflicto:")
    assert "constraint" not in conflicto.lower()
    assert "exclude" not in conflicto.lower()
