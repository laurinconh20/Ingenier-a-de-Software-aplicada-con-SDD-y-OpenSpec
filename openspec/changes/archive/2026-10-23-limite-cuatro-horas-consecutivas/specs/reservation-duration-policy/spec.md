# Spec Delta: Política de duración de reservas

## Purpose

Define la duración consecutiva máxima permitida para una solicitud individual y garantiza que la política institucional se aplique al solicitar, consultar disponibilidad y aprobar.

## ADDED Requirements

### Requirement: RF-04.6 Duración máxima consecutiva
El sistema SHALL aceptar una solicitud individual solamente cuando la diferencia entre fin e inicio sea menor o igual a cuatro horas. La duración se calculará sobre los instantes del intervalo `[inicio, fin)`; esta regla no acumula solicitudes adyacentes independientes. Relación: nueva regla institucional, Plan 2.4 y RF-04.

#### Scenario: Duración inferior a cuatro horas
- **GIVEN** un solicitante autorizado y un intervalo válido de menos de cuatro horas
- **WHEN** registra la solicitud
- **THEN** el sistema no la rechaza por su duración y continúa con las demás validaciones

#### Scenario: Duración exactamente de cuatro horas
- **GIVEN** un solicitante autorizado y un intervalo válido de exactamente cuatro horas
- **WHEN** registra la solicitud
- **THEN** el sistema no la rechaza por su duración y continúa con las demás validaciones

#### Scenario: Duración superior a cuatro horas
- **GIVEN** un solicitante autorizado y un intervalo cuyo fin está más de cuatro horas después del inicio
- **WHEN** intenta registrar la solicitud
- **THEN** el sistema rechaza la entrada, informa que la duración máxima es de cuatro horas y no crea la solicitud

#### Scenario: Solicitudes adyacentes independientes
- **GIVEN** dos solicitudes individuales de hasta cuatro horas cuyos intervalos son adyacentes
- **WHEN** se valida la duración de cada solicitud
- **THEN** el sistema evalúa cada intervalo por separado y no suma sus duraciones para esta regla

### Requirement: RF-04.7 Aplicación consistente durante el ciclo de decisión
El sistema MUST aplicar el mismo límite al validar disponibilidad y al aprobar una solicitud pendiente. Una solicitud anterior a la política que exceda cuatro horas MUST permanecer sin aprobar; las reservas ya aprobadas no SHALL cancelarse ni modificarse automáticamente. Relación: Plan RF-04, RF-05, RF-07 y validación al aprobar de 2.4.

#### Scenario: Consulta de disponibilidad con duración excesiva
- **GIVEN** un espacio activo y un intervalo de más de cuatro horas dentro de su horario habilitado
- **WHEN** un usuario consulta su disponibilidad
- **THEN** el sistema rechaza el intervalo por duración antes de informarlo como reservable

#### Scenario: Aprobación de solicitud pendiente anterior a la política
- **GIVEN** una solicitud pendiente de más de cuatro horas creada antes de activar la regla
- **WHEN** un actor autorizado intenta aprobarla
- **THEN** el sistema conserva la solicitud en `PENDIENTE`, no crea un evento de aprobación e informa el incumplimiento de duración

#### Scenario: Aprobación de solicitud de cuatro horas
- **GIVEN** una solicitud pendiente de exactamente cuatro horas que cumple las demás reglas
- **WHEN** un actor autorizado la aprueba
- **THEN** el sistema permite la transición a `APROBADA` y registra el evento correspondiente

#### Scenario: Reserva aprobada preexistente de duración mayor
- **GIVEN** una reserva aprobada antes de activar la regla cuya duración supera cuatro horas
- **WHEN** entra en vigor la política
- **THEN** el sistema conserva su estado, historial y transiciones permitidas sin modificarla automáticamente
