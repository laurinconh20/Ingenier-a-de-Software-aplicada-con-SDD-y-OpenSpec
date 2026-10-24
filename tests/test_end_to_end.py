from datetime import datetime, time, timedelta
from html.parser import HTMLParser
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth.models import Group
from django.urls import reverse

from apps.auditoria.models import EventoReserva
from apps.espacios.models import Espacio
from apps.reservas.models import Reserva
from apps.usuarios.models import Usuario
from apps.usuarios.roles import ADMINISTRADOR, GESTOR, SOLICITANTE

pytestmark = [pytest.mark.functional, pytest.mark.django_db]
BOGOTA = ZoneInfo("America/Bogota")
CLAVE = "Una-Clave-Segura-2026"


class ExtractorEnlaces(HTMLParser):
    def __init__(self):
        super().__init__()
        self.enlaces = []
        self._href = None
        self._texto = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._texto = []

    def handle_data(self, data):
        if self._href is not None:
            self._texto.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.enlaces.append((" ".join("".join(self._texto).split()), self._href))
            self._href = None
            self._texto = []


def enlace_visible(response, etiqueta):
    parser = ExtractorEnlaces()
    parser.feed(response.content.decode())
    for texto, href in parser.enlaces:
        if etiqueta in texto:
            return href
    raise AssertionError(f"No se encontró un enlace visible con la etiqueta {etiqueta!r}")


def crear_usuario(email, rol):
    usuario = Usuario.objects.create_user(email=email, nombre=rol, password=CLAVE)
    usuario.groups.add(Group.objects.get(name=rol))
    return usuario


def iniciar(client, usuario):
    response = client.post(
        reverse("usuarios:login"),
        {"username": usuario.email, "password": CLAVE},
    )
    assert response.status_code == 302


def salir(client):
    assert client.post(reverse("usuarios:logout")).status_code == 302


def proximo_lunes():
    fecha = datetime.now(BOGOTA).date() + timedelta(days=1)
    while fecha.weekday() != 0:
        fecha += timedelta(days=1)
    return fecha


def test_flujo_integral_para_solicitante_gestor_y_administrador(client):
    administrador = crear_usuario("admin@universidad.edu.co", ADMINISTRADOR)
    gestor = crear_usuario("gestor@universidad.edu.co", GESTOR)
    solicitante = crear_usuario("estudiante@universidad.edu.co", SOLICITANTE)

    iniciar(client, administrador)
    inicio_admin = client.get(reverse("home"))
    assert client.get(enlace_visible(inicio_admin, "Registrar espacio")).status_code == 200
    assert client.get(enlace_visible(inicio_admin, "Gestionar usuarios")).status_code == 200
    respuesta = client.post(
        reverse("espacios:create"),
        {
            "nombre": "Laboratorio Integral",
            "tipo": Espacio.Tipo.LABORATORIO,
            "ubicacion": "Bloque Z",
            "capacidad": 24,
            "caracteristicas": "24 equipos",
            "activo": "on",
        },
    )
    assert respuesta.status_code == 302
    espacio = Espacio.objects.get(nombre="Laboratorio Integral")
    respuesta = client.post(
        reverse("espacios:schedule-create", args=[espacio.pk]),
        {"dia_semana": 0, "hora_inicio": "08:00", "hora_fin": "18:00"},
    )
    assert respuesta.status_code == 302
    salir(client)

    fecha = proximo_lunes()
    iniciar(client, solicitante)
    inicio_solicitante = client.get(reverse("home"))
    assert client.get(enlace_visible(inicio_solicitante, "Nueva solicitud")).status_code == 200
    assert client.get(enlace_visible(inicio_solicitante, "Disponibilidad")).status_code == 200
    assert "Laboratorio Integral" in client.get(reverse("espacios:list")).content.decode()
    respuesta = client.post(
        reverse("reservas:create"),
        {
            "espacio": espacio.pk,
            "inicio": f"{fecha:%Y-%m-%d}T10:00",
            "fin": f"{fecha:%Y-%m-%d}T12:00",
        },
    )
    assert respuesta.status_code == 302
    primera = Reserva.objects.get(solicitante=solicitante)
    assert primera.estado == Reserva.Estado.PENDIENTE
    salir(client)

    iniciar(client, gestor)
    inicio_gestor = client.get(reverse("home"))
    pendientes_url = enlace_visible(inicio_gestor, "Solicitudes por gestionar")
    assert client.get(pendientes_url).status_code == 200
    assert client.get(reverse("reservas:decision", args=[primera.pk])).status_code == 200
    client.post(
        reverse("reservas:approve", args=[primera.pk]),
        {"observacion": "Aprobada por gestor"},
    )
    primera.refresh_from_db()
    assert primera.estado == Reserva.Estado.APROBADA
    assert "Aprobada por gestor" in client.get(
        reverse("reservas:global-history")
    ).content.decode()
    salir(client)

    iniciar(client, solicitante)
    assert "Aprobada" in client.get(reverse("reservas:list")).content.decode()
    client.post(
        reverse("reservas:cancel-own", args=[primera.pk]),
        {"motivo": "Ya no la necesito"},
    )
    primera.refresh_from_db()
    assert primera.estado == Reserva.Estado.CANCELADA
    assert EventoReserva.objects.filter(reserva=primera).count() == 2
    respuesta = client.post(
        reverse("reservas:create"),
        {
            "espacio": espacio.pk,
            "inicio": f"{fecha:%Y-%m-%d}T13:00",
            "fin": f"{fecha:%Y-%m-%d}T14:00",
        },
    )
    assert respuesta.status_code == 302
    segunda = Reserva.objects.exclude(pk=primera.pk).get()
    salir(client)

    iniciar(client, administrador)
    client.post(
        reverse("reservas:reject", args=[segunda.pk]),
        {"motivo": "Prioridad institucional"},
    )
    segunda.refresh_from_db()
    assert segunda.estado == Reserva.Estado.RECHAZADA
    historial = client.get(reverse("reservas:global-history")).content.decode()
    assert "Ya no la necesito" in historial
    assert "Prioridad institucional" in historial
