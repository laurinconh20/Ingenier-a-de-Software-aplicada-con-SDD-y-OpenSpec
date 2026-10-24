from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError

from apps.reservas.services import intervalos_se_superponen, validar_intervalo_temporal

pytestmark = pytest.mark.unit
BOGOTA = ZoneInfo("America/Bogota")
AHORA = datetime(2026, 10, 23, 10, 0, tzinfo=BOGOTA)


def dt(dia=23, hora=10, minuto=0, segundo=0, microsegundo=0):
    return datetime(
        2026, 10, dia, hora, minuto, segundo, microsegundo, tzinfo=BOGOTA
    )


def test_acepta_inicio_inmediatamente_futuro_sin_anticipacion_adicional():
    validar_intervalo_temporal(dt(minuto=1), dt(hora=11), ahora=AHORA)


def test_rechaza_inicio_igual_o_anterior_al_instante_actual():
    for inicio in (AHORA, AHORA - timedelta(minutes=1)):
        with pytest.raises(ValidationError, match="estrictamente futuro"):
            validar_intervalo_temporal(inicio, dt(hora=11), ahora=AHORA)


def test_rechaza_fin_igual_o_anterior_al_inicio():
    inicio = dt(hora=11)
    for fin in (inicio, inicio - timedelta(minutes=1)):
        with pytest.raises(ValidationError, match="posterior al inicio"):
            validar_intervalo_temporal(inicio, fin, ahora=AHORA)


def test_rechaza_intervalo_entre_dias_institucionales_distintos():
    with pytest.raises(ValidationError, match="mismo día institucional"):
        validar_intervalo_temporal(dt(hora=23), dt(dia=24, hora=1), ahora=AHORA)


@pytest.mark.parametrize(
    ("inicio", "fin"),
    [
        (dt(hora=11, segundo=1), dt(hora=12)),
        (dt(hora=11), dt(hora=12, segundo=1)),
        (dt(hora=11, microsegundo=1), dt(hora=12)),
    ],
)
def test_rechaza_precision_menor_que_un_minuto(inicio, fin):
    with pytest.raises(ValidationError, match="precisión permitida"):
        validar_intervalo_temporal(inicio, fin, ahora=AHORA)


def test_acepta_fecha_sin_horizonte_maximo():
    inicio = datetime(2035, 5, 8, 9, 0, tzinfo=BOGOTA)
    fin = datetime(2035, 5, 8, 10, 0, tzinfo=BOGOTA)
    validar_intervalo_temporal(inicio, fin, ahora=AHORA)


@pytest.mark.parametrize("duracion", [timedelta(hours=3, minutes=59), timedelta(hours=4)])
def test_acepta_duracion_inferior_o_igual_a_cuatro_horas(duracion):
    inicio = dt(hora=11)
    validar_intervalo_temporal(inicio, inicio + duracion, ahora=AHORA)


def test_rechaza_duracion_superior_a_cuatro_horas():
    inicio = dt(hora=11)
    with pytest.raises(ValidationError, match="máxima es de cuatro horas"):
        validar_intervalo_temporal(
            inicio,
            inicio + timedelta(hours=4, minutes=1),
            ahora=AHORA,
        )


def test_solicitudes_adyacentes_se_validan_independientemente():
    primer_inicio = dt(hora=11)
    primer_fin = dt(hora=15)
    segundo_fin = dt(hora=19)

    validar_intervalo_temporal(primer_inicio, primer_fin, ahora=AHORA)
    validar_intervalo_temporal(primer_fin, segundo_fin, ahora=AHORA)


def test_intervalos_semiabiertos_permiten_adyacencia_pero_detectan_solape():
    assert not intervalos_se_superponen(
        dt(hora=11), dt(hora=12), dt(hora=12), dt(hora=13)
    )
    assert intervalos_se_superponen(
        dt(hora=11), dt(hora=12), dt(hora=11, minuto=59), dt(hora=13)
    )


def test_rechaza_fechas_sin_zona_horaria():
    with pytest.raises(ValidationError, match="zona horaria"):
        validar_intervalo_temporal(
            datetime(2026, 10, 23, 11, 0),
            datetime(2026, 10, 23, 12, 0),
            ahora=AHORA,
        )
