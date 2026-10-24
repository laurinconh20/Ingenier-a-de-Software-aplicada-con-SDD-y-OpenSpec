# Informe final — Sistema de Gestión de Reservas Académicas

## 1. Resumen ejecutivo

El proyecto desarrolló una aplicación web centralizada para administrar espacios académicos y sus reservas. La solución reemplaza el manejo disperso mediante correos y hojas de cálculo por flujos controlados de consulta, solicitud, aprobación, rechazo, cancelación e historial.

El sistema fue construido como un monolito modular con Django 5.2, Django Templates, Bootstrap 5.3 y PostgreSQL 17, respetando las decisiones registradas en el plan de ingeniería. La implementación incorpora autenticación, autorización por permisos, validaciones temporales, prevención de conflictos concurrentes, trazabilidad y una interfaz adaptable con navegación según el rol.

La verificación final ejecutada el 24 de octubre de 2026 obtuvo **218 pruebas aprobadas** y una cobertura global de **96,79 %**, superior al objetivo mínimo del 80 %. `manage.py check` no reportó problemas y `makemigrations --check --dry-run` confirmó que no existen cambios de modelo pendientes.

## 2. Objetivos alcanzados

Se implementaron los siguientes módulos y capacidades:

- Gestión de usuarios mediante correo institucional, perfiles, activación y asignación de roles.
- Autenticación y cierre de sesión mediante los mecanismos de seguridad de Django.
- Roles de Solicitante, Gestor de espacios y Administrador con permisos diferenciados.
- Registro, consulta, actualización y desactivación controlada de espacios académicos.
- Configuración de horarios de funcionamiento sin ventanas superpuestas.
- Consulta de disponibilidad por espacio e intervalo.
- Creación y consulta de solicitudes propias.
- Validación de fechas, mismo día calendario, horarios habilitados y duración máxima.
- Aprobación, rechazo y cancelación con transiciones de estado controladas.
- Prevención de superposición por espacio y por solicitante.
- Protección ante aprobaciones simultáneas mediante transacciones y restricciones de PostgreSQL.
- Registro de eventos y consulta del historial global.
- Dashboard contextual y navegación visible según los permisos efectivos.
- Interfaz adaptable con estados, mensajes, confirmaciones y mejora progresiva.

## 3. Aplicación de Spec-Driven Development

El desarrollo utilizó OpenSpec para separar planificación, especificación, diseño, tareas e implementación. Los requisitos se expresaron mediante identificadores y escenarios verificables en formato GIVEN, WHEN, THEN.

El directorio `openspec/` conserva las especificaciones vigentes y el registro de cambios. Los cambios principales son:

| Cambio | Propósito | Estado actual |
|---|---|---|
| `sistema-reservas-espacios-academicos` | Especificar e implementar la versión inicial del sistema | Archivado |
| `limite-cuatro-horas-consecutivas` | Incorporar la nueva restricción institucional como cambio independiente | Archivado |
| `alinear-especificacion-limite-cuatro-horas` | Alinear la especificación principal con la regla aprobada | Archivado |
| `redisenar-interfaz-navegacion-dashboard` | Mejorar navegación, dashboard, consistencia y adaptación de la interfaz | Implementado y validado; pendiente de archivo |

La regla de cuatro horas no fue incluida retroactivamente en la especificación inicial. Se gestionó como una solicitud de cambio separada, demostrando el flujo de evolución controlada requerido por SDD.

## 4. Arquitectura y decisiones técnicas

### 4.1. Arquitectura aplicada

Se mantuvo la arquitectura monolítica modular definida en el plan:

- `apps/usuarios`: cuentas, autenticación, roles y permisos.
- `apps/espacios`: catálogo y horarios de funcionamiento.
- `apps/reservas`: solicitudes, disponibilidad y ciclo de vida.
- `apps/auditoria`: eventos y trazabilidad.
- `templates/` y `static/`: presentación renderizada por el servidor.
- `config/`: configuración, rutas y dashboard transversal.

La lógica de negocio permanece separada de las vistas mediante servicios de dominio. Las vistas coordinan solicitudes HTTP y mensajes, mientras que los modelos y servicios aplican validaciones, transacciones y cambios de estado.

### 4.2. Persistencia y concurrencia

PostgreSQL se mantuvo como base de datos porque proporciona transacciones, bloqueos e índices adecuados para proteger intervalos temporales. La prevención de conflictos combina:

1. Validación de disponibilidad en la lógica de negocio.
2. Operaciones atómicas y bloqueo durante la aprobación.
3. Restricciones de exclusión para impedir reservas aprobadas superpuestas del mismo espacio o del mismo solicitante.

Los intervalos se interpretan como `[inicio, fin)`, por lo que una reserva puede comenzar exactamente cuando termina otra.

### 4.3. Presentación

Se conservaron Django Templates y Bootstrap 5.3, sin introducir una SPA. El rediseño añadió componentes reutilizables, estilos locales, navegación basada en permisos y JavaScript ligero para mejoras de interacción. La autorización del servidor continúa siendo la fuente de seguridad; ocultar enlaces no reemplaza las comprobaciones de permisos.

## 5. Cambios y decisiones modificadas

Durante el proyecto se realizaron ajustes justificados:

