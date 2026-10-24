# Spec Delta: Identidad y control de acceso

## Purpose

Define la administración segura de cuentas, la autenticación y la autorización por roles para proteger las operaciones y los datos del sistema de reservas.

## ADDED Requirements

### Requirement: RF-02.1 Registro administrado de usuarios
El sistema SHALL permitir registrar usuarios únicamente a un Administrador autorizado. Nombre y correo institucional son obligatorios; el correo SHALL normalizarse y ser único. La contraseña MUST cumplir los validadores configurados de Django y nunca almacenarse ni mostrarse en texto claro. Relación: Plan RF-02, 2.3 y 3.3.

#### Scenario: Registro autorizado
- **GIVEN** un administrador autenticado con permiso de crear usuarios y datos que cumplen las validaciones vigentes
- **WHEN** registra la cuenta
- **THEN** el sistema crea un usuario en estado activo sin exponer su credencial en texto claro

#### Scenario: Registro sin autorización
- **GIVEN** un usuario autenticado sin permiso de crear usuarios
- **WHEN** intenta registrar una cuenta
- **THEN** el sistema rechaza la operación, no crea datos y presenta un resultado de acceso denegado

#### Scenario: Datos de registro inválidos
- **GIVEN** un administrador autorizado y datos incompletos, un correo ya registrado o una contraseña que incumple los validadores
- **WHEN** intenta registrar al usuario
- **THEN** el sistema no crea la cuenta e identifica los campos que requieren corrección sin revelar información sensible

### Requirement: RF-02.2 Autenticación de usuarios activos
El sistema SHALL autenticar mediante los mecanismos de seguridad de Django solamente cuentas activas con credenciales válidas, SHALL establecer una sesión protegida y SHALL permitir cerrarla invalidando el acceso autenticado. Actor: cualquier usuario registrado. Relación: Plan 2.2 RF-02, 3.2 y 3.3.

#### Scenario: Inicio de sesión exitoso
- **GIVEN** una cuenta activa y credenciales válidas
- **WHEN** el usuario inicia sesión
- **THEN** el sistema establece una sesión autenticada y permite acceder a las funciones correspondientes a sus permisos

#### Scenario: Credenciales inválidas
- **GIVEN** una cuenta inexistente o una credencial incorrecta
- **WHEN** se intenta iniciar sesión
- **THEN** el sistema rechaza el acceso con un mensaje que no permite inferir cuál dato falló

#### Scenario: Cuenta inactiva
- **GIVEN** una cuenta inactiva con credenciales correctas
- **WHEN** se intenta iniciar sesión
- **THEN** el sistema rechaza la autenticación y no establece una sesión

#### Scenario: Cierre de sesión
- **GIVEN** un usuario con sesión autenticada
- **WHEN** solicita cerrar la sesión
- **THEN** el sistema invalida la sesión y las funciones protegidas vuelven a exigir autenticación

### Requirement: RF-02.3 Administración de datos y estado de usuario
El sistema SHALL permitir al usuario actualizar su propio nombre. Solamente un Administrador autorizado SHALL cambiar correo, rol o estado. Desactivar una cuenta MUST impedir autenticación y nuevas solicitudes, sin alterar automáticamente sus solicitudes, reservas ni eventos existentes. Relación: Plan RF-02 y 3.3.

#### Scenario: Actualización autorizada
- **GIVEN** un administrador con permiso y una cuenta existente
- **WHEN** actualiza datos válidos de la cuenta
- **THEN** el sistema persiste los cambios y mantiene sus reservas y eventos asociados

#### Scenario: Usuario actualiza su nombre
- **GIVEN** un usuario autenticado
- **WHEN** actualiza su propio nombre con un valor válido
- **THEN** el sistema persiste el nombre sin permitirle cambiar correo, rol ni estado

#### Scenario: Usuario intenta cambiar un campo administrativo
- **GIVEN** un usuario autenticado sin permiso de administración
- **WHEN** intenta cambiar su correo, rol o estado mediante una petición directa
- **THEN** el sistema deniega la modificación y conserva los valores existentes

#### Scenario: Desactivación con historial
- **GIVEN** un administrador con permiso y una cuenta con solicitudes, reservas o eventos existentes
- **WHEN** desactiva la cuenta
- **THEN** el sistema impide nuevas autenticaciones y solicitudes, y conserva sin cambios las reservas y la trazabilidad existentes

#### Scenario: Administración no autorizada
- **GIVEN** un actor sin el permiso requerido
- **WHEN** intenta consultar o modificar datos administrativos de otra cuenta
- **THEN** el sistema deniega la operación sin alterar ni exponer los datos protegidos

### Requirement: RF-03.1 Roles y permisos institucionales
El sistema SHALL representar los roles `Solicitante`, `Gestor de espacios` y `Administrador` mediante grupos y permisos explícitos. `Solicitante` gestiona solicitudes propias; `Gestor de espacios` decide, cancela administrativamente y consulta historial global; `Administrador` incorpora además gestión de usuarios, espacios y horarios. Una capacidad no SHALL heredarse implícitamente de otra. Relación: Plan 1.3, RF-03 y 3.3.

#### Scenario: Operación permitida por rol
- **GIVEN** un usuario autenticado cuyo rol concede el permiso requerido
- **WHEN** solicita una operación protegida
- **THEN** el sistema permite continuar y aplica las reglas de negocio de la operación

#### Scenario: Operación denegada por rol
- **GIVEN** un usuario autenticado cuyo rol no concede el permiso requerido
- **WHEN** solicita una operación protegida, incluso mediante una petición directa
- **THEN** el sistema deniega la operación y no modifica datos

#### Scenario: Rol administrativo sin capacidad de solicitante
- **GIVEN** un Gestor o Administrador que no tiene asignada la capacidad `Solicitante`
- **WHEN** intenta registrar una solicitud propia
- **THEN** el sistema deniega la operación sin crear una solicitud

### Requirement: RF-03.2 Protección consistente de interfaces y operaciones
El sistema MUST validar autorización en el servidor para cada operación protegida; ocultar controles en la interfaz no SHALL sustituir esta validación. Actor: todos. Relación: Plan RF-03, riesgo R-02 y pruebas de seguridad de 5.1.

#### Scenario: Manipulación directa de una petición
- **GIVEN** un usuario sin permiso que conoce la dirección o los parámetros de una operación administrativa
- **WHEN** envía la petición directamente
- **THEN** el servidor rechaza la operación y conserva el estado anterior

#### Scenario: Usuario no autenticado
- **GIVEN** una persona sin sesión autenticada
- **WHEN** solicita una función reservada para usuarios registrados
- **THEN** el sistema exige autenticación y no ejecuta la función

