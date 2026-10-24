import pytest
from django.core.exceptions import ValidationError

from apps.reservas.models import Reserva
from apps.reservas.services import validar_transicion_estado

pytestmark = pytest.mark.unit

PERMITIDAS = {
    (Reserva.Estado.PENDIENTE, Reserva.Estado.APROBADA),
    (Reserva.Estado.PENDIENTE, Reserva.Estado.RECHAZADA),
    (Reserva.Estado.PENDIENTE, Reserva.Estado.CANCELADA),
    (Reserva.Estado.APROBADA, Reserva.Estado.CANCELADA),
}


@pytest.mark.parametrize(("actual", "nuevo"), sorted(PERMITIDAS))
def test_transiciones_permitidas(actual, nuevo):
    validar_transicion_estado(actual, nuevo)


@pytest.mark.parametrize(
    ("actual", "nuevo"),
    [
        (actual, nuevo)
        for actual in Reserva.Estado.values
        for nuevo in Reserva.Estado.values
        if (actual, nuevo) not in PERMITIDAS
    ],
)
def test_todas_las_demas_transiciones_estan_prohibidas(actual, nuevo):
    with pytest.raises(ValidationError, match="No se permite cambiar"):
        validar_transicion_estado(actual, nuevo)


def test_estado_desconocido_no_admite_transiciones():
    with pytest.raises(ValidationError):
        validar_transicion_estado("DESCONOCIDO", Reserva.Estado.PENDIENTE)
