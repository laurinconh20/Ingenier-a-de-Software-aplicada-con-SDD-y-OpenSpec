from datetime import timedelta

import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from apps.espacios.models import Espacio
from apps.reservas.models import Reserva
from apps.usuarios.models import Usuario
from apps.usuarios.roles import ADMINISTRADOR, SOLICITANTE

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


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
        nombre="Laboratorio 201",
        tipo=Espacio.Tipo.LABORATORIO,
        ubicacion="Bloque C",
        capacidad=25,
    )


def update_payload(active):
    return {
        "nombre": "Laboratorio 201",
        "tipo": Espacio.Tipo.LABORATORIO,
        "ubicacion": "Bloque C",
        "capacidad": 25,
        "caracteristicas": "",
        "activo": "on" if active else "",
    }


def test_future_approved_reservation_blocks_deactivation_until_cancelled(client):
    admin = user_in_role(ADMINISTRADOR, "admin@universidad.edu.co")
    requester = user_in_role(SOLICITANTE, "persona@universidad.edu.co")
    space = create_space()
    start = timezone.now() + timedelta(days=2)
    reservation = Reserva.objects.create(
        solicitante=requester,
        espacio=space,
        inicio=start,
        fin=start + timedelta(hours=2),
        estado=Reserva.Estado.APROBADA,
    )
    client.force_login(admin)

    response = client.post(reverse("espacios:update", args=[space.pk]), update_payload(False))
    assert response.status_code == 200
    space.refresh_from_db()
    assert space.activo is True

    reservation.estado = Reserva.Estado.CANCELADA
    reservation.save(update_fields=["estado"])
    response = client.post(reverse("espacios:update", args=[space.pk]), update_payload(False))
    assert response.status_code == 302
    space.refresh_from_db()
    assert space.activo is False
    assert Reserva.objects.filter(pk=reservation.pk).exists()


def test_inactive_space_rejects_new_reservation_validation():
    requester = user_in_role(SOLICITANTE, "persona@universidad.edu.co")
    space = create_space()
    space.activo = False
    space.save(update_fields=["activo"])
    start = timezone.now() + timedelta(days=2)
    reservation = Reserva(
        solicitante=requester,
        espacio=space,
        inicio=start,
        fin=start + timedelta(hours=1),
    )

    with pytest.raises(ValidationError):
        reservation.full_clean()
