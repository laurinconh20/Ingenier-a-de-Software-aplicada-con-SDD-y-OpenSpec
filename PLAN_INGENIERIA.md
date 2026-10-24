# PLAN DE INGENIERÍA
---

## 1. Análisis del problema

### 1.1. Identificación de la problemática

Actualmente, la institución universitaria administra las reservas de laboratorios, auditorios y salas de cómputo mediante correos electrónicos y hojas de cálculo.

Este procedimiento presenta diferentes dificultades:

- Duplicidad de solicitudes para un mismo espacio.
- Conflictos de horarios por falta de validaciones automáticas.
- Dificultad para consultar la disponibilidad de los espacios.
- Ausencia de un mecanismo centralizado de aprobación.
- Limitaciones para consultar el historial de reservas.
- Dependencia de procedimientos manuales.
- Falta de trazabilidad sobre las decisiones de aprobación, rechazo y cancelación.

Estas dificultades afectan la organización académica y administrativa, incrementan el riesgo de errores y dificultan el aprovechamiento adecuado de los recursos institucionales.

### 1.2. Necesidades de la institución

La institución necesita una aplicación web centralizada que permita:

1. Registrar y administrar espacios académicos.
2. Gestionar usuarios y asignarles permisos.
3. Consultar la disponibilidad de los espacios.
4. Crear solicitudes de reserva.
5. Detectar conflictos entre horarios.
6. Impedir reservas aprobadas que se superpongan.
7. Aprobar o rechazar solicitudes.
8. Cancelar reservas y conservar su historial.
9. Mantener la integridad de la información almacenada.
10. Facilitar el seguimiento y control del proceso de reservas.

### 1.3. Actores involucrados

 Actor - Responsabilidades 
 Estudiante - Consultar espacios, solicitar reservas y consultar o cancelar sus solicitudes. 
 Docente - Consultar disponibilidad, solicitar espacios y gestionar sus propias reservas. -
 Gestor de espacios - Revisar solicitudes, aprobarlas o rechazarlas y consultar el historial correspondiente. 
 Administrador - Gestionar usuarios, roles, espacios y configuración general del sistema. 

Para simplificar la implementación, estudiantes y docentes compartirán el rol funcional de **Solicitante**, mientras que los demás actores tendrán permisos específicos.

### 1.4. Alcance del sistema

El proyecto comprende el desarrollo de una aplicación web funcional, orientada a un entorno universitario, con los siguientes módulos:

- Gestión de usuarios.
- Autenticación y autorización.
- Administración de espacios académicos.
- Gestión de solicitudes de reserva.
- Validación de disponibilidad.
- Aprobación y rechazo.
- Cancelación e historial.
- Registro de eventos relevantes.

El sistema contará con una interfaz web adaptable a todo tipo de dispositivos.

### 1.5. Limitaciones

La primera versión se enfocará en las funcionalidades esenciales del proceso de reservas.

No se contempla inicialmente:

- Aplicaciones móviles nativas.
- Integración con plataformas institucionales externas.
- Notificaciones por SMS o WhatsApp.
- Sistemas de pago.
- Reservas periódicas o recurrentes.
- Integración con calendarios externos.
- Análisis predictivo de ocupación.
- Gestión de múltiples instituciones independientes.
- Despliegue productivo de alta disponibilidad.

El despliegue inicial será local o en un entorno de demostración. Se documentarán las condiciones necesarias para ejecutarlo.

### 1.6. Supuestos iniciales

Se establecen los siguientes supuestos, sujetos a revisión antes de generar las especificaciones:

