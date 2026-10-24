from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Espacio, HorarioEspacio


@transaction.atomic
def desactivar_espacio(espacio: Espacio) -> Espacio:
    locked = Espacio.objects.select_for_update().get(pk=espacio.pk)
    if locked.reservas.filter(estado="APROBADA", inicio__gt=timezone.now()).exists():
        raise ValidationError(
            "El espacio tiene reservas futuras aprobadas; deben cancelarse antes de desactivarlo."
        )
    locked.activo = False
    locked.save(update_fields=["activo"])
    return locked


@transaction.atomic
def actualizar_espacio(*, espacio_id: int, datos: dict) -> Espacio:
    """Actualiza bajo el mismo bloqueo usado por la aprobación."""
    locked = Espacio.objects.select_for_update().get(pk=espacio_id)
    if locked.activo and datos.get("activo") is False:
        if locked.reservas.filter(
            estado="APROBADA", inicio__gt=timezone.now()
        ).exists():
            raise ValidationError(
                "El espacio tiene reservas futuras aprobadas; deben cancelarse antes de desactivarlo."
            )
    for campo, valor in datos.items():
        setattr(locked, campo, valor)
    locked.full_clean()
    locked.save()
    return locked


def validar_cambio_horario(
    espacio: Espacio,
    *,
    horario_propuesto: dict | None = None,
    horario_excluido_id: int | None = None,
) -> None:
    windows = list(
        HorarioEspacio.objects.filter(espacio=espacio)
        .exclude(pk=horario_excluido_id)
        .values("dia_semana", "hora_inicio", "hora_fin")
    )
    if horario_propuesto:
        windows.append(horario_propuesto)

    future_approved = espacio.reservas.filter(
        estado="APROBADA", inicio__gt=timezone.now()
    )
    for reservation in future_approved:
        local_start = timezone.localtime(reservation.inicio)
        local_end = timezone.localtime(reservation.fin)
        start_time = local_start.time().replace(tzinfo=None)
        end_time = local_end.time().replace(tzinfo=None)
        covered = any(
            window["dia_semana"] == local_start.weekday()
            and window["hora_inicio"] <= start_time
            and end_time <= window["hora_fin"]
            for window in windows
        )
        if not covered:
            raise ValidationError(
                "El cambio dejaría una reserva futura aprobada fuera del horario habilitado."
            )


@transaction.atomic
def guardar_horario(
    *, espacio_id: int, datos: dict, horario_id: int | None = None
) -> HorarioEspacio:
    """Crea o actualiza un horario serializado con decisiones del espacio."""
    espacio = Espacio.objects.select_for_update().get(pk=espacio_id)
    if horario_id is None:
        horario = HorarioEspacio(espacio=espacio)
    else:
        horario = HorarioEspacio.objects.select_for_update().get(
            pk=horario_id, espacio_id=espacio_id
        )
    for campo, valor in datos.items():
        setattr(horario, campo, valor)
    validar_cambio_horario(
        espacio,
        horario_propuesto={
            "dia_semana": horario.dia_semana,
            "hora_inicio": horario.hora_inicio,
            "hora_fin": horario.hora_fin,
        },
        horario_excluido_id=horario.pk,
    )
    horario.full_clean()
    horario.save()
    return horario


@transaction.atomic
def eliminar_horario(*, horario_id: int) -> int:
    """Elimina un horario después de serializar y revalidar el espacio."""
    referencia = HorarioEspacio.objects.only("espacio_id").get(pk=horario_id)
    espacio = Espacio.objects.select_for_update().get(pk=referencia.espacio_id)
    horario = HorarioEspacio.objects.select_for_update().get(pk=horario_id)
    validar_cambio_horario(espacio, horario_excluido_id=horario.pk)
    espacio_id = espacio.pk
    horario.delete()
    return espacio_id


