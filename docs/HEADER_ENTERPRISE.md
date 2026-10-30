# ISO Smart MedSupplier Enterprise Header

## Alcance

El header enterprise activo está integrado en `frontend/src/features/medsupplier/components/MedSupplierShell.jsx`.

## Capacidades

- Identidad del producto y tenant activo.
- Tema claro, oscuro y sistema mediante `ThemeContext`.
- Persistencia de tema en `localStorage` con `isosmart-theme`.
- Controles A-, A+ y reset mediante `FontSizeContext`.
- Persistencia de tamaño de fuente en `localStorage` con `isosmart_font_size`.
- Selector de idioma español, inglés y portugués.
- Notificaciones conectadas a `settingsService.getNotificationHistory`.
- Panel vacío profesional cuando no hay historial real.
- Menú de configuración con preferencias visuales, accesibilidad, idioma y enlaces reales a `/settings` y `/profile`.
- Menú de usuario existente sin reemplazar autenticación, logout ni cambio de organización.

## Accesibilidad

- Botones con `aria-label`.
- Menús con `aria-haspopup`, `aria-expanded` y `aria-controls`.
- Cierre por Escape.
- Cierre por click fuera.
- Estados focus visibles con `focus:ring`.
- Header responsive; controles densos se agrupan en settings en mobile.

## Producción controlada

La funcionalidad no inventa backend de notificaciones. Si el endpoint devuelve historial real, se muestra; si no hay eventos, se muestra estado vacío. La ruta `/settings` conserva las protecciones RBAC existentes del producto.

## QA manual

1. Cambiar tema desde el botón del header.
2. Abrir settings y seleccionar claro, oscuro y sistema.
3. Recargar y validar persistencia.
4. Cambiar tamaño con A-, A+ y reset.
5. Recargar y validar persistencia.
6. Cambiar idioma a inglés y portugués.
7. Abrir y cerrar notificaciones con click fuera y Escape.
8. Abrir y cerrar settings con click fuera y Escape.
9. Abrir menú de usuario, perfil y logout.
10. Probar desktop, tablet y mobile.

## QA automatizado

- `npm run test:e2e:medsupplier:header`: valida tema, tamaño de fuente, idioma, persistencia, notificaciones vacías, menú de settings, menú de usuario, enlaces de perfil/logout, cierre por Escape/click fuera y navegación/preferencias en viewport mobile.
- `npm run test:i18n:smoke`: valida runtime ES/EN/PT en login y shell MedSupplier.
- `npm run test:e2e:medsupplier`: valida workspace, permisos, scoping y campos privados de MedSupplier.

Evidencia de validación: `docs/release/HEADER_ENTERPRISE_VALIDATION_EVIDENCE.md`.