- **Base de datos local:** la autenticación del superusuario PostgreSQL instalado localmente bloqueó la configuración inicial. Se adoptó un contenedor PostgreSQL 17 aislado en el puerto 5433, con credenciales propias del proyecto. Esto conserva la tecnología elegida y evita depender de credenciales administrativas externas.
- **Duración máxima:** el plan inicial no fijaba un máximo general. La regla institucional de cuatro horas se incorporó posteriormente mediante un cambio OpenSpec independiente y con pruebas específicas.
- **Interfaz inicial:** aunque las funciones existían, varias sólo eran accesibles conociendo sus URLs. Se propuso e implementó un cambio adicional para incorporar dashboard, menú por permisos, acciones contextuales y diseño adaptable.
- **Mejora progresiva:** las confirmaciones, el menú móvil y los estados de envío utilizan JavaScript local, pero las operaciones esenciales continúan funcionando mediante formularios renderizados por Django.

Estos cambios no sustituyeron el framework, la arquitectura, la persistencia ni las reglas de concurrencia definidas en el plan.

## 6. Dificultades encontradas

### Configuración de PostgreSQL

El primer intento dependía de la contraseña del usuario local `postgres`, que no estaba disponible. La solución fue encapsular la base de datos con Docker Compose, generar credenciales específicas y documentar comandos de configuración y diagnóstico.

### Prevención de condiciones de carrera

Una consulta previa de disponibilidad no era suficiente para solicitudes simultáneas. Fue necesario combinar validaciones, transacciones, bloqueos y restricciones de exclusión en la base de datos. Las pruebas concurrentes utilizan conexiones independientes para comprobar el comportamiento real.

### Coherencia entre permisos e interfaz

El sistema debía mostrar acciones diferentes por rol sin convertir la interfaz en el control de seguridad. La solución mantiene permisos en las vistas y servicios, y usa esos mismos permisos únicamente para construir la navegación visible.

### Evolución de requisitos

La regla de cuatro horas apareció después de la especificación inicial. OpenSpec permitió registrarla, analizar su impacto, implementarla y alinear la documentación sin alterar silenciosamente el alcance original.

### Descubribilidad de funciones

La primera interfaz era funcional pero exigía conocer rutas independientes. El cambio de rediseño convirtió la página inicial en un dashboard contextual y conectó los módulos mediante enlaces y acciones visibles.

## 7. Resultados de verificación

| Verificación | Resultado |
|---|---|
| Suite automatizada | 218 pruebas aprobadas |
| Cobertura global | 96,79 % |
| Umbral requerido | 80 % |
| Comprobación de Django | Sin problemas |
| Migraciones pendientes | Ninguna |
| Pruebas funcionales | Aprobadas |
| Pruebas de seguridad y permisos | Aprobadas |
| Pruebas de concurrencia | Aprobadas |
| Contratos responsivos | Aprobados |
| Validación estricta del cambio de interfaz | Aprobada |

Las pruebas abarcan modelos, formularios, servicios, autenticación, permisos, espacios, horarios, solicitudes, disponibilidad, decisiones, cancelaciones, historial, concurrencia, dashboard, navegación e interfaz adaptable.

## 8. Trazabilidad

La trazabilidad documental se mantiene mediante la relación:

`Plan de ingeniería → requisito → especificación OpenSpec → tarea → prueba automatizada`

Los identificadores funcionales definidos en el plan fueron conservados en las especificaciones principales. Los archivos de cambio contienen propuestas, diseños, especificaciones delta y listas de tareas. Las pruebas se organizan por módulo y por tipo de riesgo.

El repositorio Git fue inicializado al cierre para publicar la entrega final. Por ello, aunque existe trazabilidad documental detallada en OpenSpec, el único commit local reúne la versión final y no reconstruye la secuencia cronológica original plan → especificaciones → implementación. Esta limitación debe informarse al evaluador; crear commits retrospectivos separados produciría una evidencia artificial y no representaría el proceso real.

## 9. Pendientes antes de la entrega

- Archivar el cambio `redisenar-interfaz-navegacion-dashboard` cuando se apruebe formalmente su cierre.
- Si existe un repositorio Git anterior, recuperar su historial para evidenciar la secuencia SDD; el commit final actual no puede reconstruirla.
- Realizar una última revisión manual del repositorio para evitar incluir archivos temporales, credenciales o elementos ajenos a la entrega.

## 10. Conclusiones

El enfoque SDD permitió convertir reglas sensibles —especialmente permisos, transiciones y concurrencia— en escenarios verificables antes de tratarlas como trabajo terminado. También facilitó gestionar una regla institucional posterior sin reescribir informalmente la especificación original.

La solución obtenida satisface el alcance funcional y técnico planteado: centraliza reservas, evita conflictos, conserva trazabilidad y presenta flujos diferenciados según el rol. La combinación de OpenSpec, pruebas automatizadas y controles de PostgreSQL redujo el riesgo de inconsistencias entre requisitos e implementación.

La principal deuda de cierre no es funcional sino histórica: si existe, debe recuperarse el historial Git que demuestre el orden real del proceso. El código, las pruebas, la documentación y los artefactos OpenSpec están preparados para su entrega académica.
