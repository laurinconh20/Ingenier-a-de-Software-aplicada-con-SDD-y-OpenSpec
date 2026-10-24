import django.contrib.postgres.constraints
import django.contrib.postgres.fields.ranges
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("reservas", "0001_initial")]

    operations = [
        migrations.AddConstraint(
            model_name="reserva",
            constraint=django.contrib.postgres.constraints.ExclusionConstraint(
                condition=models.Q(("estado", "APROBADA")),
                expressions=[
                    ("espacio", "="),
                    (
                        models.Func(
                            models.F("inicio"),
                            models.F("fin"),
                            django.contrib.postgres.fields.ranges.RangeBoundary(),
                            function="TSTZRANGE",
                            output_field=django.contrib.postgres.fields.ranges.DateTimeRangeField(),
                        ),
                        "&&",
                    ),
                ],
                name="reserva_aprobada_espacio_sin_solape",
            ),
        )
    ]
