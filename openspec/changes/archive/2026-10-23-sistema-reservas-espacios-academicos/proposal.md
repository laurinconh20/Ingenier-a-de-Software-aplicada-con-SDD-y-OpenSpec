# Propuesta: Sistema de gestión de reservas de espacios académicos

## Why

La institución gestiona actualmente laboratorios, auditorios y salas de cómputo mediante correos y hojas de cálculo, lo que provoca duplicidades, conflictos de horario y baja trazabilidad. Se requiere una aplicación web centralizada que formalice el ciclo completo de solicitud, decisión, cancelación e historial con controles de acceso e integridad verificables.

## What Changes

- Incorporar la administración de usuarios mediante la autenticación de Django y el control de acceso basado en los roles `Solicitante`, `Gestor de espacios` y `Administrador`.
- Incorporar el registro, consulta, actualización, desactivación y configuración de horarios de funcionamiento de los espacios académicos.
- Permitir a usuarios autorizados consultar disponibilidad y registrar solicitudes para un único espacio, en un único día y dentro de su horario habilitado.
- Validar fechas, intervalos y disponibilidad con semántica `[inicio, fin)`; las solicitudes pendientes pueden coincidir y no bloquean disponibilidad definitiva.
- Impedir que existan reservas aprobadas superpuestas para un mismo espacio o para un mismo solicitante, incluso ante aprobaciones concurrentes.
- Incorporar aprobación, rechazo y cancelación mediante transiciones de estado controladas y permisos explícitos.
- Conservar historial y eventos trazables de aprobación, rechazo y cancelación, incluidos responsable, fecha y observaciones aplicables.
- Proporcionar una interfaz web adaptable que conserve contenido, navegación y operaciones en pantallas móviles y de escritorio.
- Preparar pruebas unitarias, de integración, funcionales, seguridad, concurrencia y regresión sobre PostgreSQL para los comportamientos especificados.
- Mantener fuera de alcance reservas recurrentes, integraciones externas, aplicaciones móviles nativas, alta disponibilidad y cualquier límite máximo general de duración.
- Excluir expresamente la futura regla institucional de máximo cuatro horas consecutivas; se gestionará mediante un cambio OpenSpec independiente.

## Capabilities

### New Capabilities

- `identity-access`: Registro administrado, autenticación, datos de usuario, roles y permisos de acceso (RF-02, RF-03).
- `academic-spaces`: Registro, consulta, actualización, desactivación, características y horarios habilitados de espacios (RF-01).
- `reservation-requests`: Creación y consulta de solicitudes con validación de solicitante, espacio, fecha e intervalo (RF-04).
- `availability-conflict-control`: Consulta de disponibilidad y prevención transaccional de superposiciones por espacio y solicitante (RF-05, RF-06).
- `reservation-decisions`: Aprobación y rechazo por actores autorizados mediante estados y transiciones válidas (RF-07).
- `reservation-lifecycle-audit`: Cancelación, historial y trazabilidad de eventos y responsables (RF-08, RF-09, RF-10).
- `responsive-web-interface`: Presentación adaptable y operable en anchos móviles y de escritorio (RNF-01, Plan 1.4 y 3.2).

### Modified Capabilities

Ninguna. El proyecto no contiene especificaciones previas.

## Impact

- Nueva aplicación monolítica modular con módulos Django `usuarios`, `espacios`, `reservas` y `auditoria`, separando presentación, negocio y persistencia.
- Persistencia relacional en PostgreSQL 17 con claves foráneas, restricciones de integridad, transacciones atómicas, bloqueo de la fila del espacio y restricción de exclusión para intervalos aprobados.
- Interfaz renderizada con Django Templates y Bootstrap 5.3, adaptable a distintos dispositivos.
- Dependencias principales: Python 3.13, Django 5.2 LTS, PostgreSQL 17, pytest, pytest-django y pytest-cov.
- La implementación deberá conservar trazabilidad desde `PLAN_INGENIERIA.md` hacia requisitos, tareas y pruebas.
