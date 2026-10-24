# Reservas: protocolo de decisiones

## Regla de acceso

Las vistas no editan `Reserva.estado` directamente. Toda aprobación entra por
`aprobar_reserva()` y todo rechazo por `rechazar_reserva()`. Ambos servicios verifican
el permiso `usuarios.decidir_reservas` y aplican la máquina de estados. El estado no se
expone en ningún `ModelForm` ni se registra `Reserva` en el administrador de Django.

## Protocolo transaccional de aprobación

La aprobación se ejecuta en una transacción atómica con este orden:

1. localizar la referencia de la solicitud;
2. bloquear la fila del espacio con `SELECT ... FOR UPDATE`;
3. releer y bloquear la solicitud para evitar decisiones obsoletas;
4. comprobar que sigue pendiente y revalidar intervalo, espacio y horario;
5. volver a consultar conflictos aprobados del espacio y del solicitante;
6. cambiar el estado dentro de un punto de recuperación;
7. dejar que las dos restricciones de exclusión GiST de PostgreSQL actúen como
   última barrera frente a carreras.

Las restricciones usan rangos semiabiertos `[inicio, fin)`, por lo que permiten
reservas adyacentes. Una violación de integridad se revierte y se transforma en
`ConflictoReserva`; el mensaje presentado no contiene nombres de restricciones,
SQL ni otros detalles internos.

El bloqueo por espacio serializa decisiones concurrentes sobre el mismo recurso.
La exclusión por solicitante protege además carreras entre espacios diferentes. Las
pruebas de concurrencia usan hilos, conexiones independientes y transacciones reales
contra PostgreSQL.

Las cancelaciones, la desactivación y los cambios de horario adquieren los bloqueos
en el mismo orden estable: espacio y, cuando aplica, reserva. Después del bloqueo se
releen el estado, la disponibilidad y el horario antes de escribir. Esto evita que
una aprobación simultánea confirme una combinación incompatible o deje eventos
parciales.

## Duración máxima

Cada solicitud individual puede durar como máximo cuatro horas consecutivas. La
duración se calcula como la diferencia entre los instantes `fin` e `inicio`: un
intervalo de exactamente cuatro horas es válido y cualquier duración superior se
rechaza en la creación, la consulta de disponibilidad y la revalidación previa a
la aprobación.

La política no acumula solicitudes independientes. Dos intervalos adyacentes de
hasta cuatro horas se validan por separado, sin perjuicio de las demás reglas de
horario, disponibilidad y conflictos. Las reservas aprobadas antes de activar la
política se conservan sin cambios automáticos para mantener su trazabilidad.

## Transiciones

Solo se admiten `PENDIENTE → APROBADA|RECHAZADA|CANCELADA` y
`APROBADA → CANCELADA`. `RECHAZADA` y `CANCELADA` son terminales. Los casos de
uso de cancelación se incorporan en el incremento de ciclo de vida y auditoría.
