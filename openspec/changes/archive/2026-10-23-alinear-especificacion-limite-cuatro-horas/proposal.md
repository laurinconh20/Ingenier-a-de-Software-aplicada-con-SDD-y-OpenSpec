# Proposal

## Why

La especificación principal `reservation-requests` todavía declara que no existe una duración máxima y conserva un escenario que acepta seis horas, mientras `reservation-duration-policy` y la implementación vigente limitan cada solicitud a cuatro horas consecutivas. Esta contradicción debe eliminarse para que el contrato funcional sea coherente y trazable.

## What Changes

- Modificar RF-04.2 para reconocer el límite máximo de cuatro horas definido por RF-04.6.
- Sustituir el escenario que acepta una solicitud de seis horas por escenarios coherentes para cuatro horas exactas y una duración superior.
- Conservar sin cambios las reglas de inicio futuro, fin posterior, mismo día, precisión por minutos, ausencia de anticipación mínima adicional y ausencia de horizonte máximo.
- Verificar la coherencia entre `reservation-requests` y `reservation-duration-policy` mediante validación estricta de OpenSpec.
- No modificar código, esquema de base de datos, dependencias ni comportamiento en ejecución, porque la política ya está implementada y probada.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `reservation-requests`: Alinear RF-04.2 y sus escenarios con el límite vigente de cuatro horas consecutivas establecido por RF-04.6.

## Impact

El cambio afecta exclusivamente las especificaciones OpenSpec y su trazabilidad documental. No altera APIs, modelos, servicios, migraciones, dependencias ni pruebas de comportamiento existentes; estas últimas sirven como evidencia de que la documentación corregida describe la implementación actual.
