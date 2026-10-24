from django.contrib.auth.models import Group, Permission

SOLICITANTE = "Solicitante"
GESTOR = "Gestor de espacios"
ADMINISTRADOR = "Administrador"

ROLE_PERMISSIONS = {
    SOLICITANTE: {"crear_solicitudes"},
    GESTOR: {
        "decidir_reservas",
        "cancelar_reservas",
        "consultar_historial_global",
    },
    ADMINISTRADOR: {
        "gestionar_usuarios",
        "gestionar_espacios",
        "decidir_reservas",
        "cancelar_reservas",
        "consultar_historial_global",
    },
}


def sync_role_groups() -> None:
    available = {
        permission.codename: permission
        for permission in Permission.objects.filter(
            content_type__app_label="usuarios",
            codename__in=set().union(*ROLE_PERMISSIONS.values()),
        )
    }
    for role_name, codenames in ROLE_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=role_name)
        group.permissions.set(available[code] for code in codenames if code in available)

