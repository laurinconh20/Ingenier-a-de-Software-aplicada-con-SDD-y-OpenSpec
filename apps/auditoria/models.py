"""Persistencia inmutable del módulo de auditoría."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class EventoReservaQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError("Los eventos de reserva son inmutables.")

    def delete(self):
        raise ValidationError("Los eventos de reserva no se pueden eliminar.")


class EventoReserva(models.Model):
    class Accion(models.TextChoices):
        APROBACION = "APROBACION", "Aprobación"
        RECHAZO = "RECHAZO", "Rechazo"
        CANCELACION = "CANCELACION", "Cancelación"

    reserva = models.ForeignKey(
        "reservas.Reserva",
        on_delete=models.PROTECT,
        related_name="eventos",
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="eventos_reserva",
    )
    accion = models.CharField(max_length=12, choices=Accion.choices)
    fecha = models.DateTimeField(auto_now_add=True)
    detalle = models.CharField(max_length=1000, blank=True)

    objects = EventoReservaQuerySet.as_manager()

    class Meta:
        ordering = ["-fecha", "-pk"]

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ValidationError("Los eventos de reserva son inmutables.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Los eventos de reserva no se pueden eliminar.")

    def __str__(self) -> str:
        return f"{self.get_accion_display()} de reserva {self.reserva_id}"

