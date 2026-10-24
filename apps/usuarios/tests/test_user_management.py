import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse

from apps.usuarios.models import Usuario
from apps.usuarios.roles import ADMINISTRADOR, SOLICITANTE

pytestmark = [pytest.mark.security, pytest.mark.django_db]


def user_in_role(role, email):
    call_command("sync_roles", verbosity=0)
    user = Usuario.objects.create_user(
        email=email,
        nombre=role,
        password="Una-Clave-Segura-2026",
    )
    user.groups.add(Group.objects.get(name=role))
    return user


def test_administrator_can_register_user(client):
    admin = user_in_role(ADMINISTRADOR, "admin@universidad.edu.co")
    client.force_login(admin)

    response = client.post(
        reverse("usuarios:create"),
        {
            "email": "nuevo@universidad.edu.co",
            "nombre": "Nuevo usuario",
            "is_active": "on",
            "password1": "Clave-Segura-2026-A",
            "password2": "Clave-Segura-2026-A",
        },
    )

    assert response.status_code == 302
    created = Usuario.objects.get(email="nuevo@universidad.edu.co")
    assert created.nombre == "Nuevo usuario"
    assert created.check_password("Clave-Segura-2026-A")


def test_solicitante_cannot_register_user(client):
    requester = user_in_role(SOLICITANTE, "solicitante@universidad.edu.co")
    client.force_login(requester)

    response = client.post(
        reverse("usuarios:create"),
        {
            "email": "intruso@universidad.edu.co",
            "nombre": "Intruso",
            "password1": "Clave-Segura-2026-A",
            "password2": "Clave-Segura-2026-A",
        },
    )

    assert response.status_code == 403
    assert not Usuario.objects.filter(email="intruso@universidad.edu.co").exists()


def test_profile_request_cannot_change_protected_fields(client):
    requester = user_in_role(SOLICITANTE, "persona@universidad.edu.co")
    client.force_login(requester)

    response = client.post(
        reverse("usuarios:profile"),
        {
            "nombre": "Nombre actualizado",
            "email": "alterado@universidad.edu.co",
            "is_active": "",
            "groups": Group.objects.get(name=ADMINISTRADOR).pk,
        },
    )

    assert response.status_code == 302
    requester.refresh_from_db()
    assert requester.nombre == "Nombre actualizado"
    assert requester.email == "persona@universidad.edu.co"
    assert requester.is_active is True
    assert set(requester.groups.values_list("name", flat=True)) == {SOLICITANTE}


def test_administrator_can_change_email_role_and_state(client):
    admin = user_in_role(ADMINISTRADOR, "admin@universidad.edu.co")
    target = user_in_role(SOLICITANTE, "persona@universidad.edu.co")
    client.force_login(admin)

    response = client.post(
        reverse("usuarios:update", args=[target.pk]),
        {
            "nombre": "Persona",
            "email": "persona.actualizada@universidad.edu.co",
            "groups": Group.objects.get(name=ADMINISTRADOR).pk,
        },
    )

    assert response.status_code == 302
    target.refresh_from_db()
    assert target.email == "persona.actualizada@universidad.edu.co"
    assert target.is_active is False
    assert set(target.groups.values_list("name", flat=True)) == {ADMINISTRADOR}
