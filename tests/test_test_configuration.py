import pytest
from django.conf import settings
from django.db import connection


@pytest.mark.unit
def test_institutional_timezone_is_bogota():
    assert settings.TIME_ZONE == "America/Bogota"
    assert settings.USE_TZ is True


@pytest.mark.integration
@pytest.mark.django_db
def test_integration_database_is_postgresql_17():
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_setting('server_version_num')")
        version_number = int(cursor.fetchone()[0])

    assert connection.vendor == "postgresql"
    assert 170000 <= version_number < 180000


@pytest.mark.security
def test_test_settings_do_not_expose_provisional_secrets():
    assert settings.DEBUG is False
    assert settings.SECRET_KEY not in {
        "replace-with-a-local-secret",
        "unsafe-development-key-change-me",
    }


@pytest.mark.concurrency
@pytest.mark.django_db(transaction=True)
def test_database_supports_row_locks_for_concurrency_controls():
    assert connection.vendor == "postgresql"
    assert connection.features.has_select_for_update is True
