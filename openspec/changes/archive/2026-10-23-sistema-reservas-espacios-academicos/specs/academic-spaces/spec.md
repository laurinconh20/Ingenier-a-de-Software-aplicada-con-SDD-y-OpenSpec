# Spec Delta: Gestión de espacios académicos

## Purpose

Define el catálogo institucional de laboratorios, auditorios y salas de cómputo, sus características, estado y ventanas configurables de funcionamiento.

## ADDED Requirements

### Requirement: RF-01.1 Registro de espacios académicos
El sistema SHALL permitir al Administrador registrar un espacio con nombre, tipo, ubicación, capacidad y estado obligatorios, y características opcionales. La capacidad MUST ser un entero positivo; nombre y ubicación MUST formar una combinación única; el tipo MUST ser `LABORATORIO`, `AUDITORIO` o `SALA_COMPUTO`. Relación: Plan RF-01 y 3.3.

#### Scenario: Registro válido
- **GIVEN** un administrador autorizado y datos válidos de un laboratorio, auditorio o sala de cómputo
- **WHEN** registra el espacio
- **THEN** el sistema crea el espacio con sus características y estado consultables

#### Scenario: Registro inválido
- **GIVEN** un administrador autorizado y datos obligatorios incompletos, capacidad no positiva o tipo fuera del catálogo
- **WHEN** intenta registrar el espacio
- **THEN** el sistema no crea el espacio e identifica los datos que requieren corrección

#### Scenario: Espacio duplicado en una ubicación
- **GIVEN** un espacio existente con una combinación de nombre y ubicación
- **WHEN** un administrador intenta registrar otro con la misma combinación
- **THEN** el sistema rechaza el duplicado y conserva un único espacio

#### Scenario: Registro no autorizado
- **GIVEN** un usuario sin permiso de gestión de espacios
- **WHEN** intenta registrar un espacio
- **THEN** el sistema deniega la operación y no crea registros

### Requirement: RF-01.2 Consulta de espacios y características
El sistema SHALL permitir a usuarios autenticados consultar espacios y sus características necesarias para decidir una solicitud, sin exponer datos administrativos restringidos. Actor: Solicitante, Gestor de espacios y Administrador. Relación: Plan RF-01 y 2.3.

#### Scenario: Consulta de catálogo
- **GIVEN** un usuario autenticado y espacios registrados
- **WHEN** consulta el catálogo
- **THEN** el sistema muestra por espacio su tipo, ubicación, capacidad, características, estado y horario aplicable

#### Scenario: Espacio inexistente
- **GIVEN** un identificador que no corresponde a un espacio registrado
- **WHEN** el usuario solicita su detalle
- **THEN** el sistema informa que el espacio no existe sin producir un error técnico interno

#### Scenario: Consulta sin autenticación
- **GIVEN** una persona sin sesión autenticada
- **WHEN** intenta consultar el catálogo o el detalle de un espacio
- **THEN** el sistema exige autenticación y no expone el catálogo

### Requirement: RF-01.3 Actualización y desactivación de espacios
El sistema SHALL permitir al Administrador actualizar o desactivar un espacio sin eliminar su historial. Un espacio inactivo MUST NOT aceptar solicitudes. La operación MUST rechazarse si desactivar o cambiar horarios invalidaría una reserva futura `APROBADA`; esas reservas deben cancelarse primero. Relación: Plan RF-01 y reglas de 2.4.

#### Scenario: Actualización autorizada
- **GIVEN** un administrador autorizado y un espacio existente
- **WHEN** actualiza datos válidos
- **THEN** el sistema persiste la nueva información para consultas posteriores

#### Scenario: Actualización inválida o duplicada
- **GIVEN** un administrador autorizado y un cambio con capacidad no positiva, tipo inválido o combinación nombre–ubicación ya existente
- **WHEN** intenta actualizar el espacio
- **THEN** el sistema rechaza el cambio, identifica los datos inválidos y conserva la información anterior

#### Scenario: Desactivación con reservas históricas
- **GIVEN** un espacio con reservas históricas
- **WHEN** un administrador autorizado lo desactiva
- **THEN** el sistema conserva reservas y eventos anteriores e impide nuevas solicitudes para ese espacio

#### Scenario: Desactivación con reserva futura aprobada
- **GIVEN** un espacio con una reserva aprobada cuyo inicio es futuro
- **WHEN** un administrador intenta desactivarlo
- **THEN** el sistema rechaza la desactivación e indica que la reserva debe cancelarse primero

#### Scenario: Modificación no autorizada
- **GIVEN** un actor sin permiso de gestión de espacios
- **WHEN** intenta actualizar o desactivar un espacio
- **THEN** el sistema deniega la operación y conserva la información existente

### Requirement: RF-01.4 Horarios configurables del espacio
El sistema SHALL permitir al Administrador configurar varias ventanas de funcionamiento por espacio y día de la semana. Cada ventana MUST tener fin posterior al inicio y MUST NOT superponerse con otra del mismo espacio y día. Las excepciones por fecha no forman parte de la primera versión. Relación: Plan 1.6, HorarioEspacio y RF-01.

#### Scenario: Configuración válida
- **GIVEN** un espacio existente y un intervalo de funcionamiento válido para un día
- **WHEN** el administrador guarda el horario
- **THEN** el sistema lo utiliza en consultas de disponibilidad y validación de solicitudes

#### Scenario: Intervalo de funcionamiento inválido
- **GIVEN** un intervalo cuyo fin no es posterior al inicio
- **WHEN** el administrador intenta guardarlo
- **THEN** el sistema rechaza la configuración y explica la validación incumplida

#### Scenario: Ventanas superpuestas
- **GIVEN** una ventana existente de 08:00 a 12:00 para un espacio y día
- **WHEN** el administrador intenta agregar otra de 11:00 a 14:00 para el mismo espacio y día
- **THEN** el sistema rechaza la nueva ventana por superposición

#### Scenario: Varias ventanas separadas
- **GIVEN** una ventana de 08:00 a 12:00 para un espacio y día
- **WHEN** el administrador agrega otra de 14:00 a 18:00 para el mismo espacio y día
- **THEN** el sistema conserva ambas ventanas habilitadas

#### Scenario: Ventanas adyacentes
- **GIVEN** una ventana de 08:00 a 12:00 para un espacio y día
- **WHEN** el administrador agrega otra que inicia exactamente a las 12:00
- **THEN** el sistema conserva ambas ventanas porque no se superponen

#### Scenario: Edición o eliminación no autorizada de horario
- **GIVEN** un actor sin permiso de gestión de espacios y un horario existente
- **WHEN** intenta editarlo o eliminarlo mediante una petición directa
- **THEN** el sistema deniega la operación y conserva el horario

#### Scenario: Cambio de horario invalida reserva futura
- **GIVEN** una reserva futura aprobada dentro del horario vigente
- **WHEN** el administrador intenta cambiar el horario de modo que la reserva quede fuera de toda ventana
- **THEN** el sistema rechaza el cambio e indica que la reserva debe cancelarse primero

