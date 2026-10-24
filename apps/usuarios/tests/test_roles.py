import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command

from apps.usuarios.models import Usuario
from apps.usuarios.roles import ADMINISTRADOR, GESTOR, ROLE_PERMISSIONS, SOLICITANTE

pytestmark = [pytest.mark.security, pytest.mark.django_db]


def test_role_sync_is_idempotent_and_matches_matrix():
    call_command("sync_roles")
    call_command("sync_roles")

    assert set(Group.objects.values_list("name", flat=True)) == {
        SOLICITANTE,
        GESTOR,
        ADMINISTRADOR,
    }
    for role_name, expected in ROLE_PERMISSIONS.items():
        actual = set(
            Group.objects.get(name=role_name).permissions.values_list("codename", flat=True)
        )
        assert actual == expected


def test_users_receive_only_the_permissions_of_their_role():
    call_command("sync_roles")
    users = {}
    for role_name in ROLE_PERMISSIONS:
        user = Usuario.objects.create_user(
            email=f"{role_name.replace(' ', '.').lower()}@universidad.edu.co",
            nombre=role_name,
            password="Una-Clave-Segura-2026",
        )
        user.groups.add(Group.objects.get(name=role_name))
        users[role_name] = user

    assert not users[SOLICITANTE].has_perm("usuarios.decidir_reservas")
    assert users[GESTOR].has_perm("usuarios.decidir_reservas")
    assert not users[GESTOR].has_perm("usuarios.gestionar_usuarios")
    assert users[ADMINISTRADOR].has_perm("usuarios.gestionar_usuarios")
    assert users[ADMINISTRADOR].has_perm("usuarios.gestionar_espacios")


@pytest.mark.parametrize(
    ("role_name", "codename", "expected"),
    [
        (role_name, codename, codename in allowed)
        for role_name, allowed in ROLE_PERMISSIONS.items()
        for codename in sorted(set().union(*ROLE_PERMISSIONS.values()))
    ],
)
def test_complete_role_permission_matrix(role_name, codename, expected):
    call_command("sync_roles", verbosity=0)
    user = Usuario.objects.create_user(
        email=f"{role_name.replace(' ', '.').lower()}@universidad.edu.co",
        nombre=role_name,
        password="Una-Clave-Segura-2026",
    )
    user.groups.add(Group.objects.get(name=role_name))

    assert user.has_perm(f"usuarios.{codename}") is expected
