from datetime import timedelta
from pathlib import Path

import pytest
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone

from apps.espacios.models import Espacio
from apps.reservas.models import Reserva
from apps.usuarios.models import Usuario
from apps.usuarios.roles import ADMINISTRADOR, SOLICITANTE

pytestmark = [pytest.mark.functional, pytest.mark.django_db]


def usuario_en_rol(rol):
    usuario = Usuario.objects.create_user(
        email="responsive@example.edu",
        nombre="Responsivo",
        password="Una-Clave-Segura-2026",
    )
    usuario.groups.add(Group.objects.get(name=rol))
    return usuario


@pytest.mark.parametrize(
    ("url_name", "rol"),
    [
        ("home", SOLICITANTE),
        ("espacios:list", SOLICITANTE),
        ("reservas:list", SOLICITANTE),
        ("reservas:create", SOLICITANTE),
        ("reservas:global-history", ADMINISTRADOR),
        ("usuarios:list", ADMINISTRADOR),
    ],
)
def test_flujos_principales_cargan_con_contrato_responsive(client, url_name, rol):
    client.force_login(usuario_en_rol(rol))

    response = client.get(reverse(url_name))

    assert response.status_code == 200
    contenido = response.content.decode()
    assert 'name="viewport" content="width=device-width, initial-scale=1"' in contenido
    assert 'href="/static/css/app.css"' in contenido


def test_tablas_extensas_tienen_contenedor_desplazable_propio(client):
    administrador = usuario_en_rol(ADMINISTRADOR)
    espacio = Espacio.objects.create(
        nombre="Sala responsive",
        tipo=Espacio.Tipo.SALA_COMPUTO,
        ubicacion="Bloque R",
        capacidad=20,
    )
    inicio = timezone.now() + timedelta(days=2)
    Reserva.objects.create(
        solicitante=administrador,
        espacio=espacio,
        inicio=inicio,
        fin=inicio + timedelta(hours=1),
    )
    client.force_login(administrador)

    for url_name in ("reservas:list", "reservas:global-history", "usuarios:list"):
        contenido = client.get(reverse(url_name)).content.decode()
        assert 'class="table-responsive"' in contenido
        assert 'tabindex="0"' in contenido


def test_estilos_definen_comportamiento_para_320_y_1280_pixeles():
    css = (Path(__file__).parents[1] / "static" / "css" / "app.css").read_text(
        encoding="utf-8"
    )

    assert "overflow-x: hidden" in css
    assert "overflow-x: auto" in css
    assert "@media (max-width: 575.98px)" in css
    assert "@media (min-width: 1200px)" in css


def test_navegacion_movil_es_accesible_y_usa_javascript_local(client):
    client.force_login(usuario_en_rol(SOLICITANTE))

    contenido = client.get(reverse("home")).content.decode()

    assert 'aria-controls="app-navigation"' in contenido
    assert 'aria-expanded="false"' in contenido
    assert 'data-nav-close' in contenido
    assert 'src="/static/js/app.js"' in contenido


def test_mejoras_cliente_conservan_html_funcional():
    raiz = Path(__file__).parents[1]
    javascript = (raiz / "static" / "js" / "app.js").read_text(encoding="utf-8")
    base = (raiz / "templates" / "base.html").read_text(encoding="utf-8")

    assert 'event.key === "Escape"' in javascript
    assert "form[data-confirm]" in javascript
    assert "window.confirm" in javascript
    assert '<form method="post" action="{% url \'usuarios:logout\' %}">' in (
        raiz / "templates" / "components" / "navigation.html"
    ).read_text(encoding="utf-8")
    assert "{% static 'js/app.js' %}" in base


def test_plantillas_de_espacios_y_reservas_declaran_patrones_adaptables():
    templates = Path(__file__).parents[1] / "templates"
    catalogo = (templates / "espacios" / "list.html").read_text(encoding="utf-8")
    solicitud = (templates / "reservas" / "form.html").read_text(encoding="utf-8")
    historial = (templates / "reservas" / "historial_global.html").read_text(
        encoding="utf-8"
    )

    assert "space-grid" in catalogo
    assert "form-layout" in solicitud
    assert 'class="table-responsive"' in historial
    assert 'tabindex="0"' in historial
