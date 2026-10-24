from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse

from apps.espacios.models import Espacio, HorarioEspacio
from apps.reservas.models import Reserva
from apps.usuarios.models import Usuario
from apps.usuarios.roles import ADMINISTRADOR, GESTOR, SOLICITANTE

pytestmark = [pytest.mark.functional, pytest.mark.django_db]
BOGOTA = ZoneInfo("America/Bogota")


def user_in_role(role, email):
    call_command("sync_roles", verbosity=0)
    user = Usuario.objects.create_user(
        email=email,
        nombre=role,
        password="Una-Clave-Segura-2026",
    )
    user.groups.add(Group.objects.get(name=role))
    return user


def create_space():
    return Espacio.objects.create(
        nombre="Sala 301",
        tipo=Espacio.Tipo.SALA_COMPUTO,
        ubicacion="Bloque D",
        capacidad=20,
    )


def next_weekday(weekday):
    current = datetime.now(BOGOTA).date() + timedelta(days=1)
    while current.weekday() != weekday:
        current += timedelta(days=1)
    return current


def test_administrator_can_create_separate_weekly_windows(client):
    admin = user_in_role(ADMINISTRADOR, "admin@universidad.edu.co")
    space = create_space()
    client.force_login(admin)

    for start, end in (("08:00", "12:00"), ("14:00", "18:00")):
        response = client.post(
            reverse("espacios:schedule-create", args=[space.pk]),
            {"dia_semana": 0, "hora_inicio": start, "hora_fin": end},
        )
        assert response.status_code == 302

    assert space.horarios.count() == 2


def test_administrator_can_create_adjacent_weekly_windows(client):
    admin = user_in_role(ADMINISTRADOR, "admin.adyacente@universidad.edu.co")
    space = create_space()
    client.force_login(admin)

    for start, end in (("08:00", "12:00"), ("12:00", "14:00")):
        response = client.post(
            reverse("espacios:schedule-create", args=[space.pk]),
            {"dia_semana": 0, "hora_inicio": start, "hora_fin": end},
        )
        assert response.status_code == 302

    assert space.horarios.count() == 2


def test_overlapping_or_invalid_window_is_rejected(client):
    admin = user_in_role(ADMINISTRADOR, "admin@universidad.edu.co")
    space = create_space()
    HorarioEspacio.objects.create(
        espacio=space, dia_semana=1, hora_inicio=time(8), hora_fin=time(12)
    )
    client.force_login(admin)

    overlap = client.post(
        reverse("espacios:schedule-create", args=[space.pk]),
        {"dia_semana": 1, "hora_inicio": "11:00", "hora_fin": "14:00"},
    )
    invalid = client.post(
        reverse("espacios:schedule-create", args=[space.pk]),
        {"dia_semana": 2, "hora_inicio": "12:00", "hora_fin": "12:00"},
    )

    assert overlap.status_code == 200
    assert invalid.status_code == 200
    assert space.horarios.count() == 1


def test_schedule_cannot_be_deleted_until_future_approved_reservation_is_cancelled(client):
    admin = user_in_role(ADMINISTRADOR, "admin@universidad.edu.co")
    requester = user_in_role(SOLICITANTE, "persona@universidad.edu.co")
    space = create_space()
    schedule = HorarioEspacio.objects.create(
        espacio=space, dia_semana=0, hora_inicio=time(8), hora_fin=time(18)
    )
    day = next_weekday(0)
    reservation = Reserva.objects.create(
        solicitante=requester,
        espacio=space,
        inicio=datetime.combine(day, time(10), BOGOTA),
        fin=datetime.combine(day, time(12), BOGOTA),
        estado=Reserva.Estado.APROBADA,
    )
    client.force_login(admin)

    response = client.post(reverse("espacios:schedule-delete", args=[schedule.pk]))
    assert response.status_code == 302
    assert HorarioEspacio.objects.filter(pk=schedule.pk).exists()

    reservation.estado = Reserva.Estado.CANCELADA
    reservation.save(update_fields=["estado"])
    client.post(reverse("espacios:schedule-delete", args=[schedule.pk]))
    assert not HorarioEspacio.objects.filter(pk=schedule.pk).exists()


@pytest.mark.parametrize("role", [SOLICITANTE, GESTOR])
def test_unauthorized_direct_schedule_update_and_delete_preserve_data(client, role):
    user = user_in_role(role, f"horario.{role.replace(' ', '.')}@universidad.edu.co")
    space = create_space()
    schedule = HorarioEspacio.objects.create(
        espacio=space, dia_semana=0, hora_inicio=time(8), hora_fin=time(12)
    )
    client.force_login(user)

    update_response = client.post(
        reverse("espacios:schedule-update", args=[schedule.pk]),
        {"dia_semana": 0, "hora_inicio": "09:00", "hora_fin": "13:00"},
    )
    delete_response = client.post(
        reverse("espacios:schedule-delete", args=[schedule.pk])
    )

    assert update_response.status_code == 403
    assert delete_response.status_code == 403
    schedule.refresh_from_db()
    assert (schedule.hora_inicio, schedule.hora_fin) == (time(8), time(12))
