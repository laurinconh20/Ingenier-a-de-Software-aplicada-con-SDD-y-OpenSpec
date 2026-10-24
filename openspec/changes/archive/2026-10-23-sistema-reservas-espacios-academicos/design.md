# Diseño técnico

## Context

Véase `proposal.md` para la motivación. El diseño parte de `PLAN_INGENIERIA.md`: aplicación web local o de demostración, arquitectura monolítica modular, Python 3.13, Django 5.2 LTS, Django Templates, Bootstrap 5.3 y PostgreSQL 17. La principal criticidad técnica es mantener autorización e integridad temporal ante aprobaciones concurrentes.

Los módulos lógicos son `usuarios`, `espacios`, `reservas` y `auditoria`, organizados en capas de presentación, lógica de negocio y persistencia. La zona institucional inicial es `America/Bogota`; las fechas se manejan con conciencia de zona horaria.

## Goals / Non-Goals

**Goals:**

- Preservar los límites del monolito modular y centralizar las reglas de negocio fuera de las vistas y plantillas.
- Mantener integridad referencial y temporal aun si dos aprobaciones se procesan simultáneamente.
- Aplicar autorización del lado servidor con los grupos y permisos de Django.
- Producir errores de dominio comprensibles sin filtrar detalles internos.
- Facilitar pruebas unitarias, integración PostgreSQL, funcionales, seguridad y concurrencia con trazabilidad RF → especificación → tarea → prueba.
- Mantener operables los flujos principales entre 320 y 1280 píxeles CSS sin pérdida de contenido ni desplazamiento horizontal de la página.

**Non-Goals:**

- Crear microservicios, SPA o API pública independiente.
- Incluir reservas recurrentes, integraciones externas, pagos, aplicaciones móviles nativas o alta disponibilidad productiva.
- Definir un límite máximo general de duración. La regla futura de cuatro horas queda excluida y requerirá otro cambio OpenSpec.

## Decisions

### 1. Monolito modular en tres capas

Cada módulo Django será dueño de su modelo y comportamiento, pero las operaciones que cruzan módulos se coordinarán mediante servicios de aplicación o dominio. Las vistas validarán entrada y permisos y delegarán reglas; las plantillas presentarán resultados; el ORM encapsulará persistencia.

**Rationale:** conserva la arquitectura aprobada y evita que reglas críticas queden duplicadas en formularios, vistas o plantillas. **Alternativa descartada:** microservicios, por complejidad operativa y consistencia distribuida innecesarias para el alcance académico.

### 2. Identidad basada en Django

Se utilizará el sistema de autenticación de Django, un modelo de usuario definido al iniciar el proyecto y grupos/permisos para `Solicitante`, `Gestor de espacios` y `Administrador`. Toda operación protegida verificará permisos en servidor.

**Rationale:** aprovecha controles maduros de contraseñas, sesiones y autorización. **Alternativa descartada:** autenticación propia, por riesgo de seguridad y trabajo no relacionado con el dominio.

### 3. Modelo relacional y conservación histórica

`Reserva` se relacionará mediante claves foráneas con solicitante y espacio y conservará `inicio`, `fin`, `estado` y fecha de creación. `HorarioEspacio` expresará ventanas habilitadas. `EventoReserva` conservará cada decisión confirmada. Usuarios y espacios se desactivarán en lugar de eliminarse cuando existan relaciones históricas.

**Rationale:** garantiza trazabilidad y evita registros huérfanos. **Alternativa descartada:** eliminación física en flujos ordinarios, porque contradice el historial requerido.

### 4. Intervalos y zona horaria

Las reservas usan intervalos semiabiertos `[inicio, fin)` y datetimes conscientes de zona horaria. La validación convierte el instante actual y los límites al contexto institucional para comprobar futuro y mismo día calendario.

**Rationale:** los intervalos semiabiertos permiten reservas adyacentes sin ambigüedad. **Alternativa descartada:** extremos cerrados, porque interpretaría como conflicto el instante compartido entre fin e inicio.

### 5. Defensa en profundidad contra conflictos

La consulta de disponibilidad se ejecutará en la lógica de negocio. Al aprobar se abrirá una transacción atómica, se bloqueará la fila del espacio, se releerá la solicitud, se comprobarán permisos, estado, horario y conflictos, y se intentará guardar la decisión y su evento juntos.

PostgreSQL reforzará el resultado mediante rangos temporales, índices GiST y restricciones de exclusión condicionales al estado `APROBADA`: una por `(espacio, intervalo)` y otra por `(solicitante, intervalo)`. La extensión `btree_gist` se habilitará mediante migración. Las violaciones se traducirán a conflictos de dominio y revertirán toda la transacción.

