from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from apps.auditoria.models import EventoReserva
from apps.espacios.models import Espacio
from apps.reservas.models import Reserva
from apps.reservas.services import cancelar_reserva_administrativa
from apps.usuarios.models import Usuario
from apps.usuarios.roles import ADMINISTRADOR, GESTOR, SOLICITANTE

pytestmark = [pytest.mark.integration, pytest.mark.django_db]
BOGOTA = ZoneInfo("America/Bogota")


def usuario(email, rol=SOLICITANTE):
    item = Usuario.objects.create_user(
        email=email, nombre=email.split("@")[0], password="clave-segura-123"
    )
    item.groups.add(Group.objects.get(name=rol))
    return item


def escenario():
    propietario = usuario("propietario@example.edu")
    espacio = Espacio.objects.create(
        nombre="Sala Cancelación Administrativa",
        tipo=Espacio.Tipo.AUDITORIO,
        ubicacion="Bloque L",
        capacidad=60,
    )
    inicio = datetime(2031, 3, 3, 10, 0, tzinfo=BOGOTA)
    reserva = Reserva.objects.create(
        solicitante=propietario,
        espacio=espacio,
        inicio=inicio,
        fin=inicio + timedelta(hours=1),
        estado=Reserva.Estado.APROBADA,
    )
    return reserva


@pytest.mark.parametrize("rol", [GESTOR, ADMINISTRADOR])
def test_gestor_y_administrador_cancelan_cualquier_reserva(rol):
    reserva = escenario()
    actor = usuario(f"{rol.replace(' ', '').lower()}@example.edu", rol)
    cancelar_reserva_administrativa(
        reserva_id=reserva.pk,
        actor=actor,
        motivo="Mantenimiento",
        ahora=reserva.inicio - timedelta(minutes=1),
    )
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.CANCELADA
    evento = EventoReserva.objects.get(reserva=reserva)
    assert evento.responsable == actor
    assert evento.detalle == "Mantenimiento"


def test_solicitante_no_puede_cancelar_administrativamente(client):
    reserva = escenario()
    actor = usuario("intruso@example.edu")
    client.force_login(actor)
    response = client.post(
        f"/reservas/{reserva.pk}/cancelar-administrativamente/",
        {"motivo": "Intento"},
    )
    assert response.status_code == 403
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.APROBADA


@pytest.mark.parametrize("motivo", ["", "x" * 1001])
def test_motivo_administrativo_debe_tener_entre_uno_y_mil(motivo):
    reserva = escenario()
    actor = usuario("gestor@example.edu", GESTOR)
    with pytest.raises(ValidationError):
        cancelar_reserva_administrativa(
            reserva_id=reserva.pk, actor=actor, motivo=motivo
        )
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.APROBADA


@pytest.mark.parametrize("desplazamiento", [timedelta(0), timedelta(seconds=1)])
def test_cancelacion_administrativa_no_procede_en_o_despues_del_inicio(desplazamiento):
    reserva = escenario()
    actor = usuario("gestor@example.edu", GESTOR)
    with pytest.raises(ValidationError, match="antes del inicio"):
        cancelar_reserva_administrativa(
            reserva_id=reserva.pk,
            actor=actor,
            motivo="Mantenimiento",
            ahora=reserva.inicio + desplazamiento,
        )


def test_fallo_de_evento_revierte_cancelacion_administrativa(monkeypatch):
    reserva = escenario()
    actor = usuario("gestor@example.edu", GESTOR)

    def fallar(**kwargs):
        raise RuntimeError("fallo simulado")

    monkeypatch.setattr("apps.auditoria.services.registrar_evento", fallar)
    with pytest.raises(RuntimeError):
        cancelar_reserva_administrativa(
            reserva_id=reserva.pk,
            actor=actor,
            motivo="Mantenimiento",
            ahora=reserva.inicio - timedelta(minutes=1),
        )
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.APROBADA
    assert not EventoReserva.objects.filter(reserva=reserva).exists()
