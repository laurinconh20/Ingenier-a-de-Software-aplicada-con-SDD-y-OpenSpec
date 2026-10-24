# Tareas

## 1. Revisión y base técnica

- [x] 1.1 Aprobar las ocho decisiones operativas de `design.md` y reconciliar las especificaciones afectadas; cubre RF-01 a RF-10 y se verifica con ausencia de políticas funcionales abiertas y `openspec validate sistema-reservas-espacios-academicos --strict` exitoso.
- [x] 1.2 Crear el proyecto monolítico modular con Python 3.13 y Django 5.2 LTS, separar configuración, presentación, negocio y persistencia, y crear `usuarios`, `espacios`, `reservas` y `auditoria`; satisface la base arquitectónica del Plan 3.1/3.5 y termina cuando Django ejecuta sus comprobaciones y las pruebas de humo pasan.
- [x] 1.3 Configurar PostgreSQL 17 para desarrollo y pruebas, manejo de secretos por entorno y zona `America/Bogota`; soporta RF-02 a RF-10 y termina cuando las migraciones y una prueba de conexión se ejecutan en una base limpia sin credenciales versionadas.
- [x] 1.4 Configurar pytest, pytest-django y pytest-cov con marcadores para pruebas unitarias, integración, funcionales, seguridad y concurrencia; soporta la estrategia del Plan 5.1 y termina cuando una prueba de muestra de cada configuración aplicable se descubre y ejecuta correctamente.

## 2. Identidad, usuarios, roles y permisos

- [x] 2.1 Definir el modelo de usuario con nombre, correo institucional normalizado y único, contraseña validada por Django y estado, más migraciones; satisface RF-02.1/RF-02.3 en `usuarios` y termina con pruebas de duplicidad, contraseñas inválidas, desactivación sin cambios automáticos y conservación de relaciones.
- [x] 2.2 Implementar inicio y cierre de sesión con los mecanismos de Django y mensajes que no revelen el dato incorrecto; satisface RF-02.2 en presentación y `usuarios` y termina con pruebas funcionales de credenciales válidas, inválidas y cuenta inactiva.
- [x] 2.3 Crear de forma repetible los grupos `Solicitante`, `Gestor de espacios` y `Administrador` y asignar los permisos aprobados; satisface RF-03.1 y termina con una prueba de carga repetida y una matriz automatizada rol-permiso conforme a la especificación revisada.
- [x] 2.4 Implementar registro administrado, edición propia limitada al nombre y cambios de correo, rol o estado exclusivos del Administrador; satisface RF-02.1/RF-02.3/RF-03.2 y termina con pruebas de acceso permitido, denegado y petición directa manipulada.
- [x] 2.5 Documentar la matriz aprobada de roles y permisos junto al módulo y verificar que cada permiso de RF-02/RF-03 tenga al menos una prueba positiva y una negativa; termina cuando la documentación y la suite coinciden.

## 3. Espacios y horarios habilitados

- [x] 3.1 Implementar `Espacio` con campos obligatorios, capacidad positiva, tipos cerrados y unicidad nombre–ubicación, y `HorarioEspacio` con ventanas semanales no superpuestas; satisface RF-01.1/RF-01.4 y termina con pruebas de restricciones y migraciones PostgreSQL.
- [x] 3.2 Implementar registro, consulta y actualización de espacios con tipo, ubicación, capacidad y características; satisface RF-01.1/RF-01.2/RF-01.3 en presentación, negocio y persistencia y termina con pruebas funcionales de casos válidos, inválidos e inexistentes.
- [x] 3.3 Implementar desactivación sin borrado e impedirla cuando existan reservas futuras aprobadas, además de impedir nuevas solicitudes para espacios inactivos; satisface RF-01.3 y termina con pruebas de bloqueo, cancelación previa y conservación histórica.
- [x] 3.4 Implementar varias ventanas no superpuestas por día de la semana, sin excepciones por fecha, y bloquear cambios que invaliden reservas futuras aprobadas; satisface RF-01.4 y termina con pruebas de días, límites, ventanas separadas/superpuestas y cancelación previa.
- [x] 3.5 Aplicar permisos de gestión de espacios en servidor y verificar RF-01 con pruebas positivas y negativas para cada rol; termina cuando ninguna petición directa no autorizada modifica el catálogo.

