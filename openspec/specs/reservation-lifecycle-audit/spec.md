# reservation-lifecycle-audit Specification

## Purpose

Define la cancelación autorizada y la conservación de un historial trazable de estados, decisiones y responsables durante todo el ciclo de la reserva.

## Requirements

### Requirement: RF-08.1 Cancelación por el solicitante
El sistema SHALL permitir al solicitante cancelar su propia solicitud `PENDIENTE` o reserva `APROBADA` únicamente antes del inicio y SHALL aceptar un motivo opcional de hasta 1.000 caracteres. La cancelación SHALL conservar el registro y liberar el intervalo aprobado. Relación: Plan RF-08 y 2.4.

#### Scenario: Cancelación propia antes del inicio
- **GIVEN** una solicitud pendiente o aprobada cuyo inicio es futuro
- **WHEN** su solicitante la cancela
- **THEN** el sistema cambia el estado a `CANCELADA` y registra el evento

#### Scenario: Motivo opcional demasiado extenso
- **GIVEN** una solicitud propia cancelable y un motivo superior a 1.000 caracteres
- **WHEN** el solicitante intenta cancelarla
- **THEN** el sistema rechaza la entrada y conserva el estado existente

#### Scenario: Cancelación propia después del inicio
- **GIVEN** una reserva cuyo inicio ya ocurrió
- **WHEN** su solicitante intenta cancelarla
- **THEN** el sistema rechaza la operación y conserva el estado

#### Scenario: Cancelación de una reserva ajena
- **GIVEN** un solicitante sin permiso administrativo
- **WHEN** intenta cancelar la reserva de otro usuario
- **THEN** el sistema deniega la operación y conserva la reserva

#### Scenario: Fallo al registrar una cancelación propia
- **GIVEN** una reserva propia cancelable
- **WHEN** falla el registro del evento antes de confirmar la operación
- **THEN** el sistema revierte la cancelación y conserva el estado anterior sin evento huérfano

### Requirement: RF-08.2 Cancelación administrativa autorizada
El sistema SHALL permitir a Gestores de espacios y Administradores cancelar cualquier solicitud `PENDIENTE` o reserva `APROBADA` únicamente antes del inicio y con un motivo de 1 a 1.000 caracteres. Ningún actor SHALL cancelar una reserva cuyo inicio ya ocurrió. Relación: Plan RF-08 y 2.4.

#### Scenario: Cancelación administrativa con permiso
- **GIVEN** un gestor o administrador, una reserva cuyo inicio es futuro y un motivo válido
- **WHEN** cancela la reserva
- **THEN** el sistema cambia el estado a `CANCELADA` y registra actor, fecha y motivo

#### Scenario: Cancelación administrativa sin motivo válido
- **GIVEN** una reserva cancelable y un motivo vacío o superior a 1.000 caracteres
- **WHEN** un gestor o administrador intenta cancelarla
- **THEN** el sistema rechaza la entrada y conserva el estado existente

#### Scenario: Cancelación administrativa después del inicio
- **GIVEN** una reserva cuyo inicio ya ocurrió
- **WHEN** un gestor o administrador intenta cancelarla
- **THEN** el sistema rechaza la operación y conserva el estado

#### Scenario: Cancelación administrativa sin permiso
- **GIVEN** un usuario sin permiso explícito de cancelación administrativa
- **WHEN** intenta cancelar una reserva ajena
- **THEN** el sistema deniega la operación y no altera el historial

#### Scenario: Fallo al registrar una cancelación administrativa
- **GIVEN** una reserva cancelable, un motivo válido y un actor autorizado
- **WHEN** falla el registro del evento antes de confirmar la operación
- **THEN** el sistema revierte la cancelación y conserva el estado anterior sin evento huérfano

### Requirement: RF-09.1 Consulta del historial
El sistema SHALL conservar reservas de todos los estados. Solicitantes SHALL consultar solo las propias; Gestores y Administradores SHALL consultar todo el historial y filtrarlo por estado, espacio, solicitante y rango inclusivo de fechas de inicio en `America/Bogota`. La respuesta SHALL paginar 25 registros por defecto y admitir un máximo configurable de 100. Relación: Plan RF-09.

