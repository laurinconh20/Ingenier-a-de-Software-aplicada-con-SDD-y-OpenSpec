import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("reservas", "0003_reserva_aprobada_solicitante_sin_solape"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="EventoReserva",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "accion",
                    models.CharField(
                        choices=[
                            ("APROBACION", "Aprobación"),
                            ("RECHAZO", "Rechazo"),
                            ("CANCELACION", "Cancelación"),
                        ],
                        max_length=12,
                    ),
                ),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                ("detalle", models.CharField(blank=True, max_length=1000)),
                (
                    "reserva",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="eventos",
                        to="reservas.reserva",
                    ),
                ),
                (
                    "responsable",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="eventos_reserva",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-fecha", "-pk"]},
        )
    ]
