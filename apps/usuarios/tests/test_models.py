import pytest
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.usuarios.models import Usuario

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_user_email_is_normalized_and_password_is_hashed():
    user = Usuario.objects.create_user(
        email="DOCENTE@UNIVERSIDAD.EDU.CO",
        nombre="Docente",
        password="Una-Clave-Segura-2026",
    )

    assert user.email == "docente@universidad.edu.co"
    assert user.check_password("Una-Clave-Segura-2026")
    assert user.password != "Una-Clave-Segura-2026"


def test_duplicate_email_is_rejected():
    Usuario.objects.create_user(
        email="persona@universidad.edu.co",
        nombre="Primera",
        password="Una-Clave-Segura-2026",
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        Usuario.objects.create_user(
            email="persona@universidad.edu.co",
            nombre="Segunda",
            password="Otra-Clave-Segura-2026",
        )


def test_django_password_validators_reject_weak_password():
    user = Usuario(email="persona@universidad.edu.co", nombre="Persona")

    with pytest.raises(ValidationError):
        validate_password("123", user=user)


def test_deactivation_preserves_user_record():
    user = Usuario.objects.create_user(
        email="inactivo@universidad.edu.co",
        nombre="Usuario",
        password="Una-Clave-Segura-2026",
    )

    user.is_active = False
    user.save(update_fields=["is_active"])

    persisted = Usuario.objects.get(pk=user.pk)
    assert persisted.is_active is False
    assert Usuario.objects.count() == 1
