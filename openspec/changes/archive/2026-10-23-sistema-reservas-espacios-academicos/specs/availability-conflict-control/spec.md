# Spec Delta: Disponibilidad y control de conflictos

## Purpose

Define cómo se calcula la disponibilidad y cómo se impiden reservas aprobadas incompatibles, incluidas condiciones de carrera entre operaciones simultáneas.

## ADDED Requirements

### Requirement: RF-05.1 Consulta de disponibilidad
El sistema SHALL permitir a usuarios autenticados consultar disponibilidad para un espacio, fecha e intervalo considerando estado del espacio, horario habilitado y reservas `APROBADA`. Solicitudes `PENDIENTE` y registros `RECHAZADA` o `CANCELADA` MUST NOT bloquear el intervalo. Relación: Plan RF-05 y 2.4.

#### Scenario: Intervalo disponible
- **GIVEN** un espacio activo, un intervalo dentro de su horario y ninguna reserva aprobada superpuesta
- **WHEN** un usuario consulta disponibilidad
- **THEN** el sistema informa que el intervalo está disponible

#### Scenario: Intervalo ocupado
- **GIVEN** una reserva aprobada superpuesta para el mismo espacio
- **WHEN** un usuario consulta disponibilidad
- **THEN** el sistema informa que el intervalo no está disponible

#### Scenario: Coincidencia solamente con una solicitud pendiente
- **GIVEN** una solicitud pendiente superpuesta y ninguna reserva aprobada superpuesta
- **WHEN** un usuario consulta disponibilidad
- **THEN** el sistema no considera la solicitud pendiente como bloqueo definitivo

#### Scenario: Espacio inactivo o intervalo fuera del horario
- **GIVEN** un espacio inactivo, un día cerrado o un intervalo no contenido por completo en una ventana habilitada
- **WHEN** un usuario autenticado consulta disponibilidad
- **THEN** el sistema informa que el intervalo no puede reservarse e identifica la regla incumplida

#### Scenario: Consulta sin autenticación
- **GIVEN** una persona sin sesión autenticada
- **WHEN** intenta consultar disponibilidad
- **THEN** el sistema exige autenticación y no ejecuta la consulta

### Requirement: RF-05.2 Semántica de intervalos
El sistema SHALL interpretar todo intervalo de reserva como `[inicio, fin)`. Existe superposición cuando `inicioA < finB` y `inicioB < finA`; la igualdad entre el fin de uno y el inicio de otro SHALL permitirse. Relación: Plan 2.4.

#### Scenario: Intervalos superpuestos
- **GIVEN** una reserva aprobada de 10:00 a 12:00
- **WHEN** se evalúa un intervalo de 11:59 a 13:00 para el mismo espacio
- **THEN** el sistema detecta superposición

#### Scenario: Intervalos adyacentes
- **GIVEN** una reserva aprobada de 10:00 a 12:00
- **WHEN** se evalúa un intervalo que inicia exactamente a las 12:00
- **THEN** el sistema no detecta superposición con esa reserva

### Requirement: RF-06.1 Exclusión de reservas aprobadas por espacio
El sistema MUST garantizar en la lógica de negocio y en PostgreSQL que no existan dos reservas `APROBADA` con intervalos superpuestos para el mismo espacio. Relación: Plan RF-06, 3.4 y riesgo R-01.

#### Scenario: Aprobación conflictiva secuencial
- **GIVEN** una reserva aprobada para un espacio y una solicitud pendiente superpuesta
- **WHEN** se intenta aprobar la solicitud pendiente
- **THEN** el sistema rechaza la aprobación de forma controlada y conserva una sola reserva aprobada

#### Scenario: Aprobaciones concurrentes para el mismo espacio
- **GIVEN** dos solicitudes pendientes superpuestas para el mismo espacio
- **WHEN** dos actores intentan aprobarlas simultáneamente
- **THEN** como máximo una operación termina aprobada y la otra recibe un resultado de conflicto comprensible

### Requirement: RF-06.2 Exclusión de reservas aprobadas por solicitante
El sistema MUST impedir que un usuario mantenga dos reservas `APROBADA` con intervalos superpuestos, aunque correspondan a espacios diferentes. Relación: supuesto del Plan 1.6 y controles de integridad de 3.3.

#### Scenario: Conflicto del solicitante entre espacios
- **GIVEN** un usuario con una reserva aprobada y una solicitud pendiente superpuesta para otro espacio
- **WHEN** se intenta aprobar la segunda
- **THEN** el sistema rechaza la aprobación y conserva el estado consistente

#### Scenario: Reservas adyacentes del solicitante
- **GIVEN** un usuario con una reserva aprobada que termina a las 12:00
- **WHEN** se aprueba otra que inicia a las 12:00
- **THEN** el sistema permite la aprobación si no existe otro conflicto

#### Scenario: Aprobaciones concurrentes del mismo solicitante en espacios distintos
- **GIVEN** dos solicitudes pendientes superpuestas del mismo solicitante para espacios diferentes
- **WHEN** actores autorizados intentan aprobarlas simultáneamente mediante transacciones independientes
- **THEN** como máximo una queda `APROBADA`, la otra permanece en un estado válido y recibe un conflicto comprensible

### Requirement: RF-06.3 Consistencia ante fallos concurrentes
La aprobación SHALL ejecutarse atómicamente, volver a comprobar disponibilidad y transformar violaciones de integridad o conflictos de concurrencia en un resultado controlado, sin mostrar detalles internos ni dejar cambios parciales. Relación: Plan 3.4 y 5.1.

#### Scenario: Restricción de base de datos detecta carrera
- **GIVEN** una condición de carrera que supera una comprobación previa
- **WHEN** PostgreSQL rechaza la escritura incompatible
- **THEN** el sistema revierte la transacción, conserva la solicitud sin aprobar y muestra un conflicto comprensible

#### Scenario: Fallo durante la transacción
- **GIVEN** una aprobación en curso
- **WHEN** ocurre un error antes de confirmar la transacción
- **THEN** el sistema no persiste un cambio parcial de estado ni un evento de aprobación huérfano

#### Scenario: Aprobación concurrente con cambio del espacio
- **GIVEN** una solicitud pendiente y una desactivación o cambio de horario concurrente del mismo espacio
- **WHEN** ambas operaciones se procesan simultáneamente
- **THEN** el sistema serializa las decisiones y confirma solo una combinación que mantenga espacio, horario y reserva consistentes

#### Scenario: Aprobación concurrente con cancelación
- **GIVEN** una solicitud pendiente cuyo propietario o un administrador intenta cancelar mientras otro actor intenta aprobar
- **WHEN** ambas operaciones se procesan simultáneamente
- **THEN** una sola transición se confirma, el estado final es válido y existe exactamente el evento correspondiente