## 4. Solicitudes y disponibilidad

- [x] 4.1 Implementar `Reserva` con solicitante, espacio, inicio, fin, estado `PENDIENTE` inicial y fecha de creación, incluidas restricciones básicas y migraciones; satisface RF-04.1/RF-04.4 y termina con pruebas de modelo y persistencia.
- [x] 4.2 Implementar un validador central para inicio estrictamente futuro, fin posterior, mismo día, segundos en cero y semántica `[inicio, fin)`, sin anticipación adicional, horizonte ni duración máxima; satisface RF-04.2/RF-05.2 y termina con pruebas de todos los bordes, incluida una duración superior a cuatro horas aceptada cuando cumple las demás reglas.
- [x] 4.3 Implementar validación de espacio activo y contención completa en horarios habilitados; satisface RF-04.1/RF-04.3 y termina con pruebas de intervalo contenido, parcial, día cerrado y límites exactos.
- [x] 4.4 Implementar el servicio y formulario de creación de solicitudes propias para un solo espacio; satisface RF-04.1/RF-04.5 y termina con pruebas funcionales de creación válida, múltiples pendientes coincidentes, espacio inactivo y entrada inválida.
- [x] 4.5 Implementar consulta de solicitudes propias y protección frente al acceso directo a solicitudes ajenas; satisface RF-04.4/RF-03.2 y termina con pruebas funcionales de estados visibles, aislamiento y acceso denegado.
- [x] 4.6 Implementar consulta de disponibilidad por espacio, fecha e intervalo considerando solo reservas `APROBADA` como bloqueo; satisface RF-05.1 y termina con pruebas para estados pendiente, aprobada, rechazada y cancelada, además de espacio/horario no disponible.

## 5. Decisiones y prevención de conflictos

- [x] 5.1 Implementar la máquina de estados y servicios que impidan transiciones fuera de `PENDIENTE → APROBADA|RECHAZADA|CANCELADA` y `APROBADA → CANCELADA`; satisface RF-07.4 y termina con pruebas unitarias para todas las transiciones permitidas y prohibidas.
- [x] 5.2 Añadir mediante migración `btree_gist`, representación de rango e `ExclusionConstraint` condicional para impedir superposición de reservas aprobadas por espacio; satisface RF-06.1 y termina con pruebas de integración PostgreSQL para solapamiento y adyacencia.
- [x] 5.3 Añadir la restricción PostgreSQL equivalente para impedir superposición de reservas aprobadas por solicitante; satisface RF-06.2 y termina con pruebas entre espacios distintos, solapamiento y adyacencia.
- [x] 5.4 Implementar aprobación atómica con bloqueo de la fila del espacio, relectura, revalidación y traducción controlada de errores de integridad; satisface RF-06.3/RF-07.2 y termina con pruebas de éxito, disponibilidad modificada, rollback y mensaje sin detalles internos.
- [x] 5.5 Implementar decisiones sobre cualquier espacio para Gestores y Administradores, observación opcional de aprobación y motivo obligatorio de rechazo de 1 a 1.000 caracteres; satisface RF-07.1/RF-07.3 y termina con pruebas de alcance, límites, solicitante denegado y estados no pendientes.
- [x] 5.6 Ejecutar aprobaciones realmente simultáneas mediante conexiones/transacciones independientes sobre PostgreSQL; satisface RF-06.1/RF-06.3 y termina cuando repetidas carreras garantizan como máximo una aprobación, sin cambios parciales ni errores técnicos expuestos.
- [x] 5.7 Documentar el protocolo transaccional y verificar mediante revisión que toda ruta de aprobación usa el servicio atómico y no permite edición directa de estado; termina con revisión técnica y suite RF-06/RF-07 aprobada.

