from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth.models import Group

from apps.auditoria.models import EventoReserva
from apps.espacios.models import Espacio, HorarioEspacio
from apps.reservas.models import Reserva
from apps.reservas.services import rechazar_reserva
from apps.usuarios.models import Usuario
from apps.usuarios.roles import ADMINISTRADOR, GESTOR, SOLICITANTE

pytestmark = [pytest.mark.functional, pytest.mark.django_db]
BOGOTA = ZoneInfo("America/Bogota")


def usuario(email, rol):
    item = Usuario.objects.create_user(
        email=email, nombre=email.split("@")[0], password="clave-segura-123"
    )
    item.groups.add(Group.objects.get(name=rol))
    return item


def solicitud():
    solicitante = usuario("propietario@example.edu", SOLICITANTE)
    espacio = Espacio.objects.create(
        nombre="Sala Decisiones",
        tipo=Espacio.Tipo.AUDITORIO,
        ubicacion="Bloque H",
        capacidad=80,
    )
    HorarioEspacio.objects.create(
        espacio=espacio,
        dia_semana=HorarioEspacio.DiaSemana.LUNES,
        hora_inicio=time(8),
        hora_fin=time(18),
    )
    inicio = datetime(2031, 2, 3, 10, 0, tzinfo=BOGOTA)
    return Reserva.objects.create(
        solicitante=solicitante,
        espacio=espacio,
        inicio=inicio,
        fin=inicio + timedelta(hours=2),
    )


@pytest.mark.parametrize("rol", [GESTOR, ADMINISTRADOR])
def test_roles_autorizados_deciden_solicitudes_de_cualquier_espacio(client, rol):
    reserva = solicitud()
    actor = usuario(f"{rol.replace(' ', '').lower()}@example.edu", rol)
    client.force_login(actor)

    response = client.post(f"/reservas/{reserva.pk}/aprobar/", {"observacion": "Válida"})

    assert response.status_code == 302
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.APROBADA


def test_solicitante_no_puede_decidir_aunque_envie_peticion_directa(client):
    reserva = solicitud()
    actor = usuario("intruso@example.edu", SOLICITANTE)
    client.force_login(actor)

    response = client.post(f"/reservas/{reserva.pk}/aprobar/", {"observacion": ""})

    assert response.status_code == 403
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.PENDIENTE


@pytest.mark.parametrize("longitud", [0, 1001])
def test_rechazo_exige_motivo_entre_uno_y_mil_caracteres(client, longitud):
    reserva = solicitud()
    actor = usuario("gestor@example.edu", GESTOR)
    client.force_login(actor)

    client.post(f"/reservas/{reserva.pk}/rechazar/", {"motivo": "x" * longitud})

    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.PENDIENTE


def test_rechazo_con_motivo_valido_cambia_el_estado(client):
    reserva = solicitud()
    actor = usuario("gestor@example.edu", GESTOR)
    client.force_login(actor)
    client.post(f"/reservas/{reserva.pk}/rechazar/", {"motivo": "No cumple política"})
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.RECHAZADA


def test_fallo_de_evento_revierte_rechazo(monkeypatch):
    reserva = solicitud()
    actor = usuario("gestor.rollback@example.edu", GESTOR)

    def fallar(**kwargs):
        raise RuntimeError("fallo simulado")

    monkeypatch.setattr("apps.auditoria.services.registrar_evento", fallar)
    with pytest.raises(RuntimeError, match="fallo simulado"):
        rechazar_reserva(
            reserva_id=reserva.pk,
            actor=actor,
            motivo="No cumple la política",
        )

    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.PENDIENTE
    assert not EventoReserva.objects.filter(reserva=reserva).exists()


def test_observacion_de_aprobacion_superior_a_mil_no_cambia_estado(client):
    reserva = solicitud()
    actor = usuario("gestor@example.edu", GESTOR)
    client.force_login(actor)
    client.post(f"/reservas/{reserva.pk}/aprobar/", {"observacion": "x" * 1001})
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.PENDIENTE


@pytest.mark.parametrize("estado", [Reserva.Estado.APROBADA, Reserva.Estado.RECHAZADA, Reserva.Estado.CANCELADA])
def test_no_se_puede_decidir_una_solicitud_no_pendiente(client, estado):
    reserva = solicitud()
    reserva.estado = estado
    reserva.save(update_fields=["estado"])
    actor = usuario("gestor@example.edu", GESTOR)
    client.force_login(actor)

    client.post(f"/reservas/{reserva.pk}/rechazar/", {"motivo": "Intento"})

    reserva.refresh_from_db()
    assert reserva.estado == estado
