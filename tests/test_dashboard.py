from datetime import timedelta

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from apps.espacios.models import Espacio
from apps.reservas.models import Reserva
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


def espacio():
    return Espacio.objects.create(
        nombre="Laboratorio de redes",
        tipo=Espacio.Tipo.LABORATORIO,
        ubicacion="Bloque A",
        capacidad=24,
        activo=True,
    )


def reserva_de(usuario, lugar, estado=Reserva.Estado.PENDIENTE, horas=0):
    inicio = timezone.now() + timedelta(days=5, hours=horas)
    return Reserva.objects.create(
        solicitante=usuario,
        espacio=lugar,
        inicio=inicio,
        fin=inicio + timedelta(hours=1),
        estado=estado,
    )


def test_dashboard_solicitante_limita_metricas_y_actividad_a_datos_propios(client):
    solicitante = usuario_en_rol(SOLICITANTE, "propio@example.edu")
    tercero = usuario_en_rol(SOLICITANTE, "tercero@example.edu")
    lugar = espacio()
    propia = reserva_de(solicitante, lugar)
    reserva_de(tercero, lugar, estado=Reserva.Estado.RECHAZADA, horas=2)
    client.force_login(solicitante)

    response = client.get(reverse("home"))

    assert response.context["dashboard_mode"] == "solicitante"
    assert response.context["metricas"][Reserva.Estado.PENDIENTE] == 1
    assert response.context["metricas"][Reserva.Estado.RECHAZADA] == 0
    assert list(response.context["reservas_recientes"]) == [propia]
    assert tercero.email not in response.content.decode()


def test_dashboard_gestor_muestra_pendientes_y_actividad_gestionable(client):
    gestor = usuario_en_rol(GESTOR, "gestor@example.edu")
    solicitante = usuario_en_rol(SOLICITANTE, "persona@example.edu")
    lugar = espacio()
    reserva_de(solicitante, lugar)
    reserva_de(solicitante, lugar, estado=Reserva.Estado.CANCELADA, horas=2)
    client.force_login(gestor)

    response = client.get(reverse("home"))

    assert response.context["dashboard_mode"] == "gestor"
    assert response.context["pendientes_total"] == 1
    assert len(response.context["reservas_recientes"]) == 2


def test_dashboard_administrador_muestra_totales_operativos(client):
    administrador = usuario_en_rol(ADMINISTRADOR, "admin@example.edu")
    solicitante = usuario_en_rol(SOLICITANTE, "persona@example.edu")
    lugar = espacio()
    reserva_de(solicitante, lugar)
    client.force_login(administrador)

    response = client.get(reverse("home"))

    assert response.context["dashboard_mode"] == "administrador"
    assert response.context["usuarios_total"] == 2
    assert response.context["espacios_total"] == 1
    assert response.context["reservas_total"] == 1
    assert response.context["pendientes_total"] == 1


def test_dashboard_sin_datos_expone_estado_vacio(client):
    client.force_login(usuario_en_rol(SOLICITANTE, "sin-datos@example.edu"))

    response = client.get(reverse("home"))

    assert response.context["dashboard_vacio"] is True
    assert "Aún no tienes solicitudes" in response.content.decode()


def test_inicio_anonimo_no_expone_contexto_operativo(client):
    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert "dashboard_mode" not in response.context
    assert "pendientes_total" not in response.context
    assert "Iniciar sesión" in response.content.decode()


def test_consultas_del_dashboard_no_crecen_con_la_actividad_mostrada(client):
    administrador = usuario_en_rol(ADMINISTRADOR, "queries-admin@example.edu")
    solicitante = usuario_en_rol(SOLICITANTE, "queries-user@example.edu")
    lugar = espacio()
    reserva_de(solicitante, lugar)
    client.force_login(administrador)

    with CaptureQueriesContext(connection) as consultas_iniciales:
        assert client.get(reverse("home")).status_code == 200

    for indice in range(12):
        reserva_de(solicitante, lugar, horas=indice + 2)

    with CaptureQueriesContext(connection) as consultas_con_actividad:
        response = client.get(reverse("home"))

    assert response.status_code == 200
    assert len(response.context["reservas_recientes"]) == 6
    assert len(consultas_con_actividad) <= len(consultas_iniciales) + 1
