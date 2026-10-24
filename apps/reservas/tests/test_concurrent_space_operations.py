from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, time, timedelta
from threading import Barrier
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import close_old_connections

from apps.auditoria.models import EventoReserva
from apps.espacios.models import Espacio, HorarioEspacio
from apps.espacios.services import desactivar_espacio, guardar_horario
from apps.reservas.models import Reserva
from apps.reservas import services as reservation_services
from apps.reservas.services import (
    ConflictoReserva,
    aprobar_reserva,
    cancelar_reserva_propia,
)
from apps.usuarios.models import Usuario
from apps.usuarios.roles import GESTOR

pytestmark = [pytest.mark.concurrency, pytest.mark.django_db(transaction=True)]
BOGOTA = ZoneInfo("America/Bogota")


def escenario(indice):
    gestor = Usuario.objects.create_user(
        email=f"gestor-operacion-{indice}@example.edu",
        nombre="Gestor",
        password="clave-segura-123",
    )
    gestor.groups.add(Group.objects.get(name=GESTOR))
    solicitante = Usuario.objects.create_user(
        email=f"solicitante-operacion-{indice}@example.edu",
        nombre="Solicitante",
        password="clave-segura-123",
    )
    espacio = Espacio.objects.create(
        nombre=f"Sala Operación {indice}",
        tipo=Espacio.Tipo.SALA_COMPUTO,
        ubicacion=f"Bloque O{indice}",
        capacidad=20,
    )
    horario = HorarioEspacio.objects.create(
        espacio=espacio,
        dia_semana=HorarioEspacio.DiaSemana.LUNES,
        hora_inicio=time(8),
        hora_fin=time(18),
    )
    inicio = datetime(2031, 2, 3, 10, tzinfo=BOGOTA)
    reserva = Reserva.objects.create(
        solicitante=solicitante,
        espacio=espacio,
        inicio=inicio,
        fin=inicio + timedelta(hours=2),
    )
    return gestor, solicitante, espacio, horario, reserva


def ejecutar_en_paralelo(*operaciones):
    barrera = Barrier(len(operaciones))

    def ejecutar(operacion):
        close_old_connections()
        try:
            barrera.wait(timeout=10)
            operacion()
            return "ok"
        except (ValidationError, ConflictoReserva) as error:
            return f"conflicto:{error.messages[0]}"
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=len(operaciones)) as ejecutor:
        futuros = [ejecutor.submit(ejecutar, operacion) for operacion in operaciones]
        return [futuro.result(timeout=15) for futuro in futuros]


def test_aprobacion_concurrente_con_cancelacion_confirma_una_transicion(monkeypatch):
    gestor, solicitante, _, _, reserva = escenario("cancelacion")
    barrera_lectura = Barrier(2)
    lectura_original = reservation_services._leer_referencia_reserva

    def leer_y_sincronizar(reserva_id):
        referencia = lectura_original(reserva_id)
        barrera_lectura.wait(timeout=10)
        return referencia

    monkeypatch.setattr(
        reservation_services, "_leer_referencia_reserva", leer_y_sincronizar
    )
    resultados = ejecutar_en_paralelo(
        lambda: aprobar_reserva(reserva_id=reserva.pk, actor=gestor),
        lambda: cancelar_reserva_propia(reserva_id=reserva.pk, actor=solicitante),
    )

    reserva.refresh_from_db()
    assert resultados.count("ok") == 1
    assert reserva.estado in {Reserva.Estado.APROBADA, Reserva.Estado.CANCELADA}
    assert EventoReserva.objects.filter(reserva=reserva).count() == 1


def test_aprobacion_concurrente_con_desactivacion_deja_combinacion_valida():
    gestor, _, espacio, _, reserva = escenario("desactivacion")
    resultados = ejecutar_en_paralelo(
        lambda: aprobar_reserva(reserva_id=reserva.pk, actor=gestor),
        lambda: desactivar_espacio(Espacio.objects.get(pk=espacio.pk)),
    )

    espacio.refresh_from_db()
    reserva.refresh_from_db()
    assert resultados.count("ok") == 1
    assert (espacio.activo, reserva.estado) in {
        (True, Reserva.Estado.APROBADA),
        (False, Reserva.Estado.PENDIENTE),
    }
    assert EventoReserva.objects.filter(reserva=reserva).count() == (
        1 if reserva.estado == Reserva.Estado.APROBADA else 0
    )


def test_aprobacion_concurrente_con_cambio_de_horario_deja_combinacion_valida():
    gestor, _, _, horario, reserva = escenario("horario")
    resultados = ejecutar_en_paralelo(
        lambda: aprobar_reserva(reserva_id=reserva.pk, actor=gestor),
        lambda: guardar_horario(
            espacio_id=horario.espacio_id,
            horario_id=horario.pk,
            datos={
                "dia_semana": HorarioEspacio.DiaSemana.LUNES,
                "hora_inicio": time(8),
                "hora_fin": time(9),
            },
        ),
    )

    horario.refresh_from_db()
    reserva.refresh_from_db()
    assert resultados.count("ok") == 1
    assert (
        reserva.estado == Reserva.Estado.APROBADA and horario.hora_fin == time(18)
    ) or (
        reserva.estado == Reserva.Estado.PENDIENTE and horario.hora_fin == time(9)
    )
    assert EventoReserva.objects.filter(reserva=reserva).count() == (
        1 if reserva.estado == Reserva.Estado.APROBADA else 0
    )
