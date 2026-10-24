from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied, ValidationError

from apps.auditoria.models import EventoReserva
from apps.espacios.models import Espacio, HorarioEspacio
from apps.reservas.models import Reserva
from apps.reservas.services import (
    aprobar_reserva,
    cancelar_reserva_propia,
    validar_intervalo_temporal,
)
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


def escenario(*, estado=Reserva.Estado.PENDIENTE, duracion=timedelta(hours=2)):
    propietario = usuario("propietario@example.edu")
    espacio = Espacio.objects.create(
        nombre="Sala Cancelable",
        tipo=Espacio.Tipo.SALA_COMPUTO,
        ubicacion="Bloque K",
        capacidad=20,
    )
    HorarioEspacio.objects.create(
        espacio=espacio,
        dia_semana=HorarioEspacio.DiaSemana.LUNES,
        hora_inicio=time(8),
        hora_fin=time(18),
    )
    inicio = datetime(2031, 2, 3, 10, 0, tzinfo=BOGOTA)
    reserva = Reserva.objects.create(
        solicitante=propietario,
        espacio=espacio,
        inicio=inicio,
        fin=inicio + duracion,
        estado=estado,
    )
    return propietario, reserva


@pytest.mark.parametrize("estado", [Reserva.Estado.PENDIENTE, Reserva.Estado.APROBADA])
def test_propietario_cancela_antes_del_inicio_y_registra_evento(estado):
    propietario, reserva = escenario(estado=estado)
    cancelar_reserva_propia(
        reserva_id=reserva.pk,
        actor=propietario,
        motivo="Cambio de planes",
        ahora=reserva.inicio - timedelta(minutes=1),
    )
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.CANCELADA
    evento = EventoReserva.objects.get(reserva=reserva)
    assert evento.detalle == "Cambio de planes"


def test_usuario_no_puede_cancelar_reserva_ajena():
    _, reserva = escenario()
    intruso = usuario("intruso@example.edu")
    with pytest.raises(PermissionDenied):
        cancelar_reserva_propia(reserva_id=reserva.pk, actor=intruso)
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.PENDIENTE


def test_peticion_directa_para_cancelar_reserva_ajena_devuelve_403(client):
    _, reserva = escenario()
    intruso = usuario("intruso@example.edu")
    client.force_login(intruso)
    response = client.post(f"/reservas/{reserva.pk}/cancelar/", {"motivo": "Intento"})
    assert response.status_code == 403
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.PENDIENTE


def test_motivo_opcional_no_puede_superar_mil_caracteres():
    propietario, reserva = escenario()
    with pytest.raises(ValidationError):
        cancelar_reserva_propia(
            reserva_id=reserva.pk, actor=propietario, motivo="x" * 1001
        )
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.PENDIENTE


@pytest.mark.parametrize("desplazamiento", [timedelta(0), timedelta(seconds=1)])
def test_no_se_puede_cancelar_en_o_despues_del_inicio(desplazamiento):
    propietario, reserva = escenario()
    with pytest.raises(ValidationError, match="antes del inicio"):
        cancelar_reserva_propia(
            reserva_id=reserva.pk,
            actor=propietario,
            ahora=reserva.inicio + desplazamiento,
        )


@pytest.mark.parametrize("estado", [Reserva.Estado.RECHAZADA, Reserva.Estado.CANCELADA])
def test_estados_terminales_no_se_pueden_cancelar(estado):
    propietario, reserva = escenario(estado=estado)
    with pytest.raises(ValidationError, match="No se permite cambiar"):
        cancelar_reserva_propia(
            reserva_id=reserva.pk,
            actor=propietario,
            ahora=reserva.inicio - timedelta(minutes=1),
        )


def test_cancelar_aprobada_libera_intervalo_para_otra_aprobacion():
    propietario, reserva = escenario(estado=Reserva.Estado.APROBADA)
    cancelar_reserva_propia(
        reserva_id=reserva.pk,
        actor=propietario,
        ahora=reserva.inicio - timedelta(minutes=1),
    )
    otro = usuario("otro@example.edu")
    siguiente = Reserva.objects.create(
        solicitante=otro,
        espacio=reserva.espacio,
        inicio=reserva.inicio,
        fin=reserva.fin,
    )
    gestor = usuario("gestor@example.edu", gestor=True)
    aprobar_reserva(reserva_id=siguiente.pk, actor=gestor)
    siguiente.refresh_from_db()
    assert siguiente.estado == Reserva.Estado.APROBADA


def test_aprobada_legada_superior_a_cuatro_horas_conserva_historial_y_cancelacion():
    propietario, reserva = escenario(
        estado=Reserva.Estado.APROBADA,
        duracion=timedelta(hours=5),
    )
    EventoReserva.objects.create(
        reserva=reserva,
        responsable=propietario,
        accion=EventoReserva.Accion.APROBACION,
        detalle="Aprobación anterior a la política de duración máxima",
    )

    with pytest.raises(ValidationError, match="máxima es de cuatro horas"):
        validar_intervalo_temporal(
            reserva.inicio,
            reserva.fin,
            ahora=reserva.inicio - timedelta(days=1),
        )

    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.APROBADA
    assert EventoReserva.objects.filter(reserva=reserva).count() == 1

    cancelar_reserva_propia(
        reserva_id=reserva.pk,
        actor=propietario,
        motivo="Cancelación de reserva histórica",
        ahora=reserva.inicio - timedelta(minutes=1),
    )

    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.CANCELADA
    assert EventoReserva.objects.filter(reserva=reserva).count() == 2


def test_fallo_de_evento_revierte_cancelacion_propia(monkeypatch):
    propietario, reserva = escenario(estado=Reserva.Estado.APROBADA)

    def fallar(**kwargs):
        raise RuntimeError("fallo simulado")

    monkeypatch.setattr("apps.auditoria.services.registrar_evento", fallar)
    with pytest.raises(RuntimeError, match="fallo simulado"):
        cancelar_reserva_propia(
            reserva_id=reserva.pk,
            actor=propietario,
            motivo="Cambio de planes",
            ahora=reserva.inicio - timedelta(minutes=1),
        )

    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.APROBADA
    assert not EventoReserva.objects.filter(reserva=reserva).exists()
