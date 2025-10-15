# Generador de Mapas Topográficos 3D

> Mapas topográficos “holográficos” con líneas flotantes en 3D. UI web (Eel) + controles clásicos (matplotlib), exportación a PNG/SVG y backend de ruido optimizado.

## Estructura del proyecto

```ascii
map gen/
├─ src/
│  ├─ main.py               # Aplicación principal (inicia UI web con Eel)
│  ├─ terrain_generator.py  # Generación de terreno (Perlin/fBm, cráteres)
│  ├─ visualization.py      # Render 3D, exportación y utilidades
│  ├─ ui_controller.py      # Controles para UI matplotlib
│  ├─ config.py             # Parámetros y límites (backend, semillas, octavas)
│  └─ web/                  # UI web (HTML/CSS/JS)
├─ generados/               # Salidas PNG/SVG (se crea automáticamente)
├─ tests/                   # Pruebas automatizadas (pytest)
└─ docs/                    # Documentación modular
```

Documentación (en `docs/`):

- `architecture.md`: arquitectura y flujo de datos
- `configuration.md`: parámetros y límites
- `development.md`: estilo, estructura y contribución
- `testing.md`: cómo ejecutar y escribir pruebas
- `performance.md`: tuning de rendimiento
- `troubleshooting.md`: errores comunes y soluciones

## Requisitos

- Python 3.10+ (probado en Windows)
- Dependencias (ver `requirements.txt`):
  - numpy, scipy, matplotlib
  - noise (Perlin)
  - Eel (UI web) y bottle (servidor http)
  - pytest (tests)

## Instalación (Windows, PowerShell)

```powershell
# 1) (Opcional pero recomendado) crear y activar entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Actualizar pip
python -m pip install --upgrade pip

# 3) Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

```powershell
python .\src\main.py
```

- Previsualización: `src/web/tmp/preview.png`
- Exportaciones: `./generados/`

Parámetros opcionales:

```powershell
# Elegir puerto y no abrir navegador automáticamente
python .\src\main.py --port 8081 --no-browser

# (No recomendado) Exponer en red local: se te preguntará por diálogo; por seguridad usa 127.0.0.1
```

## Cómo funciona (resumen)

- `terrain_generator.TopographicMapGenerator`:
  - Semilla normalizada (SEED_MIN/SEED_MAX), límite de octavas (MAX_OCTAVES)
  - Backend automático: Perlin o fBm vectorizado (por defecto fBm)
  - Suavizado gaussiano y cráteres procedurales
- `visualization`:
  - Líneas de contorno “flotantes”, caja de soporte
  - Caché de meshgrid, niveles seguros, z-base robusto
  - Perímetro optimizado (4 líneas vectorizadas)
- `config`: toggles/límites para backend, semillas, octavas, tamaño

Más en `docs/architecture.md` y `docs/performance.md`.

## Controles (UI web)

- Variación de altura, Rugosidad, Densidad de líneas
- Semilla (normalizada) y botón Aleatoria
- Rotación (Azimut / Elevación)
- Cráteres (activar + densidad/tamaño/profundidad)
- Ejes y grilla (color, grosor, opacidad)

## Exportación

- Botones “Guardar PNG/SVG” exportan el mapa sin UI a `./generados/`.
- Se respetan vista y estilo actuales.

## Desarrollo y mantenimiento

- Ver `docs/development.md` (naming, estructura, PRs) y `docs/configuration.md`.
- Para nuevas features: extender generadores y UI web.

## Pruebas automatizadas

- Ejecutar:

```powershell
pytest -q
```

- Cobertura inicial: normalización de semilla, selección de backend, utilidades de visualización.
- Guía para escribir más: `docs/testing.md`.

## Solución de problemas

- ImportError al ejecutar `src/main.py`: usar import absoluto (`import config`).
- Semillas grandes: normalización + fBm por defecto.
- Rendimiento: ver `docs/performance.md`.

### Seguridad (antes de publicar o usar en red)

- Por defecto el servidor corre en `127.0.0.1` (solo tu equipo).
- Evita `0.0.0.0` salvo que sepas lo que haces y estés detrás de firewall/VPN.
- Las exportaciones escriben archivos en tu disco; no expongas el servicio en redes no confiables.

## Licencia y contribución

- PRs bienvenidos. Sigue `docs/development.md` y añade tests.