- Los usuarios serán registrados y administrados por personal autorizado.
- Cada reserva corresponde a un único espacio académico.
- Las solicitudes requieren aprobación para convertirse en reservas confirmadas.
- Las solicitudes pendientes no bloquean definitivamente la disponibilidad.
- Dos reservas aprobadas no pueden coincidir en un mismo espacio durante horarios superpuestos.
- Un mismo usuario tampoco podrá mantener dos reservas aprobadas superpuestas.
- Las reservas deberán comenzar en el futuro, finalizar después de su inicio y respetar los horarios habilitados del espacio.
- Los espacios tendrán horarios de funcionamiento configurables.
- La primera versión gestionará reservas dentro de un mismo día calendario.
- La zona horaria institucional será configurable; inicialmente se utilizará `America/Bogota`.

Los supuestos deberán convertirse en decisiones explícitas durante la revisión de especificaciones. Cualquier modificación deberá documentarse y justificarse.

---

## 2. Propuesta de solución

### 2.1. Descripción general

Se propone desarrollar una aplicación web denominada **Sistema de Gestión de Reservas Académicas**, diseñada para centralizar la administración de espacios y solicitudes de reserva.

Los usuarios autenticados podrán consultar los espacios disponibles, seleccionar fechas y horarios y registrar solicitudes.

Los gestores autorizados podrán revisar las solicitudes pendientes y aprobarlas o rechazarlas.

El sistema realizará validaciones automáticas para impedir conflictos entre reservas aprobadas y mantendrá un historial de las operaciones relevantes.

La solución será modular, permitiendo desarrollar, probar y mantener cada componente de forma progresiva.

### 2.2. Funcionalidades prioritarias

 ID - Funcionalidad - Prioridad 

 RF-01 - Registrar, modificar, desactivar y consultar espacios académicos. - Alta 
 RF-02 - Registrar, autenticar y administrar usuarios. - Alta 
 RF-03 - Controlar roles y permisos de acceso. - Alta 
 RF-04 - Crear y consultar solicitudes de reserva. - Alta 
 RF-05 - Verificar disponibilidad por espacio, fecha y horario. - Alta 
 RF-06 - Prevenir reservas aprobadas superpuestas, incluso ante operaciones concurrentes. - crítica 
 RF-07 - Aprobar y rechazar solicitudes según permisos. - Alta 
 RF-08 - Cancelar solicitudes o reservas cuando las reglas lo permitan. - Alta 
 RF-09 - Consultar historial de reservas y sus estados. - Media 
 RF-10 - Registrar los eventos relevantes de aprobación, rechazo y cancelación. - Media 

Estos identificadores se conservarán como referencia durante el proceso SDD.

### 2.3. Organización del sistema en módulos

**Módulo de usuarios:** administrará cuentas, autenticación y datos básicos de los usuarios.

**Módulo de roles y permisos:** controlará el acceso a funcionalidades y operaciones según el perfil autorizado.

**Módulo de espacios:** permitirá registrar y administrar laboratorios, auditorios y salas de cómputo, incluyendo nombre, ubicación, capacidad, características, estado y horarios de funcionamiento.

**Módulo de reservas:** gestionará solicitudes, fechas, horarios, estados y reglas de validación.

**Módulo de aprobaciones:** permitirá que los gestores revisen solicitudes y registren las decisiones correspondientes.

**Módulo de historial y auditoría:** conservará información sobre las reservas y las operaciones administrativas relevantes.

### 2.4. Reglas generales de funcionamiento

Para la primera versión se proponen las siguientes reglas:

- Una solicitud tendrá fecha y hora de inicio y finalización.
- La fecha y hora de finalización deberán ser posteriores al inicio.
- No podrán solicitarse espacios inactivos.
- Las solicitudes deberán estar dentro del horario habilitado del espacio.
- Una reserva aprobada bloqueará su intervalo para nuevas aprobaciones.
- Dos solicitudes pendientes podrán coincidir, pero solamente una podrá aprobarse si sus intervalos se superponen.
- La disponibilidad deberá verificarse nuevamente en el momento de aprobar.
- Los intervalos se interpretarán como `[inicio, fin)`, permitiendo que una reserva comience exactamente cuando termina otra.
- Las reservas tendrán los estados `PENDIENTE`, `APROBADA`, `RECHAZADA` y `CANCELADA`.
- Solamente las solicitudes pendientes podrán aprobarse o rechazarse.
- El solicitante podrá cancelar sus solicitudes pendientes o reservas aprobadas antes del inicio. Los gestores y administradores podrán realizar cancelaciones autorizadas.
- Las reservas canceladas y rechazadas permanecerán registradas en el historial.