Las operaciones concurrentes usarán un orden estable de bloqueo: espacio, reserva y, cuando la exclusión por solicitante pueda intervenir, la garantía final de PostgreSQL. Cambios de horario, desactivación y aprobación que afecten al mismo espacio deberán serializarse mediante el mismo bloqueo del espacio. Aprobación y cancelación de una misma reserva bloquearán y releerán la fila antes de validar la transición.

**Rationale:** una comprobación previa aislada presenta una carrera TOCTOU; la base de datos debe ser la última barrera. **Alternativa descartada:** confiar solo en JavaScript, formularios o una consulta previa.

### 6. Máquina de estados explícita

Las operaciones de dominio serán las únicas vías para transicionar estados. Se admitirán `PENDIENTE → APROBADA|RECHAZADA|CANCELADA` y `APROBADA → CANCELADA`; `RECHAZADA` y `CANCELADA` serán terminales. La aprobación siempre repetirá validaciones dentro de la transacción.

**Rationale:** evita escrituras arbitrarias y simplifica pruebas e historial. **Alternativa descartada:** permitir editar directamente el estado desde formularios genéricos.

### 7. Auditoría transaccional de eventos

El evento de aprobación, rechazo o cancelación se guardará en la misma transacción que la transición. Los eventos no se editarán mediante flujos ordinarios. Los intentos fallidos podrán registrarse en logs técnicos, pero no como decisiones completadas en `EventoReserva`.

**Rationale:** impide que el historial contradiga el estado real. **Alternativa descartada:** señales asíncronas o escritura posterior, porque podrían dejar decisiones sin evento.

### 8. Estrategia de pruebas

Las reglas puras tendrán pruebas unitarias. Los modelos, permisos, vistas y transacciones tendrán pruebas de integración con PostgreSQL 17. Los flujos principales tendrán pruebas funcionales. La carrera de aprobación se probará con transacciones/conexiones independientes; SQLite no será sustituto para restricciones ni concurrencia. Se medirá cobertura con meta mínima del 80 % en lógica crítica, sin usarla como único criterio.

### 9. Interfaz adaptable verificable

Las plantillas renderizadas en servidor usarán estructura semántica y componentes adaptables. Las pruebas de presentación verificarán los flujos principales a 320 y 1280 píxeles CSS: el contenido y los controles deberán permanecer accesibles y la página no producirá desplazamiento horizontal. Las tablas podrán usar un contenedor desplazable propio cuando conservar columnas sea necesario.

**Rationale:** convierte la adaptabilidad exigida por el Plan en un criterio observable. **Alternativa descartada:** declarar la interfaz “responsive” sin anchos ni resultados comprobables.

## Traceability

| Plan | Capability | Componentes previstos | Pruebas principales |
|---|---|---|---|
| RF-01 | `academic-spaces` | `espacios`, presentación, persistencia | creación, edición, consulta, desactivación, horarios, permisos |
| RF-02 | `identity-access` | `usuarios`, autenticación Django | registro, login válido/inválido, inactividad, administración |
| RF-03 | `identity-access` | grupos, permisos, decoradores/mixins | acceso permitido y denegado, petición directa |
| RF-04 | `reservation-requests` | `reservas`, formularios/servicios | solicitudes válidas e inválidas, estados, privacidad |
| RF-05 | `availability-conflict-control` | consultas de reservas/horarios | disponibilidad, bordes `[inicio, fin)`, estados no bloqueantes |
| RF-06 | `availability-conflict-control` | transacciones, PostgreSQL, restricciones | superposición, solicitante, carrera concurrente, rollback |
| RF-07 | `reservation-decisions` | servicios de decisión, permisos | aprobación, rechazo, revalidación, transiciones inválidas |
| RF-08 | `reservation-lifecycle-audit` | cancelación, permisos | cancelación permitida/denegada y liberación del intervalo |
| RF-09 | `reservation-lifecycle-audit` | consultas históricas | historial propio/administrativo, privacidad, permanencia |
| RF-10 | `reservation-lifecycle-audit` | `auditoria`, transacciones | evento por decisión, ausencia de falsos eventos, responsable |
| RNF-01 | `responsive-web-interface` | plantillas y estilos | operación a 320/1280 px, contenido y controles accesibles |

## Risks / Trade-offs

