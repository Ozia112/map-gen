# Guía de desarrollo

## Configuración inicial

**Versión 2.2.0** - Octubre 22, 2025

El proyecto usa una estructura reorganizada con separación código/documentación:

1. **Clonar el repositorio**:

   ```bash
   git clone <url-del-repo>
   cd map-gen
   ```

2. **Crear entorno virtual** (dentro de `codigo/`):

   ```bash
   cd codigo
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Instalar dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación** (desde la raíz):

   ```bash
   cd ..
   python run.py
   ```

**Nota**: El launcher `run.py` está en la raíz del proyecto, pero todo el código está en `codigo/`. No es necesario cambiar de directorio manualmente al ejecutar.

## Estilo y convenciones

- Python 3.10+
- Nombres descriptivos; funciones pequeñas y puras cuando sea posible
- Evitar duplicación: usa utilidades (`_get_meshgrid`, `_compute_z_base`, `_compute_levels`)
- Capturar excepciones de forma acotada (no `except Exception` globales)

## Estructura

**Rutas actualizadas (dentro de `codigo/src/`):**

- `controller/terrain_generator.py`: lógica de alturas, mantener backends separables
- `view/visualization.py`: no recalcular mallas, preferir vectorización
- `view/ui_controller.py`: callbacks claros, sin estado global; locks simples para UI
- `view/web/`: `app.js` aplica cambios via `eel.api_update` y normaliza inputs
- `model/map_model.py`: modelo de datos del mapa
- `controller/config.py`: configuración centralizada

**Salidas**: Los archivos generados se guardan en `codigo/generados/`

## Flujo de contribución

1. Crear rama
2. Añadir/actualizar tests en `codigo/tests/`
3. Ejecutar `pytest -q` desde `codigo/`:

   ```bash
   cd codigo
   pytest -q
   ```

4. Abrir PR con descripción y notas de rendimiento (si aplica)

## Extensión de generadores

- Añadir nuevos backends en `TopographicMapGenerator` y conmutar por `config.NOISE_BACKEND`
- Mantener normalización de semilla y límites

## Depuración

- Inspeccionar `generator.last_backend` para saber Perlin vs fBm
- Registrar tiempos de generación si se modifica el pipeline
