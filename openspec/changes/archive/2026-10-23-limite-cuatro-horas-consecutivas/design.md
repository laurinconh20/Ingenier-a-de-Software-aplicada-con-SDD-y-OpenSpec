# Design

## Context

Véase `proposal.md` para la motivación y `specs/reservation-duration-policy/spec.md` para el contrato observable. El sistema concentra las reglas de intervalos en `validar_intervalo_temporal()`: el modelo la invoca durante `full_clean()`, la consulta de disponibilidad la usa directamente y la aprobación la ejecuta nuevamente dentro de su transacción y después de adquirir los bloqueos.

La regla inicial aceptaba explícitamente duraciones mayores a cuatro horas. El cambio debe reemplazar ese comportamiento sin alterar el monolito modular, Django 5.2, PostgreSQL 17, los intervalos `[inicio, fin)`, la zona institucional ni el protocolo transaccional existente.

## Goals / Non-Goals

**Goals:**

- Mantener una única definición de la duración máxima para creación, disponibilidad y aprobación.
- Calcular la duración con datetimes conscientes de zona y permitir exactamente cuatro horas.
- Rechazar de forma controlada las solicitudes pendientes antiguas que incumplan la política cuando se intenten aprobar.
- Preservar los registros históricos y las reservas ya aprobadas sin migraciones destructivas.
- Mantener trazabilidad con RF-04 y pruebas de los límites temporales.

**Non-Goals:**

- Acumular la duración de solicitudes adyacentes independientes.
- Introducir cupos diarios, semanales o mensuales por usuario.
- Cancelar, rechazar o recortar automáticamente reservas existentes.
- Agregar campos, tablas, dependencias o una configuración administrativa del límite.

## Decisions

### 1. Regla central en la validación temporal

La duración máxima se representará como una constante de dominio de cuatro horas y se comprobará en `validar_intervalo_temporal()`. La condición inválida será `fin - inicio > cuatro horas`; la igualdad será válida. El error se asociará al fin o al intervalo con un mensaje explícito de máximo cuatro horas.

**Rationale:** todas las rutas relevantes ya convergen en este validador, por lo que se evita duplicar la política entre formulario, servicio de creación, disponibilidad y aprobación. **Alternativa descartada:** validarla únicamente en el formulario, porque una llamada directa al servicio o una aprobación posterior podría omitirla.

### 2. Duración entre instantes conscientes de zona

La resta se realizará sobre los datetimes conscientes recibidos, después de validar que incluyen zona horaria. No se calculará mediante horas de texto ni componentes locales aislados.

**Rationale:** conserva la semántica temporal existente y evita resultados ambiguos si la zona institucional cambia. `America/Bogota` no aplica cambios estacionales actualmente, pero el cálculo seguirá siendo correcto para instantes conscientes.

### 3. Revalidación prospectiva y sin mutación retroactiva

Las nuevas solicitudes y consultas de disponibilidad quedarán sujetas inmediatamente al límite. `aprobar_reserva()` conservará su revalidación temporal dentro de la transacción, de modo que una solicitud pendiente anterior a la política no podrá aprobarse si excede cuatro horas. No se ejecutará una migración de datos ni una actualización masiva sobre reservas ya aprobadas.

**Rationale:** aplica la nueva política a toda decisión futura sin falsear el historial ni realizar cancelaciones no autorizadas. **Alternativa descartada:** cancelar automáticamente reservas aprobadas, porque cambiaría estados y auditoría sin una decisión explícita prevista por el dominio.

### 4. Sin restricción de base de datos para la duración

No se añadirá un `CheckConstraint` máximo global en PostgreSQL. La validación de negocio se aplicará en las rutas ordinarias y se cubrirá con pruebas de servicio y modelo.

**Rationale:** una restricción incondicional impediría conservar filas históricas aprobadas de más de cuatro horas y podría hacer fallar la migración sobre datos existentes. Añadir una fecha de vigencia o un campo de excepción solo para sostener esa restricción ampliaría innecesariamente el modelo. Se mantiene la restricción de base de datos existente que exige `fin > inicio`.

### 5. Sustitución explícita de la expectativa anterior

La prueba que acepta seis horas cambiará para esperar rechazo. Se añadirán pruebas independientes para menos de cuatro horas, cuatro horas exactas, más de cuatro horas, disponibilidad, creación, aprobación de una solicitud antigua y conservación de una reserva aprobada preexistente.

**Rationale:** evita que la suite contenga expectativas contradictorias y demuestra el cambio de comportamiento en cada punto de entrada observable.

## Risks / Trade-offs

- **Escrituras directas que omitan `full_clean()`** → mantener la creación de solicitudes detrás del servicio vigente, revisar que las vistas no escriban directamente y cubrir servicio/modelo con pruebas.
- **Mensajes inconsistentes entre formulario y aprobación** → reutilizar la misma excepción del validador central y probar el texto funcional sin depender de detalles internos.
- **Confusión entre límite individual y acumulado** → documentar que solicitudes adyacentes se evalúan por separado; una política acumulativa futura requerirá otro cambio.
- **Datos preexistentes mayores a cuatro horas** → conservarlos como excepción histórica y bloquear solamente nuevas aprobaciones o solicitudes.

## Migration Plan

1. Cambiar primero las pruebas que expresan la regla anterior y añadir los nuevos casos de borde.
2. Incorporar la constante y la validación central sin modificar el esquema de datos.
3. Ejecutar pruebas unitarias, funcionales, de aprobación, disponibilidad y regresión completa sobre PostgreSQL 17.
4. Actualizar la trazabilidad y validar el cambio con OpenSpec en modo estricto.

El rollback consiste en revertir la validación y restaurar la expectativa anterior; no requiere revertir migraciones ni transformar datos.