No se establece un límite máximo general de duración durante esta primera versión. Las nuevas restricciones institucionales se gestionarán posteriormente mediante solicitudes formales de cambio.

### 2.5. Desarrollo progresivo

El desarrollo seguirá una estrategia incremental.

Primero se implementará la estructura de usuarios y espacios. Posteriormente se incorporarán las solicitudes, la validación de horarios, las aprobaciones y el historial.

Cada incremento contará con especificaciones revisadas y pruebas automatizadas antes de considerarse terminado.

Esta estrategia permitirá detectar errores tempranamente y reducir el riesgo de desarrollar numerosos componentes sin verificar su funcionamiento.

---

## 3. Decisiones de arquitectura y tecnología

### 3.1. Arquitectura seleccionada

Se utilizará una **arquitectura monolítica modular con separación de responsabilidades**.

La aplicación estará organizada en una capa de presentación, una capa de lógica de negocio y una capa de persistencia de datos.

**Capa de presentación**

Gestionará las páginas web, formularios, navegación y mensajes mostrados al usuario.

**Capa de lógica de negocio**

Aplicará las reglas de disponibilidad, autorizaciones, validación de reservas y cambios de estado.

**Capa de persistencia**

Se encargará de almacenar y consultar usuarios, espacios, reservas y eventos utilizando una base de datos relacional.

El sistema se desplegará como una única aplicación, pero mantendrá módulos internos independientes.

Esta arquitectura se selecciona por su menor complejidad operativa y porque facilita la comprensión, implementación y prueba de un proyecto universitario.

### 3.2. Stack tecnológico

| Componente | Tecnología | Justificación |
|---|---|---|
| Lenguaje | Python 3.13 | Lenguaje legible, con herramientas consolidadas para desarrollo y pruebas. |
| Framework | Django 5.2 LTS | Incluye ORM, autenticación, formularios, migraciones y mecanismos de seguridad. |
| Frontend | Django Templates | Permite desarrollar la interfaz sin una aplicación frontend independiente. |
| Estilos | Bootstrap 5.3 | Facilita la construcción de interfaces adaptables. |
| Base de datos | PostgreSQL 17 | Proporciona integridad transaccional y mecanismos para controlar superposiciones. |
| Pruebas | pytest, pytest-django y pytest-cov | Permiten pruebas automatizadas y medición de cobertura. |
| Versionamiento | Git y GitHub | Facilitan trazabilidad y conservación del historial de desarrollo. |
| Especificaciones | OpenSpec | Organiza propuestas, especificaciones y cambios siguiendo SDD. |
| Asistente IA | Codex | Apoya la implementación y revisión técnica siguiendo especificaciones aprobadas. |

Se fijarán las versiones compatibles y las dependencias del entorno al comenzar la etapa de implementación.

### 3.3. Estrategia de persistencia

Se utilizará una base de datos relacional PostgreSQL.

Las entidades principales previstas son:

| Entidad | Información principal |
|---|---|
| Usuario | Identificador, nombre, correo, credenciales y estado. |
| Rol | Nombre del rol y permisos correspondientes. |
| Espacio | Nombre, tipo, ubicación, capacidad, características y estado. |
| HorarioEspacio | Espacio, día habilitado y horario de funcionamiento. |
| Reserva | Solicitante, espacio, inicio, fin, estado y fecha de creación. |
| EventoReserva | Reserva, responsable, acción, fecha y observaciones. |

