from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from apps.espacios.models import Espacio
from apps.reservas.models import Reserva
from apps.usuarios.models import Usuario

pytestmark = [pytest.mark.functional, pytest.mark.django_db]
BOGOTA = ZoneInfo("America/Bogota")


def usuario(email):
    return Usuario.objects.create_user(
        email=email, nombre=email.split("@")[0], password="clave-segura-123"
    )


def espacio():
    return Espacio.objects.create(
        nombre="Laboratorio Historial",
        tipo=Espacio.Tipo.LABORATORIO,
        ubicacion="Bloque E",
        capacidad=15,
    )


def reserva(solicitante, lugar, estado, desplazamiento=0):
    inicio = datetime(2031, 1, 6, 8 + desplazamiento, tzinfo=BOGOTA)
    return Reserva.objects.create(
        solicitante=solicitante,
        espacio=lugar,
        inicio=inicio,
        fin=inicio + timedelta(hours=1),
        estado=estado,
    )


def test_lista_muestra_espacio_intervalo_y_todos_los_estados_propios(client):
    propietario = usuario("propietario@example.edu")
    lugar = espacio()
    for indice, estado in enumerate(Reserva.Estado.values):
        reserva(propietario, lugar, estado, indice)
    client.force_login(propietario)

    response = client.get("/reservas/")

    contenido = response.content.decode()
    assert response.status_code == 200
    assert "Laboratorio Historial" in contenido
    for etiqueta in Reserva.Estado.labels:
        assert etiqueta in contenido


def test_lista_no_expone_solicitudes_ajenas(client):
    propietario = usuario("propietario@example.edu")
    ajeno = usuario("ajeno@example.edu")
    lugar = espacio()
    propia = reserva(propietario, lugar, Reserva.Estado.PENDIENTE)
    ajena = reserva(ajeno, lugar, Reserva.Estado.RECHAZADA, 2)
    client.force_login(propietario)

    response = client.get("/reservas/")

    ids = [item.pk for item in response.context["reservas"]]
    assert propia.pk in ids
    assert ajena.pk not in ids


def test_acceso_directo_a_solicitud_ajena_no_expone_datos(client):
    propietario = usuario("propietario@example.edu")
    ajeno = usuario("ajeno@example.edu")
    solicitud_ajena = reserva(ajeno, espacio(), Reserva.Estado.PENDIENTE)
    client.force_login(propietario)

    response = client.get(f"/reservas/{solicitud_ajena.pk}/")

    assert response.status_code == 404
    assert ajeno.email.encode() not in response.content


def test_lista_filtra_solicitudes_propias_por_estado(client):
    propietario = usuario("filtro@example.edu")
    lugar = espacio()
    pendiente = reserva(propietario, lugar, Reserva.Estado.PENDIENTE)
    aprobada = reserva(propietario, lugar, Reserva.Estado.APROBADA, 2)
    client.force_login(propietario)

    response = client.get("/reservas/", {"estado": Reserva.Estado.PENDIENTE})

    ids = [item.pk for item in response.context["reservas"]]
    assert pendiente.pk in ids
    assert aprobada.pk not in ids
    assert f'value="{Reserva.Estado.PENDIENTE}" selected' in response.content.decode()
