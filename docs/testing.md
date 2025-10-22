# Pruebas automatizadas

Las pruebas usan `pytest` y cubren la lógica principal del proyecto.

## Configuración

**Versión 2.2.0** - Octubre 22, 2025

Los tests están ubicados en `codigo/tests/`. Para ejecutarlos:

1. Activar el entorno virtual:

   ```powershell
   cd codigo
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

2. Ejecutar pytest:

   ```powershell
   pytest -q
   ```

**Nota**: Es importante ejecutar pytest desde la carpeta `codigo/` para que el path de importaciones sea correcto.

## Áreas cubiertas

- Normalización de semilla y límites (SEED_MIN/SEED_MAX)
- Selección de backend (Perlin vs fBm) y conmutación automática
- Utilidades de visualización (z-base y niveles seguros)
- Validación de modelos (MapModel)
- Controladores (MapController, RenderController)

## Escribir nuevas pruebas

- Coloca los archivos en `codigo/tests/` con prefijo `test_*.py`
- Evita pruebas frágiles con gráficos; prueba invariantes de datos y límites
- Los fixtures están en `codigo/tests/conftest.py`