## 6. Cancelación, historial y auditoría

- [x] 6.1 Implementar `EventoReserva` inmutable con reserva, responsable, acción, fecha y motivo u observación de hasta 1.000 caracteres; satisface RF-10.1 y termina con pruebas de integridad, relaciones y protección frente a edición ordinaria.
- [x] 6.2 Integrar la creación del evento en la misma transacción que aprobación y rechazo; satisface RF-07.2/RF-07.3/RF-10.1 y termina con pruebas de exactamente un evento en éxito y ningún evento exitoso falso tras rollback.
- [x] 6.3 Implementar cancelación propia antes del inicio con motivo opcional de hasta 1.000 caracteres; satisface RF-08.1 y termina con pruebas de propiedad, límite de longitud, instante límite, estado terminal y liberación del intervalo.
- [x] 6.4 Implementar cancelación por Gestor o Administrador para cualquier espacio, solo antes del inicio y con motivo obligatorio de 1 a 1.000 caracteres, registrando el evento en la misma transacción; satisface RF-08.2/RF-10.1 y termina con pruebas de rol, límites, antes/después del inicio y rollback.
- [x] 6.5 Implementar historial propio y global administrativo, filtros por estado, espacio, solicitante y fechas, páginas de 25 con máximo 100, y exclusión de credenciales y datos de seguridad; satisface RF-09.1/RF-09.2/RF-03.2 y termina con pruebas de filtros, privacidad, límites y entidades desactivadas.
- [x] 6.6 Verificar la trazabilidad RF-08/RF-09/RF-10 en documentación del módulo y pruebas funcionales completas de cancelar y consultar historial; termina cuando cada escenario de las tres especificaciones tiene prueba identificable.

## 7. Integración y estabilización

- [x] 7.1 Ejecutar el flujo integral autenticación → consulta de espacio → solicitud → aprobación/rechazo → cancelación → historial para cada rol; verifica RF-01 a RF-10 y termina con todas las pruebas funcionales aprobadas.
- [x] 7.2 Ejecutar la suite completa sobre PostgreSQL 17, incluidas seguridad, concurrencia y regresión, y corregir defectos críticos; termina con 100 % de pruebas obligatorias aprobadas y ninguna carrera que produzca reservas incompatibles.
- [x] 7.3 Medir cobertura de la lógica de negocio crítica y completar pruebas faltantes hasta alcanzar al menos 80 % sin excluir artificialmente código relevante; verifica el criterio del Plan 5.4 y termina con un informe reproducible de pytest-cov.
- [x] 7.4 Documentar instalación local, variables, PostgreSQL, migraciones, creación de roles, ejecución y pruebas; satisface las condiciones de demostración del Plan 1.5/4.5 y termina cuando una instalación limpia puede seguir las instrucciones exitosamente.
- [x] 7.5 Completar la matriz `PLAN_INGENIERIA.md → RF → spec → tarea → componente → prueba` y revisar que la regla futura de cuatro horas no esté implementada ni tratada como vigente; termina con RF-01 a RF-10 sin vacíos y el cambio futuro explícitamente separado.

## 8. Correcciones derivadas de la revisión de especificaciones

