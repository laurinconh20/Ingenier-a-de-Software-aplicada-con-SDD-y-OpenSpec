from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UsuarioManager


class Usuario(AbstractUser):
    username = None
    nombre = models.CharField(max_length=150)
    email = models.EmailField("correo institucional", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre"]

    objects = UsuarioManager()

    class Meta:
        ordering = ["nombre", "email"]
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        permissions = [
            ("crear_solicitudes", "Puede crear solicitudes propias"),
            ("gestionar_usuarios", "Puede gestionar usuarios"),
            ("gestionar_espacios", "Puede gestionar espacios académicos"),
            ("decidir_reservas", "Puede aprobar y rechazar reservas"),
            ("cancelar_reservas", "Puede cancelar reservas de terceros"),
            ("consultar_historial_global", "Puede consultar el historial global"),
        ]

    def __str__(self) -> str:
        return f"{self.nombre} <{self.email}>"


