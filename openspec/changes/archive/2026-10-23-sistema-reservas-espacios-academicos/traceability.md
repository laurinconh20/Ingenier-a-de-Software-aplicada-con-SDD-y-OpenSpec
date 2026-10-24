# Matriz de trazabilidad

Cadena verificada: `PLAN_INGENIERIA.md → requisito → especificación OpenSpec → tarea → componente → prueba`.

| Plan | RF | Especificación OpenSpec | Tareas | Componentes principales | Pruebas previstas y ejecutadas |
|---|---|---|---|---|---|
| 1.2, 2.2, 2.3, 3.3 | RF-01 | `academic-spaces` RF-01.1 a RF-01.4 | 3.1–3.5, 8.3 | `apps/espacios/models.py`, `forms.py`, `services.py`, `views.py` | `test_models.py`, `test_views.py`, `test_schedules.py`, `test_deactivation.py` |
| 1.2, 2.2, 3.2, 3.3 | RF-02 | `identity-access` RF-02.1 a RF-02.3 | 2.1, 2.2, 2.4, 8.1–8.2 | `apps/usuarios/models.py`, `forms.py`, `views.py` | `test_models.py`, `test_authentication.py`, `test_user_management.py` |
| 1.3, 2.2, 3.3, riesgo R-02 | RF-03 | `identity-access` RF-03.1 y RF-03.2 | 2.3, 2.5, 3.5, 8.2 | `apps/usuarios/roles.py`, permisos Django y mixins de vistas | `test_roles.py`, `test_user_management.py`, `apps/espacios/tests/test_views.py`, `test_create_request.py` |
| 1.6, 2.2, 2.4 | RF-04 | `reservation-requests` RF-04.1 a RF-04.5 | 4.1–4.5, 8.2 | `apps/reservas/models.py`, `forms.py`, `services.py`, `views.py` | `test_models.py`, `test_temporal_validation.py`, `test_schedule_validation.py`, `test_create_request.py`, `test_own_requests.py` |
| 2.4 | RF-04.6, RF-04.7 | `reservation-duration-policy` | 1.1–4.3 de `limite-cuatro-horas-consecutivas` | `apps/reservas/services.py` y reutilización desde modelo, formulario, disponibilidad, creación y aprobación | `test_temporal_validation.py`, `test_create_request.py`, `test_availability.py`, `test_atomic_approval.py`, `test_own_cancellation.py` |
| 1.2, 2.4, riesgo R-07 | RF-05 | `availability-conflict-control` RF-05.1 y RF-05.2 | 4.2, 4.3, 4.6 | validadores temporales/horarios y `esta_disponible()` | `test_temporal_validation.py`, `test_schedule_validation.py`, `test_availability.py` |
| 1.6, 3.4, 5.1, riesgo R-01 | RF-06 | `availability-conflict-control` RF-06.1 a RF-06.3 | 5.2–5.7, 8.4–8.5 | restricciones GiST, bloqueos estables y `aprobar_reserva()` | `test_space_exclusion.py`, `test_requester_exclusion.py`, `test_atomic_approval.py`, `test_concurrent_approval.py`, `test_concurrent_space_operations.py` |
| 1.2, 2.4, 3.4 | RF-07 | `reservation-decisions` RF-07.1 a RF-07.4 | 5.1, 5.4, 5.5, 6.2, 8.5–8.6 | máquina de estados, servicios y vistas de decisión | `test_state_machine.py`, `test_decisions.py`, `test_atomic_approval.py`, `test_decision_events.py`, `test_concurrent_space_operations.py` |
| 1.2, 2.4 | RF-08 | `reservation-lifecycle-audit` RF-08.1 y RF-08.2 | 5.1, 6.3, 6.4, 6.6, 8.5–8.6 | servicios y vistas de cancelación propia/administrativa | `test_own_cancellation.py`, `test_admin_cancellation.py`, `test_concurrent_space_operations.py` |
| 1.2, 2.2, 3.3 | RF-09 | `reservation-lifecycle-audit` RF-09.1 y RF-09.2 | 4.5, 6.5, 6.6, 8.7 | listas propia/global, filtros, paginación y plantillas | `test_own_requests.py`, `test_history.py` |
| 1.1, 2.2, 3.3 | RF-10 | `reservation-lifecycle-audit` RF-10.1 | 6.1, 6.2, 6.3, 6.4, 6.6, 8.5–8.6 | `apps/auditoria/models.py`, `services.py` e integración transaccional | `test_models.py`, `test_decision_events.py`, pruebas de cancelación, concurrencia y rollback |
| 1.4, 3.2 | RNF-01 | `responsive-web-interface` RNF-01.1 | 8.8 | `templates/`, `static/css/app.css` | `tests/test_responsive_ui.py`, `tests/test_end_to_end.py` |

La integración transversal está cubierta por `tests/test_end_to_end.py`. La suite
completa (`pytest -q`) ejecuta 195 pruebas sobre PostgreSQL 17 y la medición
`pytest --cov=apps --cov-report=term-missing -q` alcanza 97 % global.

## Regla institucional de cuatro horas

El cambio OpenSpec independiente `limite-cuatro-horas-consecutivas` incorpora los
requisitos RF-04.6 y RF-04.7: cada solicitud individual admite una duración máxima
de cuatro horas consecutivas, incluida exactamente esa duración. Las solicitudes
adyacentes se validan de manera independiente.

La política se aplica al crear solicitudes, consultar disponibilidad y volver a
validar una aprobación. Las reservas históricas ya aprobadas no se modifican de
forma automática y conservan sus transiciones de ciclo de vida permitidas. Esta
evolución sigue el proceso de gestión de cambios definido en `PLAN_INGENIERIA.md` 6.7.
