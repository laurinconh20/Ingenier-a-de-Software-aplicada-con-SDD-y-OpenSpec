from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth.models import Group

from apps.auditoria.models import EventoReserva
from apps.espacios.models import Espacio
from apps.reservas.models import Reserva
from apps.usuarios.models import Usuario
from apps.usuarios.roles import GESTOR, SOLICITANTE

pytestmark = [pytest.mark.functional, pytest.mark.django_db]
BOGOTA = ZoneInfo("America/Bogota")


def usuario(email, rol=SOLICITANTE):
    item = Usuario.objects.create_user(
        email=email, nombre=email.split("@")[0], password="clave-segura-123"
    )
    item.groups.add(Group.objects.get(name=rol))
    return item


def espacio(nombre="Sala Historial"):
    return Espacio.objects.create(
        nombre=nombre,
        tipo=Espacio.Tipo.AUDITORIO,
        ubicacion=f"Bloque {nombre}",
        capacidad=40,
    )


def crear_reserva(solicitante, lugar, dia, estado=Reserva.Estado.PENDIENTE):
    inicio = datetime(2031, 4, dia, 10, 0, tzinfo=BOGOTA)
    return Reserva.objects.create(
        solicitante=solicitante,
        espacio=lugar,
        inicio=inicio,
        fin=inicio + timedelta(hours=1),
        estado=estado,
    )


def test_solicitante_solo_consulta_su_historial(client):
    propio = usuario("propio@example.edu")
    ajeno = usuario("ajeno@example.edu")
    lugar = espacio()
    propia = crear_reserva(propio, lugar, 1)
    crear_reserva(ajeno, lugar, 2)
    client.force_login(propio)
    response = client.get("/reservas/")
    assert [item.pk for item in response.context["reservas"]] == [propia.pk]
    assert ajeno.email not in response.content.decode()


def test_solicitante_no_autorizado_recibe_403_en_historial_global(client):
    client.force_login(usuario("propio@example.edu"))
    assert client.get("/reservas/historial/").status_code == 403


def test_historial_global_filtra_estado_espacio_solicitante_y_fechas(client):
    gestor = usuario("gestor@example.edu", GESTOR)
    primero = usuario("primero@example.edu")
    segundo = usuario("segundo@example.edu")
    sala_a, sala_b = espacio("A"), espacio("B")
    esperado = crear_reserva(primero, sala_a, 5, Reserva.Estado.RECHAZADA)
    crear_reserva(primero, sala_b, 5, Reserva.Estado.RECHAZADA)
    crear_reserva(segundo, sala_a, 5, Reserva.Estado.RECHAZADA)
    crear_reserva(primero, sala_a, 6, Reserva.Estado.PENDIENTE)
    client.force_login(gestor)
    response = client.get(
        "/reservas/historial/",
        {
            "estado": Reserva.Estado.RECHAZADA,
            "espacio": sala_a.pk,
            "solicitante": primero.pk,
            "desde": "2031-04-05",
            "hasta": "2031-04-05",
        },
    )
    assert [item.pk for item in response.context["reservas"]] == [esperado.pk]


def test_rango_inclusivo_usa_fechas_institucionales_de_bogota(client):
    gestor = usuario("gestor.fechas@example.edu", GESTOR)
    propietario = usuario("propietario.fechas@example.edu")
    lugar = espacio("Fechas")

    def reserva_en(instante):
        return Reserva.objects.create(
            solicitante=propietario,
            espacio=lugar,
            inicio=instante,
            fin=instante + timedelta(minutes=1),
        )

    fuera_antes = reserva_en(datetime(2031, 4, 4, 23, 59, tzinfo=BOGOTA))
    limite_inicial = reserva_en(datetime(2031, 4, 5, 0, 0, tzinfo=BOGOTA))
    limite_final = reserva_en(datetime(2031, 4, 7, 23, 59, tzinfo=BOGOTA))
    fuera_despues = reserva_en(datetime(2031, 4, 8, 0, 0, tzinfo=BOGOTA))
    client.force_login(gestor)

    response = client.get(
        "/reservas/historial/",
        {"desde": "2031-04-05", "hasta": "2031-04-07"},
    )

    ids = {item.pk for item in response.context["reservas"]}
    assert ids == {limite_inicial.pk, limite_final.pk}
    assert fuera_antes.pk not in ids
    assert fuera_despues.pk not in ids


def test_acceso_ajeno_por_identificador_o_filtro_no_expone_datos(client):
    propio = usuario("propio.privado@example.edu")
    ajeno = usuario("ajeno.privado@example.edu")
    lugar = espacio("Privacidad")
    crear_reserva(propio, lugar, 8)
    reserva_ajena = crear_reserva(ajeno, lugar, 9)
    client.force_login(propio)

    detalle = client.get(f"/reservas/{reserva_ajena.pk}/")
    filtrado = client.get("/reservas/", {"solicitante": ajeno.pk})

    assert detalle.status_code == 404
    assert ajeno.email not in filtrado.content.decode()
    assert all(item.solicitante_id == propio.pk for item in filtrado.context["reservas"])


def test_paginacion_predeterminada_es_25_y_el_maximo_es_100(client):
    gestor = usuario("gestor@example.edu", GESTOR)
    propietario = usuario("propietario@example.edu")
    lugar = espacio()
    for indice in range(105):
        inicio = datetime(2032, 1, 5, 8, 0, tzinfo=BOGOTA) + timedelta(minutes=indice)
        Reserva.objects.create(
            solicitante=propietario,
            espacio=lugar,
            inicio=inicio,
            fin=inicio + timedelta(minutes=1),
        )
    client.force_login(gestor)
    normal = client.get("/reservas/historial/")
    maximo = client.get("/reservas/historial/", {"tamano": 1000})
    assert len(normal.context["reservas"]) == 25
    assert normal.context["page_obj"].has_next()
    assert len(maximo.context["reservas"]) == 100


def test_entidades_desactivadas_y_eventos_siguen_trazables_sin_credenciales(client):
    gestor = usuario("gestor@example.edu", GESTOR)
    propietario = usuario("propietario@example.edu")
    lugar = espacio()
    reserva = crear_reserva(propietario, lugar, 7, Reserva.Estado.CANCELADA)
    EventoReserva.objects.create(
        reserva=reserva,
        responsable=gestor,
        accion=EventoReserva.Accion.CANCELACION,
        detalle="Cierre institucional",
    )
    propietario.is_active = False
    propietario.save(update_fields=["is_active"])
    lugar.activo = False
    lugar.save(update_fields=["activo"])
    client.force_login(gestor)
    response = client.get("/reservas/historial/")
    contenido = response.content.decode()
    assert propietario.email in contenido
    assert "Cierre institucional" in contenido
    assert propietario.password not in contenido
    assert "pbkdf2_" not in contenido
    assert "sessionid" not in contenido.lower()
    assert "Creaci" in contenido
    assert str(reserva.fecha_creacion.year) in contenido
    evento = EventoReserva.objects.get(reserva=reserva)
    assert str(evento.fecha.year) in contenido
