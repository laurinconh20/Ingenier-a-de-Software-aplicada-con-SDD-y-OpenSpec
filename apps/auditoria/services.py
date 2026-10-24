"""Casos de uso y reglas del módulo de auditoría."""

from .models import EventoReserva


def registrar_evento(*, reserva, responsable, accion, detalle=""):
    return EventoReserva.objects.create(
        reserva=reserva,
        responsable=responsable,
        accion=accion,
        detalle=detalle,
    )

