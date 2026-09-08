# Desempeño Frontend (Stack: Python + Django)

## Reglas generales
- Frontend siempre sobre **Django Templates**: `{% extends %}`, `{% block %}` y `{% static %}`.
- HTML semántico estilo HTML5 (header, nav, main, section, footer). Nada de `div`s cuando existe una etiqueta con significado.
- CSS y JS SOLO por archivos estáticos comprimidos/minificados. Prohibido CSS inline o `<script>` sueltos salvo excepción justificada.
- Todo texto visible (labels, placeholders, botones, mensajes) desde el template o el sistema de mensajes de Django; nunca hardcodeado raro en JS.

## Calidad tipo senior
- **Accesibilidad (WCAG):** alt en imágenes, `<label>` ligado a cada input, foco visible, contraste suficiente, `aria-*` solo cuando hace falta.
- **Responsive mobile-first:** grid flexible, media queries por breakpoints claros; uso de `clamp()` y unidades relativas (rem/%), nada de medidas fijas en px para layout.
- **Rendimiento:** lazy loading en imágenes, evitar reflows/layout shift, CSS mínimo y ordenado, fuentes con `font-display` correcto.
- **Mantenibilidad:** convención de nombres clara (ej. BEM), variables CSS para paleta (colores/espaciamiento), componentes reutilizables en vez de copiar y pegar.

## Formularios y datos (Django)
- Usar los forms de Django con sus errores y clases bien presentadas; estados: normal, error, deshabilitado, focus.
- Evitar divulgar datos por consola/JS; todo pasa por contexto/RequestContext.

## Flujo de trabajo
- Otorgar estructura primero (layout/template base), luego estilos, luego interacción.
- Autoevalúo: si una solución la escribiría un dev junior, la reformulo; exijo calidad de producto final, no "que funcione nada más".