- [x] 8.1 Verificar RF-02.2 con una prueba funcional de cierre de sesión que confirme invalidación del acceso autenticado; afecta `usuarios` y termina cuando el cliente debe autenticarse nuevamente para acceder a una ruta protegida.
- [x] 8.2 Aplicar la matriz RF-03.1/RF-04.1 para que crear solicitudes requiera capacidad `Solicitante`, sin herencia implícita desde Gestor o Administrador; afecta permisos, formulario y servicio de solicitudes y termina con pruebas positivas de Solicitante y negativas de cada rol sin esa capacidad, incluida suplantación manipulada.
- [x] 8.3 Completar RF-01.2/RF-01.3/RF-01.4 con pruebas de catálogo anónimo, actualización inválida/duplicada, horarios adyacentes y edición o eliminación directa no autorizada; termina cuando ningún caso rechazado modifica el catálogo.
- [x] 8.4 Probar RF-06.2 con aprobaciones simultáneas del mismo solicitante en espacios distintos y conexiones PostgreSQL independientes; termina cuando cada repetición conserva como máximo una aprobación y devuelve un conflicto de dominio sin detalles internos.
- [x] 8.5 Serializar y probar RF-06.3 para aprobación concurrente con cancelación, desactivación y cambio de horario usando un orden estable de bloqueo; termina cuando cada carrera confirma una sola combinación válida de estado, horario y evento, sin cambios parciales ni interbloqueos no controlados.
- [x] 8.6 Completar RF-07.3/RF-08.1/RF-08.2/RF-10.1 con pruebas de fallo al registrar eventos de rechazo y cancelación propia/administrativa; termina cuando cada fallo revierte el estado y no crea eventos huérfanos.
- [x] 8.7 Precisar RF-09.1/RF-09.2 en la consulta de historial: rango inclusivo sobre fecha de inicio en `America/Bogota`, fechas de creación/eventos visibles y acceso ajeno por identificador o filtro denegado; termina con pruebas de ambos límites, minimización y privacidad.
- [x] 8.8 Implementar y verificar RNF-01.1 en plantillas y estilos para 320 y 1280 píxeles CSS; termina con pruebas de los flujos principales sin pérdida de contenido, controles inaccesibles ni desplazamiento horizontal de la página.
- [x] 8.9 Actualizar la evidencia de trazabilidad y ejecutar `openspec validate sistema-reservas-espacios-academicos --strict`, la suite completa y cobertura después de 8.1–8.8; termina con todas las pruebas obligatorias aprobadas, cobertura crítica mínima de 80 % y matriz sin requisitos ni escenarios huérfanos.

## Matriz de trazabilidad de tareas

| Tareas | Requisitos / capacidad | Componentes previstos | Pruebas previstas |
|---|---|---|---|
| 2.1–2.5, 8.1–8.2 | RF-02, RF-03 / `identity-access` | usuarios, autenticación, grupos y permisos | modelos, login/logout, matriz de roles y peticiones manipuladas |
| 3.1–3.5, 8.3 | RF-01 / `academic-spaces` | espacios, horarios, permisos y persistencia | CRUD, restricciones, adyacencia, desactivación y accesos directos |
| 4.1–4.5, 8.2 | RF-04 / `reservation-requests` | reservas, validadores, formularios y privacidad | intervalos, horario, rol, suplantación, coincidencia pendiente y aislamiento |
| 4.2–4.3, 4.6 | RF-05 / `availability-conflict-control` | disponibilidad, zona e intervalos | estados bloqueantes, espacio/horario inválido, adyacencia y autenticación |
| 5.2–5.7, 8.4–8.5 | RF-06 / `availability-conflict-control` | transacciones, bloqueos y exclusiones GiST | carreras por espacio, por solicitante y contra cancelación/cambios del espacio |
| 5.1, 5.4–5.5, 6.2, 8.6 | RF-07 / `reservation-decisions` | máquina de estados, decisiones y eventos | autorización, límites, rollback y transiciones inválidas |
| 6.3–6.4, 6.6, 8.5–8.6 | RF-08 / `reservation-lifecycle-audit` | cancelación propia/administrativa | propiedad, permisos, instante límite, carreras, liberación y rollback |
| 4.5, 6.5–6.6, 8.7 | RF-09 / `reservation-lifecycle-audit` | historial, filtros, paginación y privacidad | alcance, fechas inclusivas, 25/100 registros y datos minimizados |
| 6.1–6.4, 6.6, 8.6 | RF-10 / `reservation-lifecycle-audit` | eventos y transacciones | inmutabilidad, exactamente un evento, asociaciones y ausencia de eventos falsos |
| 8.8 | RNF-01 / `responsive-web-interface` | plantillas y estilos | flujos funcionales a 320/1280 px y tablas en contenedor propio |
