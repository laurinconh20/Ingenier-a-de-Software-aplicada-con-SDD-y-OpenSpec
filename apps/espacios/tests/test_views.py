import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse

from apps.espacios.models import Espacio
from apps.usuarios.models import Usuario
from apps.usuarios.roles import ADMINISTRADOR, GESTOR, SOLICITANTE

pytestmark = [pytest.mark.functional, pytest.mark.django_db]


def user_in_role(role, email):
    call_command("sync_roles", verbosity=0)
    user = Usuario.objects.create_user(
        email=email,
        nombre=role,
        password="Una-Clave-Segura-2026",
    )
    user.groups.add(Group.objects.get(name=role))
    return user


def valid_space_data(**overrides):
    data = {
        "nombre": "Auditorio Central",
        "tipo": Espacio.Tipo.AUDITORIO,
        "ubicacion": "Bloque B",
        "capacidad": 120,
        "caracteristicas": "Proyector",
        "activo": "on",
    }
    data.update(overrides)
    return data


def test_administrator_can_create_and_update_space(client):
    admin = user_in_role(ADMINISTRADOR, "admin@universidad.edu.co")
    client.force_login(admin)

    response = client.post(reverse("espacios:create"), valid_space_data())
    assert response.status_code == 302
    space = Espacio.objects.get(nombre="Auditorio Central")

    response = client.post(
        reverse("espacios:update", args=[space.pk]),
        valid_space_data(capacidad=150),
    )
    assert response.status_code == 302
    space.refresh_from_db()
    assert space.capacidad == 150


def test_invalid_space_is_not_created(client):
    admin = user_in_role(ADMINISTRADOR, "admin@universidad.edu.co")
    client.force_login(admin)

    response = client.post(reverse("espacios:create"), valid_space_data(capacidad=0))

    assert response.status_code == 200
    assert not Espacio.objects.exists()
    assert "capacidad" in response.context["form"].errors


def test_authenticated_user_can_view_catalog_and_detail(client):
    requester = user_in_role(SOLICITANTE, "persona@universidad.edu.co")
    space = Espacio.objects.create(**valid_space_data(activo=True))
    client.force_login(requester)

    assert client.get(reverse("espacios:list")).status_code == 200
    response = client.get(reverse("espacios:detail", args=[space.pk]))
    assert response.status_code == 200
    assert "Auditorio Central" in response.content.decode()


def test_missing_space_returns_404(client):
    requester = user_in_role(SOLICITANTE, "persona@universidad.edu.co")
    client.force_login(requester)

    assert client.get(reverse("espacios:detail", args=[99999])).status_code == 404


def test_anonymous_user_cannot_view_catalog_or_detail(client):
    space = Espacio.objects.create(**valid_space_data(activo=True))

    list_response = client.get(reverse("espacios:list"))
    detail_response = client.get(reverse("espacios:detail", args=[space.pk]))

    assert list_response.status_code == 302
    assert detail_response.status_code == 302
    assert reverse("usuarios:login") in list_response.url
    assert reverse("usuarios:login") in detail_response.url


@pytest.mark.parametrize(
    "changes",
    [
        {"capacidad": 0},
        {"tipo": "TIPO_INEXISTENTE"},
    ],
)
def test_invalid_update_preserves_existing_space(client, changes):
    admin = user_in_role(ADMINISTRADOR, "admin.invalido@universidad.edu.co")
    space = Espacio.objects.create(**valid_space_data(activo=True))
    original = (space.nombre, space.tipo, space.ubicacion, space.capacidad)
    client.force_login(admin)

    response = client.post(
        reverse("espacios:update", args=[space.pk]),
        valid_space_data(**changes),
    )

    assert response.status_code == 200
    space.refresh_from_db()
    assert (space.nombre, space.tipo, space.ubicacion, space.capacidad) == original


def test_duplicate_update_preserves_existing_spaces(client):
    admin = user_in_role(ADMINISTRADOR, "admin.duplicado@universidad.edu.co")
    existing = Espacio.objects.create(**valid_space_data(activo=True))
    edited = Espacio.objects.create(
        **valid_space_data(nombre="Auditorio Alterno", ubicacion="Bloque C", activo=True)
    )
    client.force_login(admin)

    response = client.post(
        reverse("espacios:update", args=[edited.pk]),
        valid_space_data(nombre=existing.nombre, ubicacion=existing.ubicacion),
    )

    assert response.status_code == 200
    assert Espacio.objects.count() == 2
    edited.refresh_from_db()
    assert (edited.nombre, edited.ubicacion) == ("Auditorio Alterno", "Bloque C")


@pytest.mark.parametrize("role", [SOLICITANTE, GESTOR])
def test_non_administrative_roles_cannot_modify_catalog_by_direct_request(client, role):
    user = user_in_role(role, f"{role.replace(' ', '.').lower()}@universidad.edu.co")
    space = Espacio.objects.create(**valid_space_data(activo=True))
    client.force_login(user)

    create_response = client.post(
        reverse("espacios:create"), valid_space_data(nombre="No autorizado")
    )
    update_response = client.post(
        reverse("espacios:update", args=[space.pk]), valid_space_data(capacidad=999)
    )

    assert create_response.status_code == 403
    assert update_response.status_code == 403
    assert not Espacio.objects.filter(nombre="No autorizado").exists()
    space.refresh_from_db()
    assert space.capacidad == 120


def test_administrator_has_positive_catalog_permission(client):
    admin = user_in_role(ADMINISTRADOR, "admin.permisos@universidad.edu.co")
    client.force_login(admin)

    response = client.post(
        reverse("espacios:create"), valid_space_data(nombre="Creación autorizada")
    )

    assert response.status_code == 302
    assert Espacio.objects.filter(nombre="Creación autorizada").exists()