Se utilizará el sistema de autenticación de Django y sus mecanismos de grupos y permisos, evitando desarrollar desde cero funciones de seguridad que el framework ya proporciona.

Las relaciones entre entidades estarán protegidas mediante claves foráneas y restricciones de integridad.

### 3.4. Prevención de conflictos y concurrencia

Uno de los riesgos más importantes consiste en que dos usuarios intenten obtener el mismo espacio para horarios superpuestos.

Una validación realizada únicamente en la interfaz o mediante una consulta previa no garantiza que esto se evite, porque dos solicitudes pueden procesarse al mismo tiempo.

Por ello se aplicarán tres medidas:

1. Validaciones de disponibilidad en la lógica de negocio.
2. Transacciones atómicas y bloqueo de la fila del espacio durante el proceso de aprobación.
3. Una restricción de exclusión en PostgreSQL que impida intervalos superpuestos para reservas aprobadas del mismo espacio.

Para esta última medida se evaluará la utilización de `ExclusionConstraint`, índices GiST y la extensión `btree_gist`.

De esta forma, incluso si ocurre una condición de carrera, la base de datos impedirá guardar dos reservas aprobadas incompatibles.

Los conflictos detectados deberán producir un resultado controlado y comprensible, sin mostrar errores técnicos internos al usuario.

### 3.5. Organización prevista del código

Se propone la siguiente estructura lógica, que se creará únicamente durante la implementación:

```text
reservas-academicas/
├── PLAN_INGENIERIA.md
├── README.md
├── INFORME_FINAL.md
├── openspec/
├── .agents/
├── config/
├── apps/
│   ├── usuarios/
│   ├── espacios/
│   ├── reservas/
│   └── auditoria/
├── templates/
├── static/
├── tests/
├── manage.py
└── requirements.txt
```

La estructura exacta podrá ajustarse a las convenciones de Django, conservando las responsabilidades y documentando cualquier decisión diferente.

### 3.6. Comparación de decisiones técnicas

**Decisión 1. Arquitectura monolítica modular frente a microservicios**

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Monolito modular | Desarrollo más sencillo, menor costo de despliegue y pruebas integradas. | Menor independencia de despliegue entre módulos. |
| Microservicios | Escalabilidad y despliegue independiente de servicios. | Mayor complejidad de comunicación, infraestructura y consistencia. |

**Elección:** arquitectura monolítica modular.

**Justificación:** el tamaño del proyecto y su finalidad académica no requieren la infraestructura y complejidad de los microservicios.

**Decisión 2. Django frente a FastAPI y Express**

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Django | Autenticación, ORM, formularios y panel administrativo integrados. | Menor flexibilidad para proyectos que buscan componentes mínimos. |
| FastAPI | Buen soporte de APIs y tipado moderno. | Requiere integrar por separado más componentes de administración y presentación. |
| Express | Flexible y ampliamente utilizado con JavaScript. | Requiere seleccionar e integrar varias herramientas adicionales. |

**Elección:** Django.

**Justificación:** permite dedicar más tiempo a las reglas de reservas y a las pruebas, reduciendo trabajo de infraestructura y autenticación.

**Decisión 3. PostgreSQL frente a SQLite y MySQL**

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| PostgreSQL | Transacciones robustas y restricciones avanzadas sobre intervalos. | Requiere configurar un servidor de base de datos. |
| SQLite | Muy sencillo de utilizar localmente. | No ofrece las mismas capacidades nativas de exclusión de intervalos requeridas para este diseño. |
| MySQL | Sistema relacional ampliamente utilizado. | La solución propuesta de restricciones temporales requeriría un diseño diferente. |

**Elección:** PostgreSQL.

**Justificación:** permite reforzar la prevención de reservas superpuestas directamente en la base de datos y proporciona mecanismos adecuados para las pruebas de concurrencia.

