# Matriz de roles y permisos

La autorización se valida siempre en el servidor. La pertenencia a un grupo no sustituye las reglas de propiedad: un Solicitante puede operar únicamente sobre sus propios registros.

| Permiso de dominio | Solicitante | Gestor de espacios | Administrador |
|---|---:|---:|---:|
| `usuarios.crear_solicitudes` | Sí | No | No |
| `usuarios.gestionar_usuarios` | No | No | Sí |
| `usuarios.gestionar_espacios` | No | No | Sí |
| `usuarios.decidir_reservas` | No | Sí | Sí |
| `usuarios.cancelar_reservas` | No | Sí | Sí |
| `usuarios.consultar_historial_global` | No | Sí | Sí |

La orden `python manage.py sync_roles` crea o reconcilia los grupos de forma idempotente. También se ejecuta después de las migraciones. Las vistas administrativas deben usar estos permisos y no depender únicamente de la visibilidad de enlaces o botones.

