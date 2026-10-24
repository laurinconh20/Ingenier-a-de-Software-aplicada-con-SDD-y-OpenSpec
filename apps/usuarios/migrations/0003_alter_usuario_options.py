from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0002_alter_usuario_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="usuario",
            options={
                "ordering": ["nombre", "email"],
                "permissions": [
                    ("crear_solicitudes", "Puede crear solicitudes propias"),
                    ("gestionar_usuarios", "Puede gestionar usuarios"),
                    ("gestionar_espacios", "Puede gestionar espacios académicos"),
                    ("decidir_reservas", "Puede aprobar y rechazar reservas"),
                    ("cancelar_reservas", "Puede cancelar reservas de terceros"),
                    ("consultar_historial_global", "Puede consultar el historial global"),
                ],
                "verbose_name": "usuario",
                "verbose_name_plural": "usuarios",
            },
        ),
    ]
