# Tasks

## 1. Coherencia del contrato temporal

- [x] 1.1 Sincronizar el delta de RF-04.2 en la especificación principal `reservation-requests`, conservando todos los escenarios temporales no modificados; verificar que ya no aparezcan la ausencia de duración máxima ni el escenario que acepta seis horas.
- [x] 1.2 Comparar RF-04.2 con RF-04.6 y RF-04.7 de `reservation-duration-policy`; verificar que ambas capacidades permitan exactamente cuatro horas, rechacen duraciones superiores y mantengan sin contradicciones la ausencia de anticipación mínima y horizonte máximo.

## 2. Evidencia y validación

- [x] 2.1 Ejecutar las pruebas focalizadas de validación temporal, creación, disponibilidad y aprobación; verificar que la documentación corregida coincide con el comportamiento ya implementado sin modificar código fuente.
- [x] 2.2 Ejecutar `openspec validate alinear-especificacion-limite-cuatro-horas --strict` y `openspec validate --specs`; verificar que el cambio y todas las especificaciones principales sean válidos.
- [x] 2.3 Confirmar que no se generaron migraciones, dependencias ni cambios de aplicación; verificarlo con `python manage.py makemigrations --check --dry-run` y una revisión de los archivos modificados.
