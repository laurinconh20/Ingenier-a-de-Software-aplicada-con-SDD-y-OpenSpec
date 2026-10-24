# Spec Delta: Decisiones sobre solicitudes

## Purpose

Define quién puede aprobar o rechazar solicitudes, las transiciones de estado válidas y las comprobaciones obligatorias al decidir.

## ADDED Requirements

### Requirement: RF-07.1 Autorización para decidir solicitudes
El sistema SHALL permitir aprobar o rechazar solicitudes únicamente a Gestores de espacios y Administradores autenticados. En la primera versión, cada Gestor autorizado SHALL decidir solicitudes de todos los espacios; no existe asignación por espacio. Los Solicitantes MUST NOT decidir solicitudes. Relación: Plan 1.3, RF-03 y RF-07.

#### Scenario: Gestor autorizado
- **GIVEN** un gestor autenticado con permiso de decidir solicitudes
- **WHEN** intenta aprobar o rechazar una solicitud pendiente de cualquier espacio
- **THEN** el sistema permite evaluar la decisión

#### Scenario: Solicitante sin permiso
- **GIVEN** un solicitante sin permiso de decisión
- **WHEN** intenta aprobar o rechazar una solicitud
- **THEN** el sistema deniega la operación y conserva el estado

### Requirement: RF-07.2 Aprobación de una solicitud pendiente
El sistema SHALL permitir la transición `PENDIENTE` a `APROBADA` solamente después de revalidar espacio, horario, intervalo y conflictos en una operación atómica. El sistema SHALL aceptar una observación opcional de hasta 1.000 caracteres y conservarla en auditoría. Relación: Plan RF-07, 2.4 y 3.4.

#### Scenario: Aprobación válida
- **GIVEN** una solicitud pendiente que todavía cumple todas las reglas y un actor autorizado
- **WHEN** el actor la aprueba
- **THEN** el sistema cambia su estado a `APROBADA` y registra la decisión y el responsable

#### Scenario: Disponibilidad cambió antes de aprobar
- **GIVEN** una solicitud pendiente cuyo intervalo dejó de estar disponible
- **WHEN** un actor autorizado intenta aprobarla
- **THEN** el sistema no la aprueba, conserva un estado válido e informa el conflicto

#### Scenario: Solicitud no pendiente
- **GIVEN** una solicitud aprobada, rechazada o cancelada
- **WHEN** un actor intenta aprobarla
- **THEN** el sistema rechaza la transición y conserva el estado existente

#### Scenario: Observación de aprobación demasiado extensa
- **GIVEN** una solicitud pendiente y una observación superior a 1.000 caracteres
- **WHEN** un actor autorizado intenta aprobarla
- **THEN** el sistema rechaza la entrada y conserva la solicitud pendiente

#### Scenario: Fallo al registrar el evento de aprobación
- **GIVEN** una solicitud pendiente que supera las validaciones
- **WHEN** falla el registro del evento antes de confirmar la transacción
- **THEN** el sistema revierte la aprobación y conserva la solicitud `PENDIENTE` sin evento huérfano

### Requirement: RF-07.3 Rechazo de una solicitud pendiente
El sistema SHALL permitir la transición `PENDIENTE` a `RECHAZADA` únicamente a un actor autorizado que aporte un motivo de 1 a 1.000 caracteres. La decisión, el motivo y el responsable SHALL conservarse en el historial. Relación: Plan RF-07, RF-10 y 2.4.

#### Scenario: Rechazo válido
- **GIVEN** una solicitud pendiente, un actor autorizado y un motivo válido
- **WHEN** el actor la rechaza
- **THEN** el sistema cambia el estado a `RECHAZADA` y registra responsable, fecha y motivo

#### Scenario: Rechazo sin motivo válido
- **GIVEN** una solicitud pendiente y un motivo vacío o superior a 1.000 caracteres
- **WHEN** un actor autorizado intenta rechazarla
- **THEN** el sistema rechaza la entrada y conserva la solicitud pendiente

#### Scenario: Rechazo de solicitud no pendiente
- **GIVEN** una solicitud aprobada, rechazada o cancelada
- **WHEN** un actor intenta rechazarla
- **THEN** el sistema rechaza la transición y no agrega una decisión falsa al historial

#### Scenario: Fallo al registrar el evento de rechazo
- **GIVEN** una solicitud pendiente, un motivo válido y un actor autorizado
- **WHEN** falla el registro del evento antes de confirmar la transacción
- **THEN** el sistema revierte el rechazo y conserva la solicitud `PENDIENTE` sin evento huérfano

### Requirement: RF-07.4 Máquina de estados válida
El sistema MUST admitir solamente estas transiciones iniciales: `PENDIENTE` a `APROBADA`, `RECHAZADA` o `CANCELADA`, y `APROBADA` a `CANCELADA`. `RECHAZADA` y `CANCELADA` SHALL ser terminales. Relación: Plan 2.4.

#### Scenario: Transición válida a cancelada
- **GIVEN** una solicitud pendiente o aprobada que cumple la política de cancelación
- **WHEN** un actor autorizado la cancela
- **THEN** el sistema cambia el estado a `CANCELADA`

#### Scenario: Reactivación inválida
- **GIVEN** una reserva rechazada o cancelada
- **WHEN** se intenta cambiarla a pendiente o aprobada
- **THEN** el sistema rechaza la transición y conserva el estado terminal

