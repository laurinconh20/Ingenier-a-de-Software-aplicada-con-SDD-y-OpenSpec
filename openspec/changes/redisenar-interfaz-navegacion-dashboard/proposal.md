# Proposal

## Why

La interfaz actual expone únicamente una cabecera mínima y una página de inicio estática, por lo que los usuarios no pueden descubrir ni recorrer los módulos según su rol sin conocer direcciones manuales. El sistema necesita una experiencia institucional, clara, dinámica y adaptable que haga visibles las acciones disponibles sin alterar la arquitectura Django definida.

## What Changes

- Incorporar una estructura visual común con identidad institucional, navegación persistente, estado activo, perfil visible y cierre de sesión.
- Añadir navegación basada en permisos para que cada actor encuentre desde la interfaz todos los módulos y acciones que puede utilizar, sin mostrar accesos no autorizados.
- Convertir la página posterior al inicio de sesión en un dashboard con indicadores, estados recientes y accesos rápidos ajustados al rol.
- Rediseñar login, listados, detalles, formularios, filtros, decisiones, historial y estados vacíos con componentes visuales consistentes.
- Añadir interacciones progresivas con JavaScript ligero para menú móvil, confirmaciones y retroalimentación, manteniendo formularios y navegación funcionales sin JavaScript.
- Mejorar accesibilidad, jerarquía visual, mensajes, indicadores de estado, foco de teclado y adaptación entre 320 y 1280 píxeles CSS.
- Mantener Django Templates y Bootstrap 5.3; no introducir una SPA ni sustituir las reglas de permisos del servidor.

## Capabilities

### New Capabilities

- `role-aware-dashboard-navigation`: Define el dashboard autenticado, la navegación descubrible y los accesos visibles según permisos y rol.

### Modified Capabilities

- `responsive-web-interface`: Amplía la operabilidad adaptable con estructura visual consistente, navegación móvil, retroalimentación y mejora progresiva.

## Impact

El cambio afecta `templates/`, `static/css/app.css`, nuevos recursos JavaScript locales, la vista de inicio y pruebas funcionales/de interfaz. Puede requerir consultas agregadas para indicadores del dashboard, siempre limitadas al alcance autorizado. No cambia modelos, migraciones, API pública, reglas de reserva, persistencia ni control de acceso del servidor.