#### Scenario: Historial propio
- **GIVEN** un usuario autenticado con reservas anteriores
- **WHEN** consulta su historial
- **THEN** el sistema muestra sus reservas con espacio, intervalo, estado y fechas relevantes

#### Scenario: Historial administrativo autorizado
- **GIVEN** un gestor o administrador con permiso de consulta histórica
- **WHEN** consulta el historial con uno o más filtros permitidos
- **THEN** el sistema presenta todos los registros coincidentes dentro de una página y sin modificar su contenido

#### Scenario: Historial ajeno no autorizado
- **GIVEN** un usuario sin permiso para consultar datos de terceros
- **WHEN** intenta acceder mediante identificador o filtro al historial de otro solicitante
- **THEN** el sistema deniega el acceso y no expone los registros

#### Scenario: Límites inclusivos del rango de fechas
- **GIVEN** reservas que inician en las fechas inicial, intermedia y final del rango institucional solicitado
- **WHEN** un actor autorizado filtra el historial por `desde` y `hasta`
- **THEN** el sistema incluye los registros de ambas fechas límite y excluye los que inician fuera del rango

#### Scenario: Paginación predeterminada
- **GIVEN** más de 25 registros visibles para el actor
- **WHEN** consulta el historial sin indicar tamaño de página
- **THEN** el sistema devuelve como máximo 25 registros y los controles para navegar por las páginas

#### Scenario: Tamaño de página superior al máximo
- **GIVEN** una petición de más de 100 registros por página
- **WHEN** un actor autorizado consulta el historial
- **THEN** el sistema limita la página al máximo configurado de 100

### Requirement: RF-09.2 Minimización de datos visibles
El historial SHALL mostrar identificador, espacio, intervalo, estado, fecha de creación, fecha de cada evento, acciones, motivos, nombre y correo institucional cuando el actor tenga alcance. MUST NOT mostrar contraseñas, hashes, tokens, datos de sesión ni información de seguridad. Relación: Plan RF-03, RF-09 y riesgo R-02.

#### Scenario: Consulta administrativa del historial
- **GIVEN** un gestor o administrador autorizado
- **WHEN** consulta un registro histórico
- **THEN** el sistema muestra los campos operativos permitidos sin incluir credenciales ni datos de seguridad

#### Scenario: Consulta del solicitante
- **GIVEN** un solicitante autenticado
- **WHEN** consulta su historial
- **THEN** el sistema muestra únicamente sus datos y registros propios

### Requirement: RF-10.1 Registro de eventos relevantes
El sistema SHALL crear un evento inmutable para cada aprobación, rechazo y cancelación confirmada, asociado a reserva, responsable, acción, fecha y motivo u observación aportado. Un intento fallido MUST NOT registrarse como decisión exitosa. Relación: Plan RF-10 y EventoReserva.

#### Scenario: Evento de aprobación
- **GIVEN** una aprobación completada correctamente
- **WHEN** se confirma la transacción
- **THEN** existe exactamente un evento de aprobación asociado a la reserva y al responsable

#### Scenario: Operación rechazada
- **GIVEN** un intento de decisión que falla por permiso, transición o conflicto
- **WHEN** termina la operación
- **THEN** el historial no contiene un evento que represente falsamente la decisión como completada

#### Scenario: Conservación tras desactivar entidades relacionadas
- **GIVEN** eventos asociados a un usuario o espacio que posteriormente se desactiva
- **WHEN** un actor autorizado consulta el historial
- **THEN** los eventos conservan sus asociaciones y permanecen trazables

#### Scenario: Intento de editar o eliminar un evento
- **GIVEN** un evento de reserva confirmado
- **WHEN** un usuario intenta editarlo o eliminarlo mediante una operación ordinaria de la aplicación
- **THEN** el sistema rechaza la operación y conserva intactos sus datos y asociaciones