**Decisión 4. Interfaz renderizada en servidor frente a SPA**

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Django Templates + Bootstrap | Menos dependencias y un único proyecto para frontend y backend. | Menor dinamismo en interacciones complejas. |
| React + API | Componentes reutilizables e interfaces altamente interactivas. | Requiere una aplicación frontend separada y mayor integración. |

**Elección:** Django Templates y Bootstrap.

**Justificación:** la aplicación se centra en formularios, consultas y flujos administrativos, por lo que no requiere inicialmente la complejidad de una SPA.

---

## 4. Estrategia de desarrollo

### 4.1. Metodología de trabajo

Se utilizará una metodología incremental basada en **Spec-Driven Development (SDD)**, combinada con prácticas de control de versiones y pruebas automatizadas.

Cada funcionalidad deberá seguir esta secuencia:

1. Identificación y análisis del requisito.
2. Elaboración de la especificación utilizando OpenSpec.
3. Revisión de consistencia y criterios de aceptación.
4. Definición de tareas técnicas.
5. Implementación asistida por Codex.
6. Revisión del código generado.
7. Ejecución de pruebas automatizadas.
8. Registro de cambios mediante Git.

No se permitirá implementar funcionalidades sin una especificación previamente revisada.

### 4.2. Etapas de implementación

| Etapa | Actividad | Criterio de finalización |
|---|---|---|
| 1 | Planificación de ingeniería | Plan completo, revisado y registrado en un commit independiente. |
| 2 | Especificaciones OpenSpec | Requisitos, escenarios, diseño y tareas revisados y validados. |
| 3 | Base del sistema | Proyecto configurado, conexión a PostgreSQL y autenticación funcional. |
| 4 | Usuarios y espacios | Gestión y consulta de usuarios y espacios con pruebas aprobadas. |
| 5 | Solicitudes y disponibilidad | Creación de solicitudes y validaciones de horarios implementadas. |
| 6 | Aprobaciones y concurrencia | Estados, decisiones y prevención de superposiciones probados. |
| 7 | Cancelaciones e historial | Cancelación, consultas y trazabilidad verificadas. |
| 8 | Gestión de cambios | Nueva solicitud documentada, especificada, implementada y probada. |
| 9 | Verificación y cierre | Pruebas completas, README e informe final consolidados. |

Los criterios anteriores son acumulativos: cada etapa requiere que las anteriores hayan cumplido sus condiciones.

### 4.3. Orden de desarrollo de funcionalidades

El orden previsto será:

1. Configuración del proyecto y persistencia.
2. Autenticación y roles.
3. Administración de espacios.
4. Consultas de disponibilidad.
5. Registro de solicitudes.
6. Validación de conflictos.
7. Aprobación y rechazo.
8. Cancelación e historial.
9. Pruebas integrales y estabilización.
10. Gestión de la nueva regla institucional.

Las pruebas de cada incremento se desarrollarán junto con sus funcionalidades, no solamente al finalizar el proyecto.

### 4.4. Dependencias entre componentes

El módulo de reservas dependerá de los módulos de usuarios y espacios, porque toda solicitud debe tener un solicitante y un espacio válido.

La validación de disponibilidad dependerá de los datos de espacios, horarios y reservas existentes.

El módulo de aprobaciones dependerá de las solicitudes y de la validación de disponibilidad.

El historial dependerá de los cambios de estado y de los eventos registrados durante las operaciones.

Estas dependencias justifican el orden de desarrollo seleccionado.

### 4.5. Criterios generales de finalización

Una funcionalidad se considerará terminada únicamente cuando:

- Exista una especificación revisada.
- El código corresponda al comportamiento especificado.
- Se hayan implementado los controles de acceso necesarios.
- Existan pruebas de sus escenarios principales y casos de error.
- Las pruebas automatizadas relacionadas finalicen correctamente.
- El código haya sido revisado por el estudiante.
- Las modificaciones se hayan registrado en Git.
- No existan defectos críticos conocidos asociados a la funcionalidad.

