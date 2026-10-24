"""Casos de uso y reglas del módulo de reservas."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, PermissionDenied, ValidationError
from django.db import transaction
from django.db import IntegrityError
from django.utils import timezone

from apps.espacios.models import Espacio, HorarioEspacio


DURACION_MAXIMA_RESERVA = timedelta(hours=4)


TRANSICIONES_PERMITIDAS = {
    "PENDIENTE": frozenset({"APROBADA", "RECHAZADA", "CANCELADA"}),
    "APROBADA": frozenset({"CANCELADA"}),
    "RECHAZADA": frozenset(),
    "CANCELADA": frozenset(),
}


class ConflictoReserva(ValidationError):
    """Conflicto de dominio seguro para presentar al usuario."""


def _leer_referencia_reserva(reserva_id: int):
    """Toma el estado observado antes de adquirir los bloqueos de escritura."""
    from apps.reservas.models import Reserva

    return Reserva.objects.only("espacio_id", "estado").get(pk=reserva_id)


def validar_transicion_estado(estado_actual: str, estado_nuevo: str) -> None:
    """Impide reactivaciones, repeticiones y cualquier transición no declarada."""
    if estado_nuevo not in TRANSICIONES_PERMITIDAS.get(estado_actual, frozenset()):
        raise ValidationError(
            f"No se permite cambiar una reserva de {estado_actual} a {estado_nuevo}."
        )


def intervalos_se_superponen(
    inicio_a: datetime,
    fin_a: datetime,
    inicio_b: datetime,
    fin_b: datetime,
) -> bool:
    """Compara intervalos semiabiertos: [inicio, fin)."""
    return inicio_a < fin_b and inicio_b < fin_a


def validar_intervalo_temporal(
    inicio: datetime,
    fin: datetime,
    *,
    ahora: datetime | None = None,
) -> None:
    """Valida las reglas temporales institucionales de una solicitud."""
    errores: dict[str, list[str]] = {}
    if timezone.is_naive(inicio) or timezone.is_naive(fin):
        raise ValidationError(
            {NON_FIELD_ERRORS: ["El inicio y el fin deben incluir zona horaria."]}
        )

    zona_institucional = ZoneInfo(settings.TIME_ZONE)
    inicio_local = inicio.astimezone(zona_institucional)
    fin_local = fin.astimezone(zona_institucional)
    instante_actual = ahora or timezone.now()
    if timezone.is_naive(instante_actual):
        instante_actual = timezone.make_aware(instante_actual, zona_institucional)
    ahora_local = instante_actual.astimezone(zona_institucional)

    if inicio_local <= ahora_local:
        errores.setdefault("inicio", []).append(
            "El inicio debe ser estrictamente futuro."
        )
    if fin_local <= inicio_local:
        errores.setdefault("fin", []).append("El fin debe ser posterior al inicio.")
    if fin - inicio > DURACION_MAXIMA_RESERVA:
        errores.setdefault("fin", []).append(
            "La duración máxima es de cuatro horas consecutivas."
        )
    if inicio_local.date() != fin_local.date():
        errores.setdefault(NON_FIELD_ERRORS, []).append(
            "La reserva debe comenzar y terminar el mismo día institucional."
        )
    if inicio_local.second or inicio_local.microsecond:
        errores.setdefault("inicio", []).append(
            "La precisión permitida es de minutos; los segundos deben ser cero."
        )
    if fin_local.second or fin_local.microsecond:
        errores.setdefault("fin", []).append(
            "La precisión permitida es de minutos; los segundos deben ser cero."
        )
    if errores:
        raise ValidationError(errores)


def validar_espacio_y_horario(
    espacio: Espacio,
    inicio: datetime,
    fin: datetime,
) -> None:
    """Exige un espacio activo y cobertura completa por una ventana habilitada."""
    if not espacio.activo:
        raise ValidationError({"espacio": ["El espacio no está disponible."]})

    zona_institucional = ZoneInfo(settings.TIME_ZONE)
    inicio_local = inicio.astimezone(zona_institucional)
    fin_local = fin.astimezone(zona_institucional)
    hora_inicio = inicio_local.time().replace(tzinfo=None)
    hora_fin = fin_local.time().replace(tzinfo=None)
    esta_contenido = HorarioEspacio.objects.filter(
        espacio=espacio,
        dia_semana=inicio_local.weekday(),
        hora_inicio__lte=hora_inicio,
        hora_fin__gte=hora_fin,
    ).exists()
    if not esta_contenido:
        raise ValidationError(
            {NON_FIELD_ERRORS: ["El intervalo excede el horario habilitado del espacio."]}
        )


@transaction.atomic
def crear_solicitud(*, solicitante, espacio: Espacio, inicio: datetime, fin: datetime):
    """Crea una solicitud propia pendiente tras ejecutar todas las validaciones."""
    from apps.reservas.models import Reserva

    if not solicitante.is_active or not solicitante.has_perm(
        "usuarios.crear_solicitudes"
    ):
        raise PermissionDenied("No tiene permiso para crear solicitudes.")
    reserva = Reserva(
        solicitante=solicitante,
        espacio=espacio,
        inicio=inicio,
        fin=fin,
    )
    reserva.full_clean()
    reserva.save()
    return reserva


def esta_disponible(*, espacio: Espacio, inicio: datetime, fin: datetime) -> bool:
    """Consulta disponibilidad; solo una reserva aprobada constituye bloqueo."""
    from apps.reservas.models import Reserva

    validar_intervalo_temporal(inicio, fin)
    validar_espacio_y_horario(espacio, inicio, fin)
    return not Reserva.objects.filter(
        espacio=espacio,
        estado=Reserva.Estado.APROBADA,
        inicio__lt=fin,
        fin__gt=inicio,
    ).exists()


@transaction.atomic
def aprobar_reserva(*, reserva_id: int, actor, observacion: str = ""):
    """Aprueba con bloqueo, relectura y respaldo de restricciones PostgreSQL."""
    from apps.reservas.models import Reserva
    from apps.auditoria.models import EventoReserva
    from apps.auditoria.services import registrar_evento

    if not actor.is_active or not actor.has_perm("usuarios.decidir_reservas"):
        raise PermissionDenied("No tiene permiso para decidir solicitudes.")
    if len(observacion) > 1000:
        raise ValidationError({"observacion": ["La observación no puede superar 1.000 caracteres."]})

    referencia = _leer_referencia_reserva(reserva_id)
    espacio = Espacio.objects.select_for_update().get(pk=referencia.espacio_id)
    reserva = (
        Reserva.objects.select_for_update()
        .select_related("espacio", "solicitante")
        .get(pk=reserva_id)
    )
    validar_transicion_estado(reserva.estado, Reserva.Estado.APROBADA)
    validar_intervalo_temporal(reserva.inicio, reserva.fin)
    validar_espacio_y_horario(espacio, reserva.inicio, reserva.fin)

    solape = {"inicio__lt": reserva.fin, "fin__gt": reserva.inicio}
    if Reserva.objects.filter(
        espacio=espacio, estado=Reserva.Estado.APROBADA, **solape
    ).exclude(pk=reserva.pk).exists():
        raise ConflictoReserva("El espacio ya no está disponible para ese intervalo.")
    if Reserva.objects.filter(
        solicitante=reserva.solicitante,
        estado=Reserva.Estado.APROBADA,
        **solape,
    ).exclude(pk=reserva.pk).exists():
        raise ConflictoReserva("El solicitante ya tiene una reserva en ese intervalo.")

    try:
        with transaction.atomic():
            reserva.estado = Reserva.Estado.APROBADA
            reserva.save(update_fields=["estado"])
    except IntegrityError as error:
        raise ConflictoReserva(
            "La solicitud no pudo aprobarse porque el intervalo dejó de estar disponible."
        ) from error
    registrar_evento(
        reserva=reserva,
        responsable=actor,
        accion=EventoReserva.Accion.APROBACION,
        detalle=observacion,
    )
    return reserva


@transaction.atomic
def rechazar_reserva(*, reserva_id: int, actor, motivo: str):
    """Rechaza una solicitud pendiente con motivo obligatorio."""
    from apps.reservas.models import Reserva
    from apps.auditoria.models import EventoReserva
    from apps.auditoria.services import registrar_evento

    if not actor.is_active or not actor.has_perm("usuarios.decidir_reservas"):
        raise PermissionDenied("No tiene permiso para decidir solicitudes.")
    motivo = motivo.strip()
    if not 1 <= len(motivo) <= 1000:
        raise ValidationError(
            {"motivo": ["El motivo debe contener entre 1 y 1.000 caracteres."]}
        )
    reserva = Reserva.objects.select_for_update().get(pk=reserva_id)
    validar_transicion_estado(reserva.estado, Reserva.Estado.RECHAZADA)
    reserva.estado = Reserva.Estado.RECHAZADA
    reserva.save(update_fields=["estado"])
    registrar_evento(
        reserva=reserva,
        responsable=actor,
        accion=EventoReserva.Accion.RECHAZO,
        detalle=motivo,
    )
    return reserva


@transaction.atomic
def cancelar_reserva_propia(*, reserva_id: int, actor, motivo: str = "", ahora=None):
    """Cancela una solicitud propia cancelable antes de su instante de inicio."""
    from apps.auditoria.models import EventoReserva
    from apps.auditoria.services import registrar_evento
    from apps.reservas.models import Reserva

    if len(motivo) > 1000:
        raise ValidationError({"motivo": ["El motivo no puede superar 1.000 caracteres."]})
    referencia = _leer_referencia_reserva(reserva_id)
    Espacio.objects.select_for_update().get(pk=referencia.espacio_id)
    reserva = Reserva.objects.select_for_update().get(pk=reserva_id)
    if reserva.estado != referencia.estado:
        raise ConflictoReserva(
            "La reserva cambió mientras se procesaba la cancelación; inténtelo nuevamente."
        )
    if reserva.solicitante_id != actor.pk:
        raise PermissionDenied("No puede cancelar una reserva ajena.")
    instante_actual = ahora or timezone.now()
    if reserva.inicio <= instante_actual:
        raise ValidationError("Solo se puede cancelar antes del inicio de la reserva.")
    validar_transicion_estado(reserva.estado, Reserva.Estado.CANCELADA)
    reserva.estado = Reserva.Estado.CANCELADA
    reserva.save(update_fields=["estado"])
    registrar_evento(
        reserva=reserva,
        responsable=actor,
        accion=EventoReserva.Accion.CANCELACION,
        detalle=motivo,
    )
    return reserva


@transaction.atomic
def cancelar_reserva_administrativa(
    *, reserva_id: int, actor, motivo: str, ahora=None
):
    """Cancela cualquier reserva futura con permiso y motivo obligatorio."""
    from apps.auditoria.models import EventoReserva
    from apps.auditoria.services import registrar_evento
    from apps.reservas.models import Reserva

    if not actor.is_active or not actor.has_perm("usuarios.cancelar_reservas"):
        raise PermissionDenied("No tiene permiso para cancelar reservas ajenas.")
    motivo = motivo.strip()
    if not 1 <= len(motivo) <= 1000:
        raise ValidationError(
            {"motivo": ["El motivo debe contener entre 1 y 1.000 caracteres."]}
        )
    referencia = _leer_referencia_reserva(reserva_id)
    Espacio.objects.select_for_update().get(pk=referencia.espacio_id)
    reserva = Reserva.objects.select_for_update().get(pk=reserva_id)
    if reserva.estado != referencia.estado:
        raise ConflictoReserva(
            "La reserva cambió mientras se procesaba la cancelación; inténtelo nuevamente."
        )
    instante_actual = ahora or timezone.now()
    if reserva.inicio <= instante_actual:
        raise ValidationError("Solo se puede cancelar antes del inicio de la reserva.")
    validar_transicion_estado(reserva.estado, Reserva.Estado.CANCELADA)
    reserva.estado = Reserva.Estado.CANCELADA
    reserva.save(update_fields=["estado"])
    registrar_evento(
        reserva=reserva,
        responsable=actor,
        accion=EventoReserva.Accion.CANCELACION,
        detalle=motivo,
    )
    return reserva

