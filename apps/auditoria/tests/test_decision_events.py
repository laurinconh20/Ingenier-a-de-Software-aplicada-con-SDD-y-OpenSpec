from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth.models import Group

from apps.auditoria.models import EventoReserva
from apps.espacios.models import Espacio, HorarioEspacio
from apps.reservas.models import Reserva
from apps.reservas.services import ConflictoReserva, aprobar_reserva, rechazar_reserva
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


def escenario():
    actor = usuario("gestor@example.edu", gestor=True)
    solicitante = usuario("solicitante@example.edu")
    espacio = Espacio.objects.create(
        nombre="Sala Eventos",
        tipo=Espacio.Tipo.AUDITORIO,
        ubicacion="Bloque J",
        capacidad=50,
    )
    HorarioEspacio.objects.create(
        espacio=espacio,
        dia_semana=HorarioEspacio.DiaSemana.LUNES,
        hora_inicio=time(8),
        hora_fin=time(18),
    )
    inicio = datetime(2031, 2, 3, 10, 0, tzinfo=BOGOTA)
    reserva = Reserva.objects.create(
        solicitante=solicitante,
        espacio=espacio,
        inicio=inicio,
        fin=inicio + timedelta(hours=2),
    )
    return actor, reserva


def test_aprobacion_crea_exactamente_un_evento_con_observacion():
    actor, reserva = escenario()
    aprobar_reserva(reserva_id=reserva.pk, actor=actor, observacion="Autorizada")
    evento = EventoReserva.objects.get(reserva=reserva)
    assert evento.accion == EventoReserva.Accion.APROBACION
    assert evento.responsable == actor
    assert evento.detalle == "Autorizada"


def test_rechazo_crea_exactamente_un_evento_con_motivo():
    actor, reserva = escenario()
    rechazar_reserva(reserva_id=reserva.pk, actor=actor, motivo="Sin capacidad")
    evento = EventoReserva.objects.get(reserva=reserva)
    assert evento.accion == EventoReserva.Accion.RECHAZO
    assert evento.responsable == actor
    assert evento.detalle == "Sin capacidad"


def test_conflicto_no_crea_evento_exitoso_falso():
    actor, reserva = escenario()
    otro = usuario("otro@example.edu")
    Reserva.objects.create(
        solicitante=otro,
        espacio=reserva.espacio,
        inicio=reserva.inicio,
        fin=reserva.fin,
        estado=Reserva.Estado.APROBADA,
    )
    with pytest.raises(ConflictoReserva):
        aprobar_reserva(reserva_id=reserva.pk, actor=actor)
    assert not EventoReserva.objects.filter(reserva=reserva).exists()


def test_fallo_al_registrar_evento_revierte_el_cambio_de_estado(monkeypatch):
    actor, reserva = escenario()

    def fallar(**kwargs):
        raise RuntimeError("fallo de auditoría")

    monkeypatch.setattr("apps.auditoria.services.registrar_evento", fallar)
    with pytest.raises(RuntimeError):
        aprobar_reserva(reserva_id=reserva.pk, actor=actor)
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.PENDIENTE
    assert not EventoReserva.objects.filter(reserva=reserva).exists()