### 4.6. Estrategia de versionamiento

Git se utilizará como mecanismo de seguimiento del trabajo.

Se realizarán commits independientes para documentar los hitos principales:

- Planificación inicial.
- Especificaciones revisadas.
- Configuración e implementación de módulos.
- Pruebas automatizadas.
- Especificación del cambio institucional.
- Implementación del cambio.
- Documentación final.

Se utilizarán mensajes descriptivos como `docs:`, `feat:`, `fix:` y `test:`.

GitHub conservará el historial y permitirá demostrar que las decisiones y especificaciones antecedieron a los cambios funcionales.

---

## 5. Estrategia de calidad

### 5.1. Tipos de pruebas

**Pruebas unitarias**

Verificarán funciones y reglas individuales, por ejemplo:

- Validación de horarios.
- Comprobación de estados.
- Reglas de cancelación.
- Validaciones de permisos.

**Pruebas de integración**

Evaluarán la interacción entre componentes y la base de datos, especialmente:

- Registro de solicitudes.
- Actualización de estados.
- Disponibilidad de espacios.
- Restricciones de superposición.
- Transacciones concurrentes.

**Pruebas funcionales**

Comprobarán los flujos principales desde la perspectiva de los usuarios:

- Inicio de sesión.
- Consulta de espacios.
- Solicitud de reserva.
- Aprobación y rechazo.
- Cancelación y consulta de historial.

**Pruebas de seguridad**

Verificarán que un usuario no pueda acceder a operaciones ni datos para los que carece de autorización.

**Pruebas de regresión**

Se ejecutarán después de cada modificación relevante para confirmar que las funcionalidades anteriores continúan funcionando.

**Pruebas de concurrencia**

Ejecutarán operaciones que intenten aprobar simultáneamente reservas incompatibles.

Las pruebas de restricciones y concurrencia se realizarán sobre PostgreSQL, no sobre una base de datos alternativa que no reproduzca las mismas garantías.

### 5.2. Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| R-01: Reservas aprobadas superpuestas | Media | Alto | Validación de disponibilidad, transacciones y restricción en PostgreSQL. |
| R-02: Acceso no autorizado | Media | Alto | Autenticación, permisos y pruebas de autorización. |
| R-03: Pérdida o inconsistencia de información | Media | Alto | Restricciones de integridad, migraciones y transacciones. |
| R-04: Interpretación incorrecta de requisitos por la IA | Alta | Alto | Especificaciones verificables y revisión humana del código. |
| R-05: Retrasos por complejidad técnica | Media | Medio | Arquitectura sencilla y desarrollo incremental. |
| R-06: Especificaciones incompletas o contradictorias | Media | Alto | Revisión formal antes de implementar. |
| R-07: Errores por fechas y zonas horarias | Media | Medio | Uso de fechas con zona horaria y pruebas de límites. |
| R-08: Cambios que afectan funcionalidades anteriores | Alta | Alto | Gestión de cambios con OpenSpec y pruebas de regresión. |

### 5.3. Mecanismos de verificación

Se mantendrá una matriz de trazabilidad para relacionar requisitos, especificaciones, implementación y pruebas.

Como planificación inicial, se establecen los siguientes controles:

| Requisito | Verificación prevista |
|---|---|
| RF-01 | Pruebas de creación, edición, consulta y desactivación de espacios. |
| RF-02 | Pruebas de autenticación y administración de usuarios. |
| RF-03 | Pruebas de acceso autorizado y denegado. |
| RF-04 | Pruebas de solicitudes válidas e inválidas. |
| RF-05 | Pruebas de disponibilidad por intervalo. |
| RF-06 | Pruebas de superposición y aprobación concurrente. |
| RF-07 | Pruebas de aprobación, rechazo y transiciones de estado. |
| RF-08 | Pruebas de cancelación permitida y denegada. |
| RF-09 | Pruebas de consulta y conservación del historial. |
| RF-10 | Pruebas de registro de eventos relevantes. |

