import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse

from apps.usuarios.models import Usuario
from apps.usuarios.roles import ADMINISTRADOR, GESTOR, SOLICITANTE

pytestmark = [pytest.mark.functional, pytest.mark.django_db]


def usuario_en_rol(rol, email):
    call_command("sync_roles", verbosity=0)
    usuario = Usuario.objects.create_user(
        email=email,
        nombre=rol,
        password="Una-Clave-Segura-2026",
    )
    usuario.groups.add(Group.objects.get(name=rol))
    return usuario


@pytest.mark.parametrize(
    ("rol", "esperados", "ausentes"),
    [
        (
            SOLICITANTE,
            ("Inicio", "Espacios", "Mis solicitudes", "Nueva solicitud", "Disponibilidad", "Perfil"),
            ("Gestionar usuarios", "Solicitudes por gestionar", "Historial global"),
        ),
        (
            GESTOR,
            ("Inicio", "Espacios", "Solicitudes por gestionar", "Historial global", "Perfil"),
            ("Gestionar usuarios", "Registrar espacio"),
        ),
        (
            ADMINISTRADOR,
            ("Inicio", "Espacios", "Reservas", "Historial global", "Gestionar usuarios", "Perfil"),
            (),
        ),
    ],
)
def test_navegacion_global_refleja_permisos(client, rol, esperados, ausentes):
    usuario = usuario_en_rol(rol, f"{rol.replace(' ', '.').lower()}@example.edu")
    client.force_login(usuario)

    contenido = client.get(reverse("home")).content.decode()

    for etiqueta in esperados:
        assert etiqueta in contenido
    for etiqueta in ausentes:
        assert etiqueta not in contenido


def test_navegacion_identifica_seccion_activa(client):
    client.force_login(usuario_en_rol(SOLICITANTE, "activo@example.edu"))

    contenido = client.get(reverse("espacios:list")).content.decode()

    assert 'href="/espacios/"' in contenido
    assert 'aria-current="page"' in contenido


def test_ocultar_opcion_no_reemplaza_autorizacion_del_servidor(client):
    client.force_login(usuario_en_rol(SOLICITANTE, "sin-permiso@example.edu"))

    pagina = client.get(reverse("home"))
    acceso_directo = client.get(reverse("usuarios:list"))

    assert "Gestionar usuarios" not in pagina.content.decode()
    assert acceso_directo.status_code == 403
