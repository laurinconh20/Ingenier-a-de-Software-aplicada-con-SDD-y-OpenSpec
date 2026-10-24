from django.core.management.base import BaseCommand

from apps.usuarios.roles import sync_role_groups


class Command(BaseCommand):
    help = "Crea o actualiza de forma idempotente los roles y permisos institucionales."

    def handle(self, *args, **options):
        sync_role_groups()
        self.stdout.write(self.style.SUCCESS("Roles y permisos sincronizados."))