Durante OpenSpec se completará la matriz con las rutas reales de las especificaciones, módulos y archivos de prueba.

### 5.4. Criterios de calidad

Se establecen las siguientes metas:

- Todos los requisitos obligatorios deben contar con especificaciones verificables.
- El 100 % de las pruebas automatizadas obligatorias debe aprobarse antes de la entrega.
- Se buscará una cobertura mínima del 80 % en la lógica de negocio crítica.
- Ningún caso de prueba concurrente podrá producir dos reservas aprobadas incompatibles.
- Ningún usuario sin permisos podrá ejecutar operaciones administrativas.
- Las operaciones normales deberán responder en un tiempo razonable, que se medirá durante las pruebas de rendimiento en el entorno de demostración.
- Los resultados de las pruebas deberán documentarse y ser reproducibles.
- No deberán permanecer defectos críticos conocidos al finalizar.

La cobertura de código se utilizará como indicador complementario, sin sustituir la revisión de escenarios y reglas de negocio.

---

## 6. Uso de SDD e inteligencia artificial

### 6.1. Aplicación de Spec-Driven Development

El proyecto utilizará SDD como metodología para asegurar que las funcionalidades se desarrollen a partir de requisitos definidos y revisados.

La planificación servirá como base para tomar decisiones arquitectónicas y determinar el alcance.

Posteriormente, OpenSpec permitirá transformar esta planificación en especificaciones estructuradas.

El proceso seguirá el principio:

**Planificación → Especificación → Revisión → Implementación → Pruebas → Verificación.**

### 6.2. Uso de OpenSpec

Una vez finalizado y registrado este documento en Git, se inicializará OpenSpec en el repositorio.

Para cada cambio o conjunto coherente de funcionalidades se generarán los artefactos establecidos por el flujo de OpenSpec:

- `proposal.md`: motivación, alcance y propósito del cambio.
- `design.md`: decisiones y consideraciones de diseño.
- `specs/`: requisitos y escenarios verificables.
- `tasks.md`: actividades necesarias para implementar el cambio.

La organización específica de los archivos seguirá las convenciones de la versión instalada de OpenSpec.

Los requisitos funcionales RF-01 a RF-10 permitirán establecer una relación entre la planificación y las especificaciones.

### 6.3. Transformación del plan en especificaciones

Los módulos y requisitos identificados en este plan serán analizados individualmente.

Para cada requisito se definirán:

1. Descripción precisa del comportamiento esperado.
2. Actor responsable.
3. Condiciones previas.
4. Restricciones de negocio.
5. Resultados esperados.
6. Escenarios de aceptación positivos y negativos.
7. Casos límite.
8. Dependencias técnicas.
9. Tareas y pruebas asociadas.

Las especificaciones deberán revisarse antes de autorizar la implementación.

Las ambigüedades encontradas se documentarán y resolverán mediante decisiones explícitas.

### 6.4. Uso de Codex

Codex se utilizará como agente de asistencia para:

- Analizar especificaciones técnicas.
- Proponer soluciones de implementación.
- Crear módulos y componentes.
- Generar pruebas automatizadas.
- Identificar posibles errores.
- Sugerir refactorizaciones.
- Revisar código y documentación.

Todas estas actividades deberán respetar el plan de ingeniería y las especificaciones aprobadas.

No se utilizará Codex como sustituto de la toma de decisiones del estudiante.

### 6.5. Verificación del código generado por IA

El código generado será revisado mediante:

- Inspección de los archivos modificados.
- Comparación con las especificaciones.
- Verificación de arquitectura y dependencias.
- Ejecución de pruebas automatizadas.
- Pruebas manuales de los flujos principales.
- Revisión de permisos y validaciones.
- Comprobación del comportamiento ante errores.
- Inspección de los cambios antes de registrarlos en Git.

