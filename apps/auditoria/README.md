# Auditoría y trazabilidad de reservas

`EventoReserva` es un registro inmutable. Guarda la reserva, el responsable, la
acción, la fecha y el motivo u observación. Sus relaciones usan `PROTECT`; desactivar
usuarios o espacios no elimina ni desasocia el historial. Los eventos solo se crean
desde los servicios transaccionales de aprobar, rechazar y cancelar.

## Trazabilidad de escenarios

| Requisito | Escenario | Prueba automatizada |
|---|---|---|
| RF-08.1 | cancelación propia pendiente/aprobada antes del inicio | `test_propietario_cancela_antes_del_inicio_y_registra_evento` |
| RF-08.1 | motivo propio mayor a 1.000 | `test_motivo_opcional_no_puede_superar_mil_caracteres` |
| RF-08.1 | en/después del inicio | `test_no_se_puede_cancelar_en_o_despues_del_inicio` |
| RF-08.1 | reserva ajena | `test_peticion_directa_para_cancelar_reserva_ajena_devuelve_403` |
| RF-08.1 | estado terminal y liberación | `test_estados_terminales_no_se_pueden_cancelar`, `test_cancelar_aprobada_libera_intervalo_para_otra_aprobacion` |
| RF-08.2 | Gestor/Administrador y evento | `test_gestor_y_administrador_cancelan_cualquier_reserva` |
| RF-08.2 | rol, motivo e instante no válidos | `test_solicitante_no_puede_cancelar_administrativamente`, `test_motivo_administrativo_debe_tener_entre_uno_y_mil`, `test_cancelacion_administrativa_no_procede_en_o_despues_del_inicio` |
| RF-08.2 | atomicidad | `test_fallo_de_evento_revierte_cancelacion_administrativa` |
| RF-09.1 | historial propio aislado | `test_solicitante_solo_consulta_su_historial` |
| RF-09.1 | acceso global autorizado y filtros | `test_historial_global_filtra_estado_espacio_solicitante_y_fechas` |
| RF-09.1 | acceso global denegado | `test_solicitante_no_autorizado_recibe_403_en_historial_global` |
| RF-09.1 | página 25 y máximo 100 | `test_paginacion_predeterminada_es_25_y_el_maximo_es_100` |
| RF-09.2 | datos operativos y exclusión de secretos | `test_entidades_desactivadas_y_eventos_siguen_trazables_sin_credenciales` |
| RF-10.1 | evento de aprobación/rechazo | `test_aprobacion_crea_exactamente_un_evento_con_observacion`, `test_rechazo_crea_exactamente_un_evento_con_motivo` |
| RF-10.1 | intento fallido sin evento falso | `test_conflicto_no_crea_evento_exitoso_falso` |
| RF-10.1 | inmutabilidad y conservación | `test_evento_no_admite_edicion_ni_eliminacion_ordinaria`, `test_relaciones_protegidas_impiden_perder_trazabilidad` |

La suite se ejecuta con:

```powershell
.\.venv\Scripts\python.exe -m pytest apps\auditoria\tests apps\reservas\tests\test_own_cancellation.py apps\reservas\tests\test_admin_cancellation.py apps\reservas\tests\test_history.py
```
