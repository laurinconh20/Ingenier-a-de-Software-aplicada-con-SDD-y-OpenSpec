from django.conf import settings
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeBoundary, RangeOperators
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class Reserva(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADA = "APROBADA", "Aprobada"
        RECHAZADA = "RECHAZADA", "Rechazada"
        CANCELADA = "CANCELADA", "Cancelada"

    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reservas",
    )
    espacio = models.ForeignKey(
        "espacios.Espacio",
        on_delete=models.PROTECT,
        related_name="reservas",
    )
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-inicio", "-fecha_creacion"]
        constraints = [
            models.CheckConstraint(condition=Q(fin__gt=F("inicio")), name="reserva_fin_posterior_inicio"),
            ExclusionConstraint(
                name="reserva_aprobada_espacio_sin_solape",
                expressions=[
                    ("espacio", RangeOperators.EQUAL),
                    (
                        models.Func(
                            F("inicio"),
                            F("fin"),
                            RangeBoundary(),
                            function="TSTZRANGE",
                            output_field=DateTimeRangeField(),
                        ),
                        RangeOperators.OVERLAPS,
                    ),
                ],
                condition=Q(estado="APROBADA"),
            ),
            ExclusionConstraint(
                name="reserva_aprobada_solicitante_sin_solape",
                expressions=[
                    ("solicitante", RangeOperators.EQUAL),
                    (
                        models.Func(
                            F("inicio"),
                            F("fin"),
                            RangeBoundary(),
                            function="TSTZRANGE",
                            output_field=DateTimeRangeField(),
                        ),
                        RangeOperators.OVERLAPS,
                    ),
                ],
                condition=Q(estado="APROBADA"),
            ),
        ]

    def clean(self):
        super().clean()
        from apps.reservas.services import (
            validar_espacio_y_horario,
            validar_intervalo_temporal,
        )

        if self.inicio and self.fin:
            validar_intervalo_temporal(self.inicio, self.fin)
            if self.espacio_id:
                validar_espacio_y_horario(self.espacio, self.inicio, self.fin)

    def __str__(self) -> str:
        return f"{self.espacio} — {self.inicio:%Y-%m-%d %H:%M}"


