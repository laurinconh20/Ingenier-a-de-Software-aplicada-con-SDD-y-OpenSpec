from datetime import time, timedelta

import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.management import call_command

from apps.espacios.models import Espacio, HorarioEspacio
from apps.reservas.models import Reserva
from apps.reservas.services import crear_solicitud
from apps.usuarios.models import Usuario
from apps.usuarios.roles import ADMINISTRADOR, GESTOR, SOLICITANTE

pytestmark = [pytest.mark.functional, pytest.mark.django_db]


def crear_usuario(*, email="solicitante@example.edu", rol=SOLICITANTE):
    usuario = Usuario.objects.create_user(
        email=email,
        nombre=rol,
        password="clave-segura-123",
    )
    call_command("sync_roles", verbosity=0)
    usuario.groups.add(Group.objects.get(name=rol))
    return usuario


def crear_espacio(*, activo=True):
    espacio = Espacio.objects.create(
        nombre="Sala de Cómputo 1",
        tipo=Espacio.Tipo.SALA_COMPUTO,
        ubicacion="Bloque D",
        capacidad=20,
        activo=activo,
    )
    HorarioEspacio.objects.create(
        espacio=espacio,
        dia_semana=HorarioEspacio.DiaSemana.LUNES,
        hora_inicio=time(8),
        hora_fin=time(18),
    )
    return espacio


def datos(espacio, *, inicio="2030-11-04T10:00", fin="2030-11-04T12:00"):
    return {"espacio": espacio.pk, "inicio": inicio, "fin": fin}


def test_solicitante_autenticado_crea_solicitud_propia_pendiente(client):
    usuario = crear_usuario()
    otro = crear_usuario(email="otro@example.edu")
    espacio = crear_espacio()
    client.force_login(usuario)

    payload = {**datos(espacio), "solicitante": otro.pk}
    response = client.post("/reservas/nueva/", payload)

    assert response.status_code == 302
    reserva = Reserva.objects.get()
    assert reserva.solicitante == usuario
    assert reserva.espacio == espacio
    assert reserva.estado == Reserva.Estado.PENDIENTE


def test_solicitud_de_exactamente_cuatro_horas_es_creada(client):
    usuario = crear_usuario()
    espacio = crear_espacio()
    client.force_login(usuario)

    response = client.post(
        "/reservas/nueva/",
        datos(espacio, inicio="2030-11-04T10:00", fin="2030-11-04T14:00"),
    )

    assert response.status_code == 302
    reserva = Reserva.objects.get()
    assert reserva.fin - reserva.inicio == timedelta(hours=4)


def test_solicitud_superior_a_cuatro_horas_muestra_error_y_no_se_crea(client):
    usuario = crear_usuario()
    espacio = crear_espacio()
    client.force_login(usuario)

    response = client.post(
        "/reservas/nueva/",
        datos(espacio, inicio="2030-11-04T10:00", fin="2030-11-04T14:01"),
    )

    assert response.status_code == 200
    assert "duración máxima es de cuatro horas" in response.content.decode()
    assert not Reserva.objects.exists()


def test_se_permiten_multiples_solicitudes_pendientes_superpuestas(client):
    primero = crear_usuario()
    segundo = crear_usuario(email="otro@example.edu")
    espacio = crear_espacio()
    client.force_login(primero)
    client.post("/reservas/nueva/", datos(espacio))
    client.force_login(segundo)

    response = client.post("/reservas/nueva/", datos(espacio))

    assert response.status_code == 302
    assert Reserva.objects.filter(estado=Reserva.Estado.PENDIENTE).count() == 2


def test_rechaza_espacio_inactivo_aunque_se_manipule_la_peticion(client):
    usuario = crear_usuario()
    espacio = crear_espacio(activo=False)
    client.force_login(usuario)

    response = client.post("/reservas/nueva/", datos(espacio))

    assert response.status_code == 200
    assert response.context["form"].errors["espacio"]
    assert not Reserva.objects.exists()


def test_rechaza_intervalo_invalido_sin_crear_solicitud(client):
    usuario = crear_usuario()
    espacio = crear_espacio()
    client.force_login(usuario)

    response = client.post(
        "/reservas/nueva/",
        datos(espacio, inicio="2030-11-04T17:00", fin="2030-11-04T19:00"),
    )

    assert response.status_code == 200
    assert "excede el horario" in response.content.decode()
    assert not Reserva.objects.exists()


def test_usuario_anonimo_es_redirigido_al_login(client):
    espacio = crear_espacio()
    response = client.post("/reservas/nueva/", datos(espacio))
    assert response.status_code == 302
    assert "/usuarios/iniciar-sesion/" in response.url
    assert not Reserva.objects.exists()


def test_enlace_contextual_preselecciona_espacio_activo(client):
    usuario = crear_usuario()
    espacio = crear_espacio()
    client.force_login(usuario)

    response = client.get("/reservas/nueva/", {"espacio": espacio.pk})

    assert response.status_code == 200
    assert response.context["form"].initial["espacio"] == espacio


@pytest.mark.parametrize("rol", [GESTOR, ADMINISTRADOR])
def test_rol_administrativo_sin_capacidad_no_puede_crear_solicitud(client, rol):
    usuario = crear_usuario(email=f"{rol.replace(' ', '.')}@example.edu", rol=rol)
    espacio = crear_espacio()
    client.force_login(usuario)

    response = client.post(
        "/reservas/nueva/",
        {**datos(espacio), "solicitante": usuario.pk},
    )

    assert response.status_code == 403
    assert not Reserva.objects.exists()


def test_servicio_impide_omitir_el_control_de_capacidad_solicitante():
    gestor = crear_usuario(rol=GESTOR)
    espacio = crear_espacio()

    with pytest.raises(PermissionDenied, match="permiso para crear solicitudes"):
        crear_solicitud(
            solicitante=gestor,
            espacio=espacio,
            inicio=datos(espacio)["inicio"],
            fin=datos(espacio)["fin"],
        )

    assert not Reserva.objects.exists()