Si el código implementa comportamientos no solicitados o contradice las especificaciones, deberá corregirse antes de considerarse terminado.

### 6.6. Responsabilidades del estudiante

El estudiante será responsable de:

- Comprender y justificar las decisiones de ingeniería.
- Aprobar la arquitectura y las tecnologías.
- Revisar los requisitos.
- Resolver ambigüedades.
- Aprobar las especificaciones.
- Validar el código generado.
- Ejecutar y analizar las pruebas.
- Gestionar los cambios.
- Mantener la documentación.
- Sustentar técnicamente el sistema.

La inteligencia artificial será una herramienta de apoyo, no la responsable final del proyecto.

### 6.7. Gestión de cambios con OpenSpec

Después de implementar las funcionalidades principales, se incorporará una nueva solicitud institucional relacionada con la duración consecutiva de las reservas.

Esta modificación se gestionará como un cambio separado para demostrar la aplicación de SDD durante el mantenimiento del sistema.

El procedimiento será:

1. Registrar la solicitud de cambio.
2. Analizar su impacto en los requisitos y la arquitectura.
3. Determinar si es necesario actualizar este plan.
4. Crear o actualizar la propuesta y especificaciones utilizando OpenSpec.
5. Definir nuevos escenarios de aceptación.
6. Revisar y aprobar las modificaciones.
7. Implementar el cambio mediante Codex.
8. Crear o actualizar las pruebas automatizadas.
9. Ejecutar las pruebas de regresión.
10. Documentar los resultados y registrar los commits correspondientes.

La nueva regla no forma parte de los requisitos vigentes de la versión inicial y no deberá implementarse antes de su especificación formal.

### 6.8. Trazabilidad del proyecto

La trazabilidad se mantendrá mediante la siguiente relación:

**Plan de ingeniería → Requisito identificado → Especificación OpenSpec → Tarea → Código fuente → Prueba automatizada → Evidencia Git.**

Esta relación permitirá demostrar cómo cada funcionalidad fue planificada, especificada, desarrollada y verificada.

También permitirá identificar qué componentes y pruebas deben revisarse ante una nueva solicitud institucional.

---

## 7. Resultados esperados y conclusión

Se espera obtener una aplicación web capaz de centralizar la gestión de reservas de espacios académicos, reducir conflictos de horarios, controlar permisos y conservar un historial confiable de las solicitudes.

Desde la perspectiva de ingeniería de software, el principal resultado será demostrar que el sistema se construyó mediante un proceso organizado, en el que las decisiones técnicas, los requisitos, las especificaciones, la implementación y las pruebas mantienen correspondencia.

La arquitectura monolítica modular con Django y PostgreSQL permitirá desarrollar una solución viable para el contexto académico, manteniendo mecanismos adecuados de integridad de datos, seguridad y control de concurrencia.

El uso de OpenSpec facilitará la gestión formal de los requisitos y sus cambios, mientras que Codex apoyará la implementación bajo supervisión técnica del estudiante.

Finalmente, Git y GitHub permitirán demostrar cronológicamente las etapas de planificación, especificación, desarrollo, gestión de cambios y verificación.

Este documento constituye la planificación inicial y deberá aprobarse y registrarse mediante un commit independiente antes de comenzar la etapa de especificaciones.

---

## 8. Referencias técnicas

- Django Software Foundation. *Django 5.2 Release Notes*. https://docs.djangoproject.com/en/5.2/releases/5.2/
- Django Software Foundation. *PostgreSQL Specific Database Constraints*. https://docs.djangoproject.com/en/5.2/ref/contrib/postgres/constraints/
- PostgreSQL Global Development Group. *PostgreSQL Documentation*. https://www.postgresql.org/docs/
- OpenSpec. *Official Documentation*. https://openspec.dev/
- Git. *Git Documentation*. https://git-scm.com/doc/
