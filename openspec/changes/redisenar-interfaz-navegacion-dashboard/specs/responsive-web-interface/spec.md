# Spec Delta: Interfaz web adaptable

## MODIFIED Requirements

### Requirement: RNF-01.1 Operabilidad adaptable
La interfaz web SHALL mantener visibles y operables el contenido, la navegación, los formularios, los mensajes y las acciones principales a 320 y 1280 píxeles CSS de ancho. La navegación SHALL adaptarse sin perder destinos autorizados. La página MUST NOT producir desplazamiento horizontal; una tabla extensa MAY desplazarse dentro de un contenedor propio sin ocultar acciones.

#### Scenario: Flujo principal en ancho móvil
- **GIVEN** una ventana de 320 píxeles CSS de ancho
- **WHEN** un usuario recorre autenticación, catálogo, solicitud, decisión, cancelación e historial según sus permisos
- **THEN** puede leer el contenido y usar todos los controles sin desplazamiento horizontal de la página

#### Scenario: Flujo principal en ancho de escritorio
- **GIVEN** una ventana de 1280 píxeles CSS de ancho
- **WHEN** un usuario recorre los mismos flujos autorizados
- **THEN** el contenido y los controles permanecen visibles, ordenados y operables

#### Scenario: Tabla extensa en ancho móvil
- **GIVEN** una tabla de espacios o historial cuyo contenido excede 320 píxeles
- **WHEN** se presenta en una pantalla móvil
- **THEN** la tabla se adapta o dispone de desplazamiento en su propio contenedor sin desplazar toda la página ni ocultar las acciones

#### Scenario: Navegación móvil desplegable
- **GIVEN** una ventana de 320 píxeles CSS de ancho y un usuario autenticado
- **WHEN** abre y cierra la navegación
- **THEN** puede alcanzar mediante teclado o toque todos sus destinos autorizados sin que el menú cubra permanentemente el contenido

## ADDED Requirements

### Requirement: RNF-01.2 Consistencia visual y mejora progresiva
La interfaz SHALL usar patrones consistentes para títulos, acciones, formularios, estados, mensajes y contenido vacío. Las acciones esenciales MUST permanecer disponibles sin scripts cliente; las mejoras interactivas SHALL conservar etiquetas accesibles, foco visible y retroalimentación comprensible.

#### Scenario: Navegación y formularios sin scripts cliente
- **GIVEN** un navegador que no ejecuta scripts cliente
- **WHEN** un usuario navega, consulta o envía un formulario autorizado
- **THEN** puede completar la operación esencial mediante respuestas renderizadas por el servidor

#### Scenario: Error de validación visible
- **GIVEN** un formulario enviado con datos inválidos
- **WHEN** el servidor devuelve la página
- **THEN** la interfaz conserva los datos permitidos, identifica los campos con error y presenta mensajes asociados y comprensibles

#### Scenario: Confirmación de acción destructiva
- **GIVEN** una acción de cancelación o eliminación disponible para el usuario
- **WHEN** intenta ejecutarla
- **THEN** la interfaz solicita confirmación, describe el efecto y permite continuar o regresar sin cambios

#### Scenario: Estado de una reserva distinguible
- **GIVEN** una solicitud pendiente, aprobada, rechazada o cancelada
- **WHEN** se presenta en dashboard, listado o detalle
- **THEN** la interfaz comunica su estado mediante texto y un indicador visual que no depende únicamente del color

#### Scenario: Retroalimentación posterior a una acción
- **GIVEN** una operación confirmada correctamente o rechazada de forma controlada
- **WHEN** la respuesta se presenta al usuario
- **THEN** la interfaz muestra un mensaje visible que explica el resultado y conserva una ruta clara para continuar
