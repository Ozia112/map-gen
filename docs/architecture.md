# Arquitectura y flujo

Este proyecto genera un mapa topográfico 3D a partir de un campo de alturas y lo renderiza con líneas de contorno “flotantes”.

## Componentes

- `terrain_generator.TopographicMapGenerator`
  - Normaliza semilla (SEED_MIN/SEED_MAX) y limita octavas (MAX_OCTAVES)
  - Backend de ruido automático: Perlin 3D o fBm vectorizado (por defecto)
  - Suavizado gaussiano
  - Capa de cráteres procedurales (perfil con fondo plano, transición y rim)
- `visualization`
  - `draw_map_3d`: líneas de contorno con offsets en su altura real
  - `export_map_clean`: exportación sin UI (PNG/SVG)
  - Utilidades: `_get_meshgrid` (caché), `_compute_z_base`, `_compute_levels`
  - Perímetro optimizado: cuatro trazos vectorizados
- `ui_controller`
  - Controles de matplotlib (sliders, color, semilla, cráteres, rotación)
  - Gizmo de orientación simple
- `web/`
  - UI web: `index.html`, `styles.css`, `app.js` con Eel

## Flujo de datos

1. `main.py` crea `TopographicMapGenerator` y genera el terreno inicial.
2. Se renderiza una previsualización (`export_preview_image`) para la UI web.
3. La UI (web/matplotlib) emite cambios → `eel.api_update` → `generate_terrain` → `export_preview_image`.
4. Exportaciones a alta calidad con `export_map_clean` a `./generados/`.

## Decisiones de diseño

- fBm vectorizado para rendimiento y estabilidad en resoluciones altas.
- Normalización de semilla para evitar estados extremos o cuelgues.
- Caché de meshgrid para evitar recalcular X/Y en cada render.
- Utilidades factoradas para reducir duplicación y facilitar mantenimiento.
