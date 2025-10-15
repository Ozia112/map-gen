# Configuración y parámetros

La configuración vive en `src/config.py`.

## Parámetros principales

- `TERRAIN_PARAMS`
  - `terrain_roughness` (0–100): Rugosidad → controla escala, octavas y persistencia
  - `height_variation`: Amplitud de alturas
  - `seed`: Semilla reproducible (normalizada a [SEED_MIN, SEED_MAX])
  - `crater_*`: Activación y controles de cráteres
- `VISUAL_PARAMS`
  - `num_contour_levels`: Densidad de líneas
  - `elevation_angle`, `azimuth_angle`: Vista 3D
  - `line_color`, `grid_*`: Estilo
- `WINDOW_CONFIG`: Tamaño y márgenes de la figura
- `TERRAIN_SIZE`: Resolución (ancho x alto)

## Límites y backend

- `NOISE_BACKEND`: `'fbm'` (recomendado) o `'perlin'`
- `SEED_MIN`, `SEED_MAX`: Rango seguro de semilla
- `MAX_OCTAVES`: Límite de octavas (rendimiento)
- `PERLIN_MAX_PIXELS`: Conmutación automática a fBm si resolución alta

## Exportación

- Las exportaciones (PNG/SVG) se guardan en `./generados/` (fuera de `src`).
