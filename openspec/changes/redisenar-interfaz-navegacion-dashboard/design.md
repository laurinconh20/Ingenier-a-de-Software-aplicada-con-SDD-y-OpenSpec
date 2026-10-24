# Design

## Context

La aplicación ya implementa los módulos de usuarios, espacios y reservas mediante vistas y plantillas renderizadas por Django. Sin embargo, `base.html` únicamente presenta la marca y las acciones de autenticación, mientras que la página inicial autenticada no orienta al usuario ni expone los flujos permitidos. Como resultado, varias funciones existentes sólo son descubribles si se conoce su URL.

El diseño debe respetar `PLAN_INGENIERIA.md`: arquitectura monolítica modular, Django 5.2, Django Templates, Bootstrap 5.3, autorización en el servidor y mejora progresiva. No se introducirá una SPA, un nuevo framework frontend, cambios en el modelo de datos ni modificaciones a las reglas de reservas.

## Goals / Non-Goals

### Goals

- Proporcionar una estructura visual institucional, coherente y reutilizable para todas las páginas.
- Hacer visibles los módulos y acciones disponibles según los permisos del usuario.
- Convertir la página inicial en un tablero contextual con información útil y correctamente acotada por rol.
- Permitir que los flujos principales se recorran mediante enlaces y botones, sin escribir URLs manualmente.
- Mantener accesibilidad básica, adaptación a pantallas móviles y funcionamiento esencial sin JavaScript.
- Conservar la autorización de las vistas del servidor como control de seguridad definitivo.

### Non-Goals

- Crear una SPA o reemplazar Django Templates y Bootstrap.
- Rediseñar la API, la persistencia, los modelos o las reglas de negocio de reservas.
- Agregar nuevos roles, permisos o estados de reserva.
- Incorporar dependencias frontend adicionales o servicios externos.
- Cambiar el alcance funcional aprobado en las especificaciones archivadas.

## Decisions

### 1. Estructura global renderizada en el servidor

`base.html` será la estructura común de la aplicación y delegará elementos repetidos en componentes de plantilla: navegación principal, barra superior, mensajes, indicadores de estado y encabezados de página. La navegación marcará la sección activa y mostrará únicamente las opciones para las que el usuario tenga permiso mediante los permisos de Django disponibles en el contexto de plantilla.

Ocultar una opción no sustituye la autorización. Todas las vistas conservarán sus comprobaciones de permisos y las pruebas verificarán también el rechazo del acceso directo no autorizado.

Se descarta mantener enlaces distintos en cada página porque duplicaría reglas de presentación y facilitaría inconsistencias. También se descarta una SPA porque contradice el stack y la arquitectura establecidos.

### 2. Tablero contextual y consultas acotadas

La ruta inicial dejará de ser una plantilla estática y utilizará una vista de tablero autenticada. Su contexto dependerá de los permisos efectivos:

- Solicitante: totales y actividad reciente exclusivamente de sus propias solicitudes o reservas.
- Gestor: solicitudes pendientes y actividad que esté autorizado a gestionar.
- Administrador: totales de usuarios, espacios y reservas, junto con accesos administrativos.
- Usuario anónimo: pantalla orientada al inicio de sesión, sin métricas ni datos protegidos.

Las métricas se obtendrán mediante agregaciones de Django ORM y las listas recientes estarán limitadas. Las relaciones necesarias se cargarán con `select_related` o mecanismos equivalentes para evitar consultas repetidas. Las consultas reutilizarán los mismos criterios de alcance que las vistas funcionales y tendrán pruebas contra filtración de datos entre usuarios.

### 3. Sistema visual sobre Bootstrap 5.3

Se conservará Bootstrap como base de rejilla, formularios y utilidades. `app.css` definirá variables visuales propias para una paleta institucional sobria, jerarquía tipográfica, espaciado, superficies, estados, foco y navegación. Las páginas usarán patrones consistentes para encabezados, acciones, tarjetas de resumen, filtros, tablas adaptables, formularios y estados vacíos.

Los estados de las reservas se comunicarán con texto y un distintivo visual; el color no será el único medio. Los iconos, si se requieren, serán SVG locales o recursos ya disponibles para no añadir dependencias remotas nuevas.

### 4. JavaScript local y mejora progresiva

Un archivo JavaScript local y pequeño controlará únicamente comportamientos de interfaz: apertura y cierre de navegación móvil, actualización de atributos ARIA, cierre con Escape o clic exterior, confirmaciones declarativas y prevención visual de dobles envíos.

Los enlaces, formularios y operaciones principales continuarán funcionando sin JavaScript. No se usará JavaScript para decidir permisos ni validar reglas de negocio; esas responsabilidades permanecen en Django.

### 5. Rediseño incremental de las páginas existentes

Las plantillas de autenticación, espacios, reservas y usuarios adoptarán la estructura común sin alterar sus URLs ni contratos funcionales. Cada módulo incluirá rutas visibles de entrada, acciones contextuales según permisos, retorno claro al listado o detalle, mensajes de resultado y estados vacíos útiles. Las operaciones destructivas o irreversibles solicitarán confirmación explícita, conservando el envío normal del formulario como mecanismo efectivo.

### 6. Estrategia de verificación

Las pruebas con el cliente de Django comprobarán el contenido del tablero, el alcance de sus consultas, la visibilidad de navegación por permisos y el rechazo del acceso directo. Las pruebas de contrato HTML/CSS comprobarán puntos de quiebre, ausencia de desbordamiento horizontal de página, atributos accesibles y funcionamiento progresivo. Los flujos de extremo a extremo existentes se ampliarán para recorrer las funciones mediante enlaces visibles.

La revisión visual se realizará al menos a 320 px y 1280 px, incluyendo navegación, formularios, tablas, estados vacíos y mensajes de error.

## Risks / Trade-offs

- **Divergencia entre navegación y permisos del servidor:** se mitiga centralizando la navegación y verificando por prueba tanto visibilidad como autorización directa.
- **Filtración de información en el tablero:** se mitiga construyendo consultas explícitamente acotadas por usuario o permiso y creando casos con datos de otros usuarios.
- **Costo de las métricas del tablero:** se mitiga con agregaciones, listas limitadas y carga anticipada de relaciones; no se calcularán informes históricos completos en cada solicitud.
- **Dependencia accidental de JavaScript:** se mitiga usando HTML funcional como base y reservando JavaScript para mejoras de interacción.
- **Regresiones por el alcance transversal del rediseño:** se mitiga migrando por módulo y ejecutando las pruebas existentes después de cada grupo de plantillas.
- **Mayor densidad visual para usuarios con varios roles:** se priorizarán acciones frecuentes y se agruparán las administrativas sin ocultar capacidades autorizadas.

## Migration Plan

1. Incorporar primero pruebas de navegación, alcance de datos y contratos responsivos.
2. Crear la estructura global, los componentes reutilizables y los recursos estáticos.
3. Implementar la vista y la plantilla del tablero contextual.
4. Migrar las plantillas por módulo: autenticación, espacios, reservas y usuarios.
5. Ejecutar la suite completa, la validación de Django y la revisión visual en los anchos definidos.

El cambio no requiere migración de datos. Si fuera necesario revertirlo, se restauran las plantillas, recursos estáticos y la vista inicial anteriores; los módulos y datos existentes permanecen intactos.

## Open Questions

- La identidad gráfica definitiva de la institución (logotipo, colores oficiales y tipografía corporativa) no está definida en el plan. Se utilizará un tema institucional neutral y configurable mediante variables CSS hasta recibir esos recursos.
