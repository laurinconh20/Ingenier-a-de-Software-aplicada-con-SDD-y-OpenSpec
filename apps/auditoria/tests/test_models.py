from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

from apps.auditoria.models import EventoReserva
from apps.espacios.models import Espacio
from apps.reservas.models import Reserva
from apps.usuarios.models import Usuario

pytestmark = [pytest.mark.integration, pytest.mark.django_db]
BOGOTA = ZoneInfo("America/Bogota")


def escenario():
    solicitante = Usuario.objects.create_user(
        email="solicitante@example.edu", nombre="Solicitante", password="clave-123"
    )
    responsable = Usuario.objects.create_user(
        email="responsable@example.edu", nombre="Responsable", password="clave-123"
    )
    espacio = Espacio.objects.create(
        nombre="Sala Auditada",
        tipo=Espacio.Tipo.AUDITORIO,
        ubicacion="Bloque I",
        capacidad=30,
    )
    inicio = datetime(2031, 3, 3, 10, 0, tzinfo=BOGOTA)
    reserva = Reserva.objects.create(
        solicitante=solicitante,
        espacio=espacio,
        inicio=inicio,
        fin=inicio + timedelta(hours=1),
    )
    return reserva, responsable


def test_evento_conserva_relaciones_accion_fecha_y_detalle():
    reserva, responsable = escenario()
    evento = EventoReserva.objects.create(
        reserva=reserva,
        responsable=responsable,
        accion=EventoReserva.Accion.APROBACION,
        detalle="Revisada",
    )
    assert evento.fecha is not None
    assert evento.reserva == reserva
    assert evento.responsable == responsable
    assert evento.detalle == "Revisada"


def test_evento_rechaza_detalle_superior_a_mil_caracteres():
    reserva, responsable = escenario()
    with pytest.raises(ValidationError):
        EventoReserva.objects.create(
            reserva=reserva,
            responsable=responsable,
            accion=EventoReserva.Accion.RECHAZO,
            detalle="x" * 1001,
        )


def test_evento_no_admite_edicion_ni_eliminacion_ordinaria():
    reserva, responsable = escenario()
    evento = EventoReserva.objects.create(
        reserva=reserva,
        responsable=responsable,
        accion=EventoReserva.Accion.APROBACION,
    )
    evento.detalle = "alterado"
    with pytest.raises(ValidationError, match="inmutables"):
        evento.save()
    with pytest.raises(ValidationError, match="no se pueden eliminar"):
        evento.delete()
    with pytest.raises(ValidationError, match="inmutables"):
        EventoReserva.objects.filter(pk=evento.pk).update(detalle="alterado")
    with pytest.raises(ValidationError, match="no se pueden eliminar"):
        EventoReserva.objects.filter(pk=evento.pk).delete()


def test_relaciones_protegidas_impiden_perder_trazabilidad():
    reserva, responsable = escenario()
    EventoReserva.objects.create(
        reserva=reserva,
        responsable=responsable,
        accion=EventoReserva.Accion.APROBACION,
    )
    with pytest.raises(ProtectedError):
        reserva.delete()
    with pytest.raises(ProtectedError):
        responsable.delete()
