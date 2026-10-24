from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.auditoria.models import EventoReserva
from apps.espacios.models import Espacio, HorarioEspacio
from apps.reservas.models import Reserva
from apps.reservas.services import ConflictoReserva, aprobar_reserva
from apps.usuarios.models import Usuario
from apps.usuarios.roles import GESTOR

pytestmark = [pytest.mark.integration, pytest.mark.django_db]
BOGOTA = ZoneInfo("America/Bogota")


def usuario(email, *, gestor=False):
    item = Usuario.objects.create_user(
        email=email, nombre=email.split("@")[0], password="clave-segura-123"
    )
    if gestor:
        item.groups.add(Group.objects.get(name=GESTOR))
    return item


def espacio(nombre):
    item = Espacio.objects.create(
        nombre=nombre,
        tipo=Espacio.Tipo.LABORATORIO,
        ubicacion=f"Bloque {nombre}",
        capacidad=20,
    )
    HorarioEspacio.objects.create(
        espacio=item,
        dia_semana=HorarioEspacio.DiaSemana.LUNES,
        hora_inicio=time(8),
        hora_fin=time(18),
    )
    return item


def solicitud(
    solicitante,
    lugar,
    inicio,
    *,
    estado=Reserva.Estado.PENDIENTE,
    duracion=timedelta(hours=2),
):
    return Reserva.objects.create(
        solicitante=solicitante,
        espacio=lugar,
        inicio=inicio,
        fin=inicio + duracion,
        estado=estado,
    )


def test_aprobacion_valida_confirma_el_estado():
    gestor = usuario("gestor@example.edu", gestor=True)
    solicitante = usuario("solicitante@example.edu")
    inicio = datetime(2031, 2, 3, 10, 0, tzinfo=BOGOTA)
    reserva = solicitud(solicitante, espacio("A"), inicio)

    resultado = aprobar_reserva(reserva_id=reserva.pk, actor=gestor)

    assert resultado.estado == Reserva.Estado.APROBADA
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.APROBADA


def test_aprobacion_rechaza_solicitud_legada_superior_a_cuatro_horas():
    gestor = usuario("gestor.legado@example.edu", gestor=True)
    solicitante = usuario("solicitante.legado@example.edu")
    inicio = datetime(2031, 2, 3, 10, 0, tzinfo=BOGOTA)
    reserva = solicitud(
        solicitante,
        espacio("Legada"),
        inicio,
        duracion=timedelta(hours=4, minutes=1),
    )

    with pytest.raises(ValidationError, match="máxima es de cuatro horas"):
        aprobar_reserva(reserva_id=reserva.pk, actor=gestor)

    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.PENDIENTE
    assert not EventoReserva.objects.filter(reserva=reserva).exists()


def test_aprobacion_de_exactamente_cuatro_horas_registra_un_evento():
    gestor = usuario("gestor.cuatro@example.edu", gestor=True)
    solicitante = usuario("solicitante.cuatro@example.edu")
    inicio = datetime(2031, 2, 3, 10, 0, tzinfo=BOGOTA)
    reserva = solicitud(
        solicitante,
        espacio("Cuatro horas"),
        inicio,
        duracion=timedelta(hours=4),
    )

    resultado = aprobar_reserva(reserva_id=reserva.pk, actor=gestor)

    assert resultado.estado == Reserva.Estado.APROBADA
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.APROBADA
    evento = EventoReserva.objects.get(reserva=reserva)
    assert evento.accion == EventoReserva.Accion.APROBACION
    assert evento.responsable == gestor


def test_disponibilidad_modificada_conserva_la_solicitud_pendiente():
    gestor = usuario("gestor@example.edu", gestor=True)
    solicitante = usuario("solicitante@example.edu")
    otro = usuario("otro@example.edu")
    inicio = datetime(2031, 2, 3, 10, 0, tzinfo=BOGOTA)
    lugar = espacio("A")
    reserva = solicitud(solicitante, lugar, inicio)
    solicitud(otro, lugar, inicio + timedelta(hours=1), estado=Reserva.Estado.APROBADA)

    with pytest.raises(ConflictoReserva, match="ya no está disponible"):
        aprobar_reserva(reserva_id=reserva.pk, actor=gestor)

    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.PENDIENTE


def test_fallo_durante_guardado_revierte_el_estado(monkeypatch):
    gestor = usuario("gestor@example.edu", gestor=True)
    solicitante = usuario("solicitante@example.edu")
    inicio = datetime(2031, 2, 3, 10, 0, tzinfo=BOGOTA)
    reserva = solicitud(solicitante, espacio("A"), inicio)
    guardado_original = Reserva.save

    def guardar_y_fallar(self, *args, **kwargs):
        guardado_original(self, *args, **kwargs)
        raise RuntimeError("fallo simulado posterior a la escritura")

    monkeypatch.setattr(Reserva, "save", guardar_y_fallar)
    with pytest.raises(RuntimeError):
        aprobar_reserva(reserva_id=reserva.pk, actor=gestor)

    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.PENDIENTE


def test_error_de_integridad_se_traduce_sin_detalles_internos(monkeypatch):
    gestor = usuario("gestor@example.edu", gestor=True)
    solicitante = usuario("solicitante@example.edu")
    inicio = datetime(2031, 2, 3, 10, 0, tzinfo=BOGOTA)
    reserva = solicitud(solicitante, espacio("A"), inicio)

    def fallar(*args, **kwargs):
        raise IntegrityError("nombre_secreto_de_restriccion")

    monkeypatch.setattr(Reserva, "save", fallar)
    with pytest.raises(ConflictoReserva) as capturado:
        aprobar_reserva(reserva_id=reserva.pk, actor=gestor)

    assert "nombre_secreto" not in str(capturado.value)
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.PENDIENTE
