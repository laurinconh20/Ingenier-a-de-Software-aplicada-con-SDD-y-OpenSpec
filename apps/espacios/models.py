from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class Espacio(models.Model):
    class Tipo(models.TextChoices):
        LABORATORIO = "LABORATORIO", "Laboratorio"
        AUDITORIO = "AUDITORIO", "Auditorio"
        SALA_COMPUTO = "SALA_COMPUTO", "Sala de cómputo"

    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    ubicacion = models.CharField(max_length=200)
    capacidad = models.PositiveIntegerField()
    caracteristicas = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre", "ubicacion"]
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "ubicacion"], name="espacio_nombre_ubicacion_unicos"
            ),
            models.CheckConstraint(
                condition=Q(capacidad__gt=0), name="espacio_capacidad_positiva"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nombre} — {self.ubicacion}"


class HorarioEspacio(models.Model):
    class DiaSemana(models.IntegerChoices):
        LUNES = 0, "Lunes"
        MARTES = 1, "Martes"
        MIERCOLES = 2, "Miércoles"
        JUEVES = 3, "Jueves"
        VIERNES = 4, "Viernes"
        SABADO = 5, "Sábado"
        DOMINGO = 6, "Domingo"

    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE, related_name="horarios")
    dia_semana = models.PositiveSmallIntegerField(choices=DiaSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        ordering = ["espacio", "dia_semana", "hora_inicio"]
        constraints = [
            models.CheckConstraint(
                condition=Q(hora_fin__gt=F("hora_inicio")),
                name="horario_fin_posterior_inicio",
            )
        ]

    def clean(self):
        super().clean()
        if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
            raise ValidationError({"hora_fin": "La hora final debe ser posterior al inicio."})
        if not all((self.espacio_id, self.hora_inicio, self.hora_fin)):
            return
        overlapping = type(self).objects.filter(
            espacio_id=self.espacio_id,
            dia_semana=self.dia_semana,
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio,
        ).exclude(pk=self.pk)
        if overlapping.exists():
            raise ValidationError("El horario se superpone con otra ventana del mismo día.")

    def __str__(self) -> str:
        return (
            f"{self.espacio} — {self.get_dia_semana_display()} "
            f"{self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M}"
        )


