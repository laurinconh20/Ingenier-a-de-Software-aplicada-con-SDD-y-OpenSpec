# Tasks

## 1. Regla temporal central

- [x] 1.1 Sustituir en `test_temporal_validation.py` la expectativa que acepta seis horas y añadir casos de menos de cuatro horas, exactamente cuatro, más de cuatro y dos intervalos adyacentes independientes; satisface RF-04.6 y termina cuando las pruebas expresan sin contradicciones todos los límites de la política.
- [x] 1.2 Definir la constante de dominio de cuatro horas e incorporar la comprobación en `validar_intervalo_temporal()` con un error comprensible asociado al intervalo; satisface RF-04.6 en `apps/reservas/services.py` y termina cuando las pruebas unitarias temporales pasan.
- [x] 1.3 Documentar en `apps/reservas/README.md` el alcance por solicitud individual, la igualdad permitida y la ausencia de acumulación entre solicitudes adyacentes; satisface RF-04.6 y termina cuando la documentación coincide con la especificación y las pruebas.

## 2. Creación y consulta de disponibilidad

- [x] 2.1 Añadir pruebas funcionales de creación para exactamente cuatro horas y para más de cuatro horas, verificando en este último caso el mensaje y la ausencia de una nueva `Reserva`; satisface RF-04.6 y termina cuando `test_create_request.py` demuestra ambos resultados mediante la ruta web.
- [x] 2.2 Añadir pruebas de disponibilidad que acepten cuatro horas y rechacen una duración superior aun dentro del horario habilitado; satisface RF-04.7 y termina cuando `test_availability.py` confirma que el intervalo excesivo nunca se presenta como reservable.
- [x] 2.3 Verificar que formulario, modelo y servicio de creación reutilizan la validación central sin escrituras directas que la omitan; satisface RF-04.6/RF-04.7 y termina cuando la revisión técnica y las pruebas focalizadas de solicitudes y disponibilidad pasan.

## 3. Aprobación y compatibilidad histórica

- [x] 3.1 Añadir una prueba de aprobación para una solicitud pendiente preexistente de más de cuatro horas, creada como dato legado, y verificar que permanece `PENDIENTE`, no genera evento y devuelve un error de dominio; satisface RF-04.7 y termina cuando `test_atomic_approval.py` pasa.
- [x] 3.2 Añadir una prueba de aprobación de exactamente cuatro horas que confirme estado `APROBADA` y un único evento; satisface RF-04.7 y termina cuando la ruta transaccional conserva las validaciones, bloqueos y auditoría existentes.
- [x] 3.3 Añadir una prueba de regresión para una reserva ya aprobada de más de cuatro horas y verificar que la activación de la regla no cambia automáticamente su estado, historial ni transiciones permitidas; satisface RF-04.7 y termina cuando la prueba de ciclo de vida pasa sin migración de datos.

## 4. Integración y trazabilidad

- [x] 4.1 Actualizar la matriz de trazabilidad con la cadena `Plan 2.4 → RF-04.6/RF-04.7 → reservation-duration-policy → tareas → componentes → pruebas` y verificar que la regla anterior de duración ilimitada ya no figure como comportamiento vigente.
- [x] 4.2 Ejecutar `python manage.py makemigrations --check --dry-run` y verificar que el cambio no introduce modificaciones de esquema ni dependencias nuevas.
- [x] 4.3 Ejecutar `openspec validate limite-cuatro-horas-consecutivas --strict`, la suite completa sobre PostgreSQL 17 y cobertura; termina cuando OpenSpec valida, todas las pruebas pasan y la cobertura de lógica crítica permanece al menos en 80 %.