- **Bloqueos o interbloqueos durante aprobaciones concurrentes** → mantener transacciones cortas, bloquear en orden estable, capturar errores operativos y probar carreras reproducibles.
- **Complejidad de restricciones condicionales con rangos** → validar migraciones directamente en PostgreSQL 17 y documentar la extensión `btree_gist`.
- **Diferencias entre validación de aplicación y base de datos** → compartir la semántica `[inicio, fin)` y probar cada borde contra ambas capas.
- **Cambios de zona horaria o interpretación de día calendario** → almacenar instantes conscientes de zona y centralizar la conversión institucional.
- **Carrera entre aprobación y cambio de horario/desactivación** → usar el mismo bloqueo del espacio, releer estado y horario y probar ambas operaciones simultáneas.
- **Carrera entre aprobación y cancelación** → bloquear la reserva, revalidar la transición y confirmar como máximo una decisión con un solo evento.
- **Conflicto concurrente del solicitante en espacios distintos** → mantener la exclusión PostgreSQL por solicitante, traducir la violación y probar conexiones independientes.
- **Alcance global de datos para gestores** → aplicar el permiso aprobado de historial global, minimizar campos visibles y cubrir accesos directos no autorizados.

## Operational Decisions

Estas políticas fueron aprobadas para la primera versión y concretan las reglas del plan:

1. **Catálogo de espacios:** nombre, tipo, ubicación, capacidad y estado son obligatorios; la capacidad es un entero mayor que cero y la combinación nombre–ubicación es única. Los tipos admitidos son `LABORATORIO`, `AUDITORIO` y `SALA_COMPUTO`; las características son opcionales.
2. **Cuentas:** el correo institucional es obligatorio, normalizado y único; las contraseñas usan los validadores configurados de Django. El usuario puede actualizar su nombre, mientras que correo, rol y estado requieren administración. Desactivar una cuenta impide autenticarse y crear solicitudes, pero no altera automáticamente reservas ni eventos existentes.
3. **Horarios:** un espacio admite varias ventanas no superpuestas por día de la semana. Las excepciones por fecha quedan fuera de la primera versión. No se permite desactivar un espacio ni cambiar su horario si ello invalida reservas futuras aprobadas; primero deben cancelarse. Las solicitudes pendientes se revalidan al aprobar.
4. **Tiempo de solicitud:** el inicio debe ser estrictamente futuro, sin anticipación mínima adicional ni horizonte máximo. Inicio y fin tienen precisión de minutos y segundos iguales a cero. No existe duración máxima en esta versión; la futura regla de cuatro horas permanece fuera de alcance.
5. **Alcance del gestor:** todo Gestor de espacios puede consultar y decidir solicitudes de todos los espacios. La asignación de gestores a espacios concretos queda fuera de alcance. El Administrador conserva todos los permisos de gestión.
6. **Motivos y observaciones:** rechazo y cancelación administrativa requieren un motivo de 1 a 1.000 caracteres. La observación de aprobación y el motivo de cancelación del solicitante son opcionales, con máximo de 1.000 caracteres. Todo valor aportado se conserva en auditoría.
7. **Límite de cancelación:** ningún actor puede cancelar cuando el inicio ya ocurrió. El solicitante cancela únicamente registros propios; gestores y administradores pueden cancelar cualquier solicitud pendiente o reserva aprobada antes del inicio.
8. **Historial:** el solicitante accede solo a sus registros. Gestores y administradores acceden al historial completo con filtros por estado, espacio, solicitante y rango de fechas. Se muestran nombre y correo institucional, nunca credenciales ni datos de seguridad. La página predeterminada contiene 25 registros y el máximo configurable es 100.
9. **Solicitudes por rol:** crear solicitudes requiere una cuenta activa con capacidad `Solicitante`. Un Gestor o Administrador solo podrá solicitar para sí mismo si también tiene asignada esa capacidad; los permisos administrativos no la conceden implícitamente.
10. **Rango del historial:** los filtros `desde` y `hasta` se aplican inclusivamente sobre la fecha de inicio de la reserva en `America/Bogota`; las fechas de creación y de eventos se muestran, pero no alteran ese filtro.

Las alternativas descartadas fueron introducir asignaciones gestor–espacio, calendarios excepcionales y cancelaciones retrospectivas en la primera versión, porque agregan modelos y reglas que no exige el alcance inicial.

## Migration Plan

1. Configurar el proyecto Django y la conexión de desarrollo/pruebas con PostgreSQL 17.
2. Crear extensiones y modelos base mediante migraciones versionadas.
3. Cargar grupos y permisos institucionales de forma repetible.
4. Incorporar módulos en el orden usuarios/roles → espacios/horarios → solicitudes/disponibilidad → decisiones/concurrencia → cancelación/auditoría.
5. Ejecutar migraciones y pruebas de cada incremento; realizar una prueba integral y de regresión antes de aceptar la versión.

Como aún no existe sistema productivo ni datos que migrar, el rollback inicial consiste en revertir las migraciones del incremento en el entorno de demostración y restaurar una copia de la base de datos cuando corresponda. No se realizará despliegue de alta disponibilidad.
