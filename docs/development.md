# Guía de desarrollo

## Estilo y convenciones

- Python 3.10+
- Nombres descriptivos; funciones pequeñas y puras cuando sea posible
- Evitar duplicación: usa utilidades (`_get_meshgrid`, `_compute_z_base`, `_compute_levels`)
- Capturar excepciones de forma acotada (no `except Exception` globales)

## Estructura

- `terrain_generator.py`: lógica de alturas, mantener backends separables
- `visualization.py`: no recalcular mallas, preferir vectorización
- `ui_controller.py`: callbacks claros, sin estado global; locks simples para UI
- `web/`: `app.js` aplica cambios via `eel.api_update` y normaliza inputs

## Flujo de contribución

1. Crear rama
2. Añadir/actualizar tests en `tests/`
3. Ejecutar `pytest -q`
4. Abrir PR con descripción y notas de rendimiento (si aplica)

## Extensión de generadores

- Añadir nuevos backends en `TopographicMapGenerator` y conmutar por `config.NOISE_BACKEND`
- Mantener normalización de semilla y límites

## Depuración

- Inspeccionar `generator.last_backend` para saber Perlin vs fBm
- Registrar tiempos de generación si se modifica el pipeline
