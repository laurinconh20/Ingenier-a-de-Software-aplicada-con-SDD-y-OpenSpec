from datetime import time

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.espacios.models import Espacio, HorarioEspacio

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def create_space(**overrides):
    data = {
        "nombre": "Laboratorio 101",
        "tipo": Espacio.Tipo.LABORATORIO,
        "ubicacion": "Bloque A",
        "capacidad": 30,
    }
    data.update(overrides)
    return Espacio.objects.create(**data)


def test_space_constraints_reject_duplicate_and_non_positive_capacity():
    create_space()
    with pytest.raises(IntegrityError), transaction.atomic():
        create_space()
    with pytest.raises(IntegrityError), transaction.atomic():
        create_space(nombre="Laboratorio 102", capacidad=0)


def test_schedule_clean_rejects_invalid_or_overlapping_windows():
    space = create_space()
    HorarioEspacio.objects.create(
        espacio=space,
        dia_semana=HorarioEspacio.DiaSemana.LUNES,
        hora_inicio=time(8),
        hora_fin=time(12),
    )
    invalid = HorarioEspacio(
        espacio=space,
        dia_semana=HorarioEspacio.DiaSemana.LUNES,
        hora_inicio=time(12),
        hora_fin=time(12),
    )
    with pytest.raises(ValidationError):
        invalid.full_clean()

    overlap = HorarioEspacio(
        espacio=space,
        dia_semana=HorarioEspacio.DiaSemana.LUNES,
        hora_inicio=time(11),
        hora_fin=time(14),
    )
    with pytest.raises(ValidationError):
        overlap.full_clean()


def test_postgresql_rejects_overlapping_windows_but_allows_adjacent_ones():
    space = create_space()
    HorarioEspacio.objects.create(
        espacio=space,
        dia_semana=HorarioEspacio.DiaSemana.MARTES,
        hora_inicio=time(8),
        hora_fin=time(12),
    )
    HorarioEspacio.objects.create(
        espacio=space,
        dia_semana=HorarioEspacio.DiaSemana.MARTES,
        hora_inicio=time(12),
        hora_fin=time(14),
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        HorarioEspacio.objects.create(
            espacio=space,
            dia_semana=HorarioEspacio.DiaSemana.MARTES,
            hora_inicio=time(11, 59),
            hora_fin=time(13),
        )
