# Tasks

## 1. Estructura global y navegación

- [x] 1.1 Crear pruebas de interfaz para la navegación visible de solicitante, gestor y administrador, la sección activa y la ausencia de opciones no autorizadas (UI-01.1); verificar que las pruebas fallen antes del cambio y que el acceso directo siga cubierto por pruebas de permisos.
- [x] 1.2 Refactorizar la plantilla base y crear componentes reutilizables de navegación, barra superior, mensajes y estado de reserva (UI-01.1, RNF-01.2); verificar con las pruebas de interfaz y renderizado de páginas autenticadas.
- [x] 1.3 Incorporar el tema visual institucional configurable en `app.css`, incluyendo jerarquía, espaciado, foco visible, estados y contenedores de tablas (RNF-01.1, RNF-01.2); verificar los contratos CSS/HTML y revisar que no exista desbordamiento de página a 320 y 1280 px.
- [x] 1.4 Añadir JavaScript local de mejora progresiva para navegación móvil, atributos ARIA, cierre con Escape o clic exterior, confirmaciones y estado de envío (RNF-01.1, RNF-01.2); verificar mediante pruebas del marcado que los controles tengan semántica accesible y que enlaces y formularios sigan operando sin JavaScript.
- [x] 1.5 Rediseñar la pantalla de autenticación y la presentación anónima con la estructura pública, sin datos protegidos (UI-01.2, RNF-01.2); verificar inicio de sesión correcto, errores visibles y acceso anónimo sin métricas.

## 2. Dashboard contextual

- [x] 2.1 Crear pruebas para el contexto del dashboard de solicitante, gestor y administrador, incluyendo datos de terceros, ausencia de registros y usuario anónimo (UI-01.2); verificar alcance, totales, actividad reciente y ausencia de filtraciones antes de implementar la vista.
- [x] 2.2 Sustituir la página inicial estática por una vista de dashboard con agregaciones acotadas, relaciones precargadas y listas limitadas (UI-01.2); verificar las pruebas de contexto y que cada rol sólo reciba datos permitidos.
- [x] 2.3 Construir el dashboard con saludo, indicadores enlazados, actividad reciente, acciones rápidas y estados vacíos por rol (UI-01.2, UI-01.3); verificar mediante el cliente Django que cada indicador y acción resuelva a una ruta autorizada.
- [x] 2.4 Añadir una comprobación de cantidad acotada de consultas para los escenarios representativos del dashboard (UI-01.2); verificar que el número de consultas no crezca con la cantidad de elementos mostrados.

## 3. Flujos de espacios y reservas

- [x] 3.1 Rediseñar catálogo, detalle, formularios y administración de disponibilidad de espacios con encabezados, acciones contextuales, estados vacíos y rutas de retorno (UI-01.3, RNF-01.2); verificar los recorridos y permisos existentes del módulo de espacios.
- [x] 3.2 Rediseñar listado propio, creación, consulta de disponibilidad y detalle de solicitudes con estados textuales, filtros y acciones enlazadas (UI-01.3, RNF-01.2); verificar el recorrido completo del solicitante y los casos de validación fallida.
- [x] 3.3 Rediseñar las pantallas de decisión, cancelación e historial con acciones claras, confirmación y retroalimentación (UI-01.3, RNF-01.2); verificar aprobación, rechazo, cancelación, retorno al listado y rechazo de acciones sin permiso.
- [x] 3.4 Extender las pruebas responsivas de espacios y reservas para tablas extensas, formularios, mensajes y navegación móvil (RNF-01.1); verificar operabilidad a 320 y 1280 px y desplazamiento limitado al contenedor de tabla.

## 4. Flujos de usuarios y consistencia transversal

- [x] 4.1 Rediseñar listado, formulario y perfil de usuarios con navegación, acciones según permiso, errores asociados a campos y rutas de retorno (UI-01.1, UI-01.3, RNF-01.2); verificar los recorridos administrativos y el acceso denegado para usuarios sin permiso.
- [x] 4.2 Aplicar en todas las plantillas los componentes comunes de títulos, mensajes, distintivos, formularios y estados vacíos (RNF-01.2); verificar mediante una prueba de inventario que todas las plantillas funcionales extiendan la estructura correspondiente y conserven sus acciones.
- [x] 4.3 Añadir pruebas de confirmación y retroalimentación para cancelaciones y eliminaciones, incluido el comportamiento base sin JavaScript (RNF-01.2); verificar que cancelar la confirmación no cambie datos y que continuar use el formulario protegido por el servidor.

## 5. Integración y validación final

- [x] 5.1 Ampliar las pruebas de extremo a extremo para recorrer desde el dashboard los flujos de solicitante, gestor y administrador sin escribir URLs manualmente (UI-01.1, UI-01.2, UI-01.3); verificar que los tres recorridos finalicen por navegación interna.
- [x] 5.2 Ejecutar la suite completa y las comprobaciones de Django, verificando que no existan regresiones, migraciones pendientes ni cobertura inferior al umbral definido en el plan.
- [x] 5.3 Realizar la revisión visual final a 320 y 1280 px sobre autenticación, dashboard, espacios, reservas y usuarios; registrar y corregir cualquier control oculto, desbordamiento, foco inaccesible o inconsistencia con RNF-01.1 y RNF-01.2.
- [x] 5.4 Ejecutar `openspec validate redisenar-interfaz-navegacion-dashboard --strict` y verificar que todos los artefactos y escenarios permanezcan válidos antes de solicitar aprobación para archivar.
