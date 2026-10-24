import pytest
from django.urls import reverse

from apps.usuarios.models import Usuario

pytestmark = [pytest.mark.functional, pytest.mark.django_db]


def create_user(*, active=True):
    return Usuario.objects.create_user(
        email="usuario@universidad.edu.co",
        nombre="Usuario",
        password="Una-Clave-Segura-2026",
        is_active=active,
    )


def test_active_user_can_log_in_and_log_out(client):
    create_user()

    response = client.post(
        reverse("usuarios:login"),
        {"username": "usuario@universidad.edu.co", "password": "Una-Clave-Segura-2026"},
    )
    assert response.status_code == 302
    assert "_auth_user_id" in client.session

    response = client.post(reverse("usuarios:logout"))
    assert response.status_code == 302
    assert "_auth_user_id" not in client.session

    response = client.get(reverse("usuarios:profile"))
    assert response.status_code == 302
    assert response.url.startswith(reverse("usuarios:login"))


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("desconocido@universidad.edu.co", "Una-Clave-Segura-2026"),
        ("usuario@universidad.edu.co", "incorrecta"),
    ],
)
def test_invalid_credentials_use_same_generic_error(client, email, password):
    create_user()

    response = client.post(
        reverse("usuarios:login"),
        {"username": email, "password": password},
    )

    assert response.status_code == 200
    assert "Las credenciales proporcionadas no son válidas." in response.content.decode()
    assert "_auth_user_id" not in client.session


def test_inactive_user_cannot_log_in(client):
    create_user(active=False)

    response = client.post(
        reverse("usuarios:login"),
        {"username": "usuario@universidad.edu.co", "password": "Una-Clave-Segura-2026"},
    )

    assert response.status_code == 200
    assert "Las credenciales proporcionadas no son válidas." in response.content.decode()
    assert "_auth_user_id" not in client.session


def test_anonymous_home_promotes_login_without_protected_metrics(client):
    response = client.get(reverse("home"))

    assert response.status_code == 200
    contenido = response.content.decode()
    assert "Iniciar sesión" in contenido
    assert "Gestiona tus reservas desde aquí" in contenido
    assert "Solicitudes pendientes" not in contenido
    assert "Gestionar usuarios" not in contenido
