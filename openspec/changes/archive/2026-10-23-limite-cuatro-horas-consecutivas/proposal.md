# Proposal

## Why

La institución estableció una nueva regla para limitar a cuatro horas consecutivas la duración de una reserva académica. El sistema actual permite duraciones mayores, por lo que debe incorporar la política mediante un cambio independiente y trazable sin alterar las decisiones arquitectónicas vigentes.

## What Changes

- **BREAKING**: rechazar nuevas solicitudes cuyo intervalo dure más de cuatro horas consecutivas.
- Permitir intervalos de exactamente cuatro horas cuando cumplan las demás reglas temporales, de horario y disponibilidad.
- Revalidar el límite al aprobar una solicitud pendiente para impedir que una solicitud anterior a la política se convierta en una reserva aprobada incompatible.
- Mantener sin modificación automática las reservas ya aprobadas antes de desplegar la regla; permanecen en el historial y conservan sus transiciones permitidas.
- Presentar un error de validación comprensible y asociado al intervalo, sin exponer detalles internos.
- Sustituir la prueba que actualmente acepta seis horas por pruebas de los límites inferior, exacto y superior a cuatro horas, tanto en creación como en aprobación.

## Capabilities

### New Capabilities

- `reservation-duration-policy`: Define y verifica la duración máxima consecutiva de las solicitudes y reservas académicas.

### Modified Capabilities

Ninguna en `openspec/specs`: la especificación inicial permanece en un cambio completado pero aún no archivado. Esta capacidad nueva documenta formalmente la política institucional posterior y su relación con RF-04.

## Impact

- Lógica temporal central de `apps/reservas/services.py`, reutilizada por creación, consulta de disponibilidad y aprobación.
- Formularios y vistas que presentan errores de validación de solicitudes y decisiones.
- Pruebas unitarias de intervalos, pruebas funcionales de creación y pruebas de integración de aprobación/revalidación.
- Documentación y matriz de trazabilidad RF-04 → especificación → tarea → prueba.
- Sin cambios de arquitectura, stack tecnológico, modelo de datos, estados, permisos, reglas de concurrencia ni dependencias externas.
