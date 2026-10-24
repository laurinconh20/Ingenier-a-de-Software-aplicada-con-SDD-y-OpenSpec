# Spec Delta: Solicitudes de reserva

## Purpose

Define la creación y consulta de solicitudes para un espacio académico, con fechas, intervalos y estados válidos antes de cualquier decisión administrativa.

## ADDED Requirements

### Requirement: RF-04.1 Creación de una solicitud
El sistema SHALL permitir a una cuenta activa, autenticada y con capacidad `Solicitante` crear una solicitud para sí misma, un único espacio activo y un intervalo futuro. La solicitud válida SHALL iniciar en `PENDIENTE`; ningún dato enviado por el cliente SHALL sustituir al solicitante autenticado. Relación: Plan RF-04, 1.3, 1.6 y 2.4.

#### Scenario: Solicitud válida
- **GIVEN** un solicitante autenticado, un espacio activo y un intervalo futuro válido dentro del horario habilitado
- **WHEN** registra la solicitud
- **THEN** el sistema la conserva en estado `PENDIENTE`, asociada al solicitante y al espacio

#### Scenario: Espacio inactivo
- **GIVEN** un solicitante autenticado y un espacio inactivo
- **WHEN** intenta registrar una solicitud
- **THEN** el sistema la rechaza y no crea la solicitud

#### Scenario: Solicitud para más de un espacio
- **GIVEN** un solicitante autenticado
- **WHEN** intenta incluir más de un espacio en una solicitud
- **THEN** el sistema rechaza la operación e indica que cada solicitud corresponde a un único espacio

#### Scenario: Suplantación del solicitante
- **GIVEN** un solicitante autenticado
- **WHEN** manipula la petición para atribuir la solicitud a otra cuenta
- **THEN** el sistema ignora o rechaza el identificador ajeno y nunca crea una solicitud a nombre de otra persona

#### Scenario: Cuenta sin capacidad de solicitante
- **GIVEN** una cuenta autenticada que no tiene asignada la capacidad `Solicitante`
- **WHEN** intenta registrar una solicitud
- **THEN** el sistema deniega la operación y no crea la solicitud

### Requirement: RF-04.2 Validez temporal de la solicitud
El sistema SHALL aceptar únicamente intervalos con inicio estrictamente futuro, fin posterior, un solo día en `America/Bogota` y precisión de minutos con segundos en cero. No SHALL exigir anticipación mínima adicional, horizonte máximo ni duración máxima general en esta versión. Relación: Plan 1.6, 2.4, 6.7 y riesgo R-07.

#### Scenario: Intervalo futuro válido
- **GIVEN** un inicio futuro y un fin posterior en el mismo día institucional
- **WHEN** se valida la solicitud
- **THEN** el intervalo supera la validación temporal

#### Scenario: Inicio no futuro
- **GIVEN** un inicio igual o anterior al instante actual institucional
- **WHEN** se valida la solicitud
- **THEN** el sistema rechaza el intervalo sin crear la solicitud

#### Scenario: Inicio futuro sin anticipación adicional
- **GIVEN** un inicio posterior al instante actual que cumple las demás reglas
- **WHEN** se valida la solicitud
- **THEN** el sistema no la rechaza por carecer de un margen mínimo adicional

#### Scenario: Fin no posterior
- **GIVEN** un fin igual o anterior al inicio
- **WHEN** se valida la solicitud
- **THEN** el sistema rechaza el intervalo sin crear la solicitud

#### Scenario: Intervalo entre días distintos
- **GIVEN** un inicio y un fin que pertenecen a días calendario distintos en la zona institucional
- **WHEN** se valida la solicitud
- **THEN** el sistema la rechaza porque la primera versión admite reservas de un solo día

#### Scenario: Segundos distintos de cero
- **GIVEN** un inicio o fin con segundos distintos de cero
- **WHEN** se valida la solicitud
- **THEN** el sistema rechaza el intervalo e indica que la precisión permitida es de minutos

#### Scenario: Fecha futura sin horizonte máximo
- **GIVEN** un intervalo futuro que cumple las demás reglas
- **WHEN** se valida la solicitud
- **THEN** el sistema no lo rechaza únicamente por la distancia entre la fecha actual y la fecha solicitada

#### Scenario: Duración extensa dentro del mismo día
- **GIVEN** una solicitud de 09:00 a 15:00 contenida en el horario habilitado y sin conflictos aprobados
- **WHEN** se valida la duración
- **THEN** el sistema no la rechaza por un límite máximo general de duración

### Requirement: RF-04.3 Respeto del horario habilitado
El sistema SHALL aceptar una solicitud solamente si todo su intervalo está contenido en un horario de funcionamiento habilitado para el espacio y día correspondientes. Relación: Plan 1.6, 2.4 y RF-04.

#### Scenario: Intervalo contenido
- **GIVEN** un horario habilitado de 08:00 a 18:00 y una solicitud de 10:00 a 12:00 del día aplicable
- **WHEN** se valida la solicitud
- **THEN** el sistema permite continuar

#### Scenario: Intervalo parcialmente fuera del horario
- **GIVEN** un horario habilitado de 08:00 a 18:00 y una solicitud de 17:00 a 19:00
- **WHEN** se valida la solicitud
- **THEN** el sistema rechaza la solicitud e informa que excede el horario habilitado

#### Scenario: Día no habilitado
- **GIVEN** un espacio sin horario habilitado para el día solicitado
- **WHEN** se valida la solicitud
- **THEN** el sistema rechaza la solicitud

### Requirement: RF-04.4 Consulta del estado de solicitudes propias
El sistema SHALL permitir al solicitante consultar sus solicitudes y el estado actual `PENDIENTE`, `APROBADA`, `RECHAZADA` o `CANCELADA`, sin acceder por defecto a solicitudes ajenas. Relación: Plan RF-04 y estados de 2.4.

#### Scenario: Consulta propia
- **GIVEN** un solicitante autenticado con solicitudes registradas
- **WHEN** consulta sus solicitudes
- **THEN** el sistema muestra cada solicitud con espacio, intervalo y estado actual

#### Scenario: Consulta de solicitud ajena sin permiso
- **GIVEN** un solicitante sin permiso administrativo
- **WHEN** intenta consultar directamente una solicitud de otro usuario
- **THEN** el sistema deniega el acceso y no expone sus datos

### Requirement: RF-04.5 Coincidencia entre solicitudes pendientes
El sistema SHALL permitir que dos o más solicitudes `PENDIENTE` coincidan en el mismo espacio e intervalo; estar pendientes no SHALL constituir una reserva confirmada. Relación: Plan 1.6 y 2.4.

#### Scenario: Segunda solicitud pendiente coincidente
- **GIVEN** una solicitud pendiente para un espacio e intervalo
- **WHEN** otro solicitante registra una solicitud válida superpuesta
- **THEN** el sistema conserva ambas en estado `PENDIENTE`

