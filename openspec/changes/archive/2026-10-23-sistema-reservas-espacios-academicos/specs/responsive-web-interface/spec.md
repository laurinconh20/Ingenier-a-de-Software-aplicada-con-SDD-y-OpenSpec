# Spec Delta: Interfaz web adaptable

## Purpose

Define criterios observables para que los flujos principales de reservas conserven contenido, navegación y operabilidad en pantallas móviles y de escritorio.

## ADDED Requirements

### Requirement: RNF-01.1 Operabilidad adaptable
La interfaz web SHALL mantener visibles y operables el contenido, la navegación, los formularios, los mensajes y las acciones principales a 320 y 1280 píxeles CSS de ancho. La página MUST NOT producir desplazamiento horizontal; una tabla extensa MAY desplazarse dentro de un contenedor propio sin ocultar acciones.

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
