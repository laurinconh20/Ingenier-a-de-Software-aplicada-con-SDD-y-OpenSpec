import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.db import connection  # noqa: E402

with connection.cursor() as cursor:
    cursor.execute(
        "SELECT current_database(), current_user, "
        "current_setting('server_version'), current_setting('TimeZone')"
    )
    database, user, version, timezone_name = cursor.fetchone()

print(f"database={database}")
print(f"user={user}")
print(f"server_version={version}")
print(f"database_session_timezone={timezone_name}")
print(f"institutional_timezone={settings.TIME_ZONE}")
