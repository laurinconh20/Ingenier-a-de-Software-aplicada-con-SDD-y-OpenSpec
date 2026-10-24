from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .roles import sync_role_groups


@receiver(post_migrate, dispatch_uid="usuarios.sync_role_groups")
def create_role_groups(**kwargs):
    sync_role_groups()

