# Spec Delta: Dashboard y navegación según permisos

## Purpose

Define una experiencia autenticada descubrible en la que cada usuario puede recorrer desde la interfaz los módulos autorizados y obtener un resumen operativo acorde con sus permisos.

## ADDED Requirements

### Requirement: UI-01.1 Navegación global basada en permisos
El sistema SHALL presentar en todas las páginas autenticadas una navegación global con acceso a Inicio, Espacios, Perfil y a cada función autorizada para el usuario. Los accesos a solicitudes, disponibilidad, decisiones, historial, usuarios, espacios y horarios SHALL mostrarse según permisos; ocultarlos MUST NOT sustituir la autorización del servidor.

#### Scenario: Navegación de solicitante
- **GIVEN** un usuario autenticado con permiso para crear solicitudes propias
- **WHEN** visualiza cualquier página autenticada
- **THEN** encuentra enlaces operables a Inicio, Espacios, Mis solicitudes, Nueva solicitud, Disponibilidad y Perfil

#### Scenario: Navegación de gestor
- **GIVEN** un usuario autenticado con permisos para decidir y consultar el historial global
- **WHEN** visualiza cualquier página autenticada
- **THEN** encuentra enlaces operables a Inicio, Espacios, Solicitudes por gestionar e Historial global sin accesos de administración de usuarios o espacios que no posea

#### Scenario: Navegación de administrador
- **GIVEN** un usuario autenticado con permisos administrativos
- **WHEN** visualiza cualquier página autenticada
- **THEN** encuentra enlaces operables a Inicio, Espacios, Reservas, Historial y Usuarios, además de las acciones administrativas correspondientes

#### Scenario: Opción no autorizada
- **GIVEN** un usuario autenticado sin un permiso específico
- **WHEN** se construye la navegación
- **THEN** el acceso correspondiente no se muestra y una petición directa continúa siendo rechazada por el servidor

#### Scenario: Ubicación actual identificable
- **GIVEN** un usuario que navega por un módulo
- **WHEN** cambia entre páginas del sistema
- **THEN** la interfaz identifica visual y semánticamente la sección activa

### Requirement: UI-01.2 Dashboard autenticado y contextual
El sistema SHALL mostrar después de iniciar sesión un dashboard con saludo, indicadores, actividad reciente y accesos rápidos calculados únicamente sobre datos visibles para el usuario. Cada indicador SHALL enlazar al listado o acción correspondiente y SHALL presentar un estado vacío comprensible cuando no existan datos.

#### Scenario: Dashboard de solicitante
- **GIVEN** un solicitante autenticado con solicitudes propias
- **WHEN** accede al inicio
- **THEN** visualiza totales propios por estado, sus solicitudes recientes y accesos para consultar disponibilidad o crear una solicitud, sin datos de terceros

#### Scenario: Dashboard de gestor
- **GIVEN** un gestor autenticado
- **WHEN** accede al inicio
- **THEN** visualiza solicitudes pendientes y actividad reciente que puede gestionar, con accesos a decisiones e historial global

#### Scenario: Dashboard de administrador
- **GIVEN** un administrador autenticado
- **WHEN** accede al inicio
- **THEN** visualiza indicadores operativos de espacios, usuarios y reservas, junto con accesos a sus módulos de administración

#### Scenario: Dashboard sin datos
- **GIVEN** un usuario autenticado para cuyo alcance no existen registros
- **WHEN** accede al inicio
- **THEN** visualiza un estado vacío con una explicación y las acciones disponibles para comenzar

#### Scenario: Acceso anónimo al inicio
- **GIVEN** una persona sin sesión autenticada
- **WHEN** accede a la página inicial
- **THEN** el sistema presenta el acceso de autenticación sin revelar indicadores ni información protegida

### Requirement: UI-01.3 Recorridos enlazados y acciones contextuales
El sistema SHALL permitir completar los recorridos principales mediante enlaces y botones visibles dentro de la aplicación. Listados, detalles y formularios SHALL ofrecer retorno al contexto anterior y acciones primarias claramente diferenciadas, sin requerir que el usuario escriba una dirección manualmente.

#### Scenario: Recorrido para reservar
- **GIVEN** un solicitante autenticado en el dashboard o catálogo de espacios
- **WHEN** utiliza los accesos visibles
- **THEN** puede consultar disponibilidad, registrar una solicitud y regresar a sus solicitudes mediante navegación interna

#### Scenario: Recorrido para decidir
- **GIVEN** un gestor autenticado con solicitudes pendientes
- **WHEN** utiliza los accesos del dashboard o listado
- **THEN** puede abrir una solicitud, decidirla y volver al listado o historial mediante navegación interna

#### Scenario: Recorrido administrativo
- **GIVEN** un administrador autenticado
- **WHEN** utiliza los accesos visibles
- **THEN** puede gestionar usuarios, espacios y horarios y regresar a sus listados sin escribir direcciones manualmente
