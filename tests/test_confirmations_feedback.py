from datetime import time, timedelta
from pathlib import Path

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from apps.espacios.models import Espacio, HorarioEspacio
from apps.reservas.models import Reserva
from apps.usuarios.models import Usuario
from apps.usuarios.roles import ADMINISTRADOR, SOLICITANTE

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
        nombre="Sala de confirmaciones",
        tipo=Espacio.Tipo.SALA_COMPUTO,
        ubicacion="Bloque C",
        capacidad=20,
    )


def test_volver_desde_confirmacion_no_elimina_y_post_si_elimina(client):
    administrador = usuario_en_rol(ADMINISTRADOR, "confirm-admin@example.edu")
    lugar = espacio()
    horario = HorarioEspacio.objects.create(
        espacio=lugar,
        dia_semana=HorarioEspacio.DiaSemana.LUNES,
        hora_inicio=time(8),
        hora_fin=time(18),
    )
    client.force_login(administrador)

    pagina = client.get(reverse("espacios:schedule-delete", args=[horario.pk]))

    assert pagina.status_code == 200
    assert "data-confirm=" in pagina.content.decode()
    assert "Volver sin cambios" in pagina.content.decode()
    assert HorarioEspacio.objects.filter(pk=horario.pk).exists()

    response = client.post(
        reverse("espacios:schedule-delete", args=[horario.pk]), follow=True
    )

    assert not HorarioEspacio.objects.filter(pk=horario.pk).exists()
    assert "El horario fue eliminado correctamente." in response.content.decode()


def test_cancelacion_funciona_con_post_normal_y_muestra_resultado(client):
    solicitante = usuario_en_rol(SOLICITANTE, "confirm-user@example.edu")
    lugar = espacio()
    inicio = timezone.now() + timedelta(days=2)
    reserva = Reserva.objects.create(
        solicitante=solicitante,
        espacio=lugar,
        inicio=inicio,
        fin=inicio + timedelta(hours=1),
    )
    client.force_login(solicitante)

    detalle = client.get(reverse("reservas:detail", args=[reserva.pk]))
    assert "data-confirm=" in detalle.content.decode()
    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.PENDIENTE

    response = client.post(
        reverse("reservas:cancel-own", args=[reserva.pk]),
        {"motivo": "Cambio de actividad"},
        follow=True,
    )

    reserva.refresh_from_db()
    assert reserva.estado == Reserva.Estado.CANCELADA
    assert "La reserva fue cancelada." in response.content.decode()


def test_cancelar_confirmacion_cliente_previene_el_envio():
    javascript = (
        Path(__file__).parents[1] / "static" / "js" / "app.js"
    ).read_text(encoding="utf-8")

    assert "!window.confirm(question)" in javascript
    assert "event.preventDefault()" in javascript
