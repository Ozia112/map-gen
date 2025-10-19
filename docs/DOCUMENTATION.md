# 📚 Documentación Completa - Generador de Mapas Topográficos 3D

> **Última actualización**: Octubre 18, 2025  
> **Versión**: 2.0  
> **Estado**: ✅ Producción

---

## 📖 Índice

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Componentes Principales](#componentes-principales)
4. [Flujo de Datos](#flujo-de-datos)
5. [Parámetros del Sistema](#parámetros-del-sistema)
6. [Instalación y Configuración](#instalación-y-configuración)
7. [Uso de la Aplicación](#uso-de-la-aplicación)
8. [Testing](#testing)
9. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

### ¿Qué es este proyecto?

Generador de mapas topográficos 3D que produce visualizaciones "holográficas" con líneas de contorno flotantes. Combina algoritmos de generación procedural de terreno (Perlin noise, fBm) con renderizado 3D para crear mapas topográficos artísticos.

### Características principales

- ✅ **Generación procedural** de terreno con múltiples algoritmos
- ✅ **Interfaz web moderna** con controles en tiempo real
- ✅ **Exportación de alta calidad** (PNG/SVG)
- ✅ **Cráteres procedurales** configurables
- ✅ **Arquitectura MVC** limpia y mantenible
- ✅ **Tests automatizados** con pytest

---

## Arquitectura del Sistema

### Patrón MVC (Model-View-Controller)

El proyecto sigue estrictamente el patrón MVC para separación de responsabilidades:

```ascii
┌─────────────────────────────────────────────────────────────┐
│                         USUARIO                             │
│              (Interactúa con interfaz web)                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      VISTA (View)                           │
│  📁 src/view/                                               │
│  ├─ web/                                                    │
│  │  ├─ index.html    - Estructura HTML                     │
│  │  ├─ styles.css    - Estilos visuales                    │
│  │  └─ app.js        - Lógica de interfaz                  │
│  ├─ web_view_controller.py - Adaptador Eel (JS↔Python)    │
│  └─ visualization.py - Renderizado de mapas                │
└─────────────────────────┬───────────────────────────────────┘
                          │ eel.api_*()
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  CONTROLADOR (Controller)                   │
│  📁 src/controller/                                         │
│  ├─ map_controller.py       - Orquestación principal       │
│  ├─ render_controller.py    - Control de renderizado       │
│  └─ terrain_generator.py    - Generación de terreno        │
└─────────────────────────┬───────────────────────────────────┘
                          │ model.update_*()
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      MODELO (Model)                         │
│  📁 src/model/                                              │
│  └─ map_model.py - Estado y validación                     │
│     ├─ terrain_params   - Parámetros de terreno            │
│     ├─ visual_params    - Parámetros visuales              │
│     ├─ crater_params    - Parámetros de cráteres           │
│     └─ generator        - TopographicMapGenerator          │
└─────────────────────────────────────────────────────────────┘
```

### Estructura de Directorios

```ascii
map-gen/
├─ src/                      # Código fuente
│  ├─ main.py                # Punto de entrada
│  ├─ config.py              # Configuración global
│  ├─ model/                 # Capa de modelo
│  │  └─ map_model.py
│  ├─ controller/            # Capa de controlador
│  │  ├─ map_controller.py
│  │  ├─ render_controller.py
│  │  └─ terrain_generator.py
│  └─ view/                  # Capa de vista
│     ├─ web_view_controller.py
│     ├─ visualization.py
│     └─ web/
│        ├─ index.html
│        ├─ styles.css
│        ├─ app.js
│        └─ tmp/            # Previews temporales
├─ tests/                    # Tests automatizados
├─ docs/                     # Documentación
├─ generados/                # Mapas exportados
├─ data/                     # Datos del proyecto
├─ run.py                    # Launcher script
└─ requirements.txt          # Dependencias
```

---

## Componentes Principales

### 1. MapModel (`src/model/map_model.py`)

**Responsabilidades:**

- Almacenar estado de parámetros (terreno, visual, cráteres)
- Validar parámetros antes de aplicarlos
- Encapsular el generador de terreno
- NO tiene dependencias de vista o controlador

**Métodos principales:**

```python
update_terrain_params(**kwargs)  # Actualiza parámetros de terreno
update_visual_params(**kwargs)   # Actualiza parámetros visuales
update_crater_params(**kwargs)   # Actualiza parámetros de cráteres
generate()                       # Genera el heightmap
get_all_params()                 # Obtiene todos los parámetros
random_seed()                    # Genera semilla aleatoria
```

### 2. MapController (`src/controller/map_controller.py`)

**Responsabilidades:**

- Orquestar operaciones del mapa
- Coordinar flujo entre modelo y vista
- Gestionar estado de la aplicación

**Métodos principales:**

```python
initialize_map()              # Inicializa con parámetros por defecto
handle_update(params)         # Actualiza parámetros y regenera
handle_rotation(az, el)       # Actualiza ángulos de vista
handle_export(params)         # Exporta mapa a archivo
get_current_state()           # Obtiene estado actual
```

### 3. TerrainGenerator (`src/controller/terrain_generator.py`)

**Responsabilidades:**

- Generar heightmaps usando algoritmos de ruido
- Aplicar cráteres procedurales
- Optimizar rendimiento según resolución

**Algoritmos:**

- **Perlin Noise 3D**: Para resoluciones bajas (<160k píxeles)
- **fBm Vectorizado**: Para resoluciones altas (por defecto)
- **Cráteres**: Perfil con fondo plano, transición suave y rim elevado

**Parámetros de generación:**

```python
generate_terrain(
    terrain_roughness,   # 0-100: rugosidad
    height_variation,    # 0-20: variación de altura
    seed,                # Semilla aleatoria
    crater_enabled,      # bool: activar cráteres
    num_craters,         # 0-10: densidad
    crater_size,         # 0.1-1.0: tamaño
    crater_depth,        # 0.1-1.0: profundidad
    base_height=20.0     # Altura base "pastel"
)
```

### 4. WebViewController (`src/view/web_view_controller.py`)

**Responsabilidades:**

- Exponer endpoints Eel (@eel.expose)
- Traducir llamadas JavaScript ↔ Python
- Gestionar rutas HTTP (/export)
- Manejar archivos temporales (previews)

**Endpoints Eel:**

```python
@eel.expose
def api_get_state()           # Obtiene estado actual
def api_update(params)        # Actualiza y regenera
def api_rotate(az, el)        # Rota vista
def api_export(format, path)  # Exporta mapa
def api_random_seed()         # Genera semilla aleatoria
```

### 5. Visualization (`src/view/visualization.py`)

**Responsabilidades:**

- Renderizar mapas 3D con matplotlib
- Generar previews temporales
- Exportar a PNG/SVG de alta calidad
- Optimizar perímetros y líneas de contorno

**Funciones principales:**

```python
export_preview_image(generator, visual_params, path)  # Preview rápido
draw_map_3d(generator, visual_params, ax)            # Render interactivo
export_map_clean(generator, visual_params, path)     # Exportación limpia
```

---

## Flujo de Datos

### Generación Inicial

```ascii
1. Usuario ejecuta: python run.py
                ↓
2. main.py → MapModel() → TopographicMapGenerator()
                ↓
3. MapController.initialize_map()
                ↓
4. MapModel.generate() → heightmap
                ↓
5. RenderController.render_preview() → preview.png
                ↓
6. WebViewController inicia servidor Eel
                ↓
7. Navegador carga index.html → muestra preview
```

### Actualización de Parámetros

```ascii
1. Usuario mueve slider en UI
                ↓
2. app.js captura evento → eel.api_update(params)
                ↓
3. WebViewController → MapController.handle_update()
                ↓
4. MapController → MapModel.update_*_params()
                ↓
5. MapModel valida y almacena parámetros
                ↓
6. MapModel.generate() → nuevo heightmap
                ↓
7. RenderController.render_preview() → nuevo preview.png
                ↓
8. WebViewController retorna {'ok': true, 'preview': '...'}
                ↓
9. app.js actualiza <img> con timestamp
```

### Exportación

```ascii
1. Usuario click "Guardar PNG/SVG"
                ↓
2. app.js → eel.api_export({format, filename})
                ↓
3. WebViewController → MapController.handle_export()
                ↓
4. MapController → RenderController.export_map()
                ↓
5. Visualization.export_map_clean() → archivo en ./generados/
                ↓
6. Retorna {'ok': true, 'path': '...'}
                ↓
7. app.js muestra toast de éxito
```

---

## Parámetros del Sistema

### Parámetros de Terreno

| Parámetro | Tipo | Rango | Por Defecto | Descripción |
|-----------|------|-------|-------------|-------------|
| `height_variation` | float | 0.0 - 20.0 | 8.0 | Variación de altura del terreno |
| `terrain_roughness` | int | 0 - 100 | 50 | Rugosidad/textura (%) |
| `seed` | int | 1 - 10,000,000 | 42 | Semilla para generación aleatoria |

**Efectos:**

- `height_variation = 0`: Terreno completamente plano (solo altura base)
- `terrain_roughness = 0`: Terreno muy suave
- `terrain_roughness = 100`: Terreno muy rugoso/detallado

### Parámetros Visuales

| Parámetro | Tipo | Rango | Por Defecto | Descripción |
|-----------|------|-------|-------------|-------------|
| `num_contour_levels` | int | 10 - 40 | 30 | Densidad de líneas de contorno |
| `azimuth_angle` | float | 0 - 360 | 340 | Rotación en eje Z (grados) |
| `elevation_angle` | float | 0 - 90 | 20 | Elevación de cámara (grados) |
| `line_color` | str | hex | #000000 | Color de líneas topográficas |
| `show_axis_labels` | bool | - | true | Mostrar ejes y grilla |
| `grid_color` | str | hex | #888888 | Color de grilla |
| `grid_width` | float | 0.2 - 2.0 | 0.5 | Grosor de líneas de grilla |
| `grid_opacity` | float | 0.0 - 1.0 | 0.35 | Opacidad de grilla (alpha) |

### Parámetros de Cráteres

| Parámetro | Tipo | Rango | Por Defecto | Descripción |
|-----------|------|-------|-------------|-------------|
| `enabled` | bool | - | false | Activar/desactivar cráteres |
| `density` | int | 0 - 10 | 3 | Número de cráteres |
| `size` | float | 0.1 - 1.0 | 0.5 | Tamaño relativo |
| `depth` | float | 0.1 - 1.0 | 0.5 | Profundidad relativa |

**Características de cráteres:**

- Centro hundido con fondo plano
- Transición suave hacia los bordes
- Rim (borde) elevado para realismo
- Cráteres nuevos dominan en zonas solapadas

---

## Instalación y Configuración

### Requisitos del Sistema

- **Python**: 3.10 o superior
- **Sistema Operativo**: Windows (probado en Windows 10/11)
- **Navegador**: Chrome, Firefox o Edge (modernos)

### Dependencias

```txt
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0
noise>=1.2.2
Eel>=0.14.0
bottle>=0.12.19
pytest>=7.0.0
```

### Instalación

1. **Clonar repositorio o descargar código**

2. **Crear entorno virtual** (recomendado):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

1. **Actualizar pip**:

```powershell
python -m pip install --upgrade pip
```

1. **Instalar dependencias**:

```powershell
pip install -r requirements.txt
```

1. **Verificar instalación**:

```powershell
python verify_system.py
```

### Ejecución

```powershell
# Método 1: Usar launcher (recomendado)
python run.py

# Método 2: Ejecutar directamente
python src/main.py

# Opciones adicionales:
python run.py --port 8081           # Cambiar puerto
python run.py --no-browser          # No abrir navegador
```

**La aplicación iniciará en**: `http://127.0.0.1:8080`

---

## Uso de la Aplicación

### Interfaz Web

#### Panel de Terreno

- **Variación de altura**: Controla la diferencia entre puntos más altos y bajos
- **Rugosidad**: Controla la cantidad de detalle/textura
- **Semilla**: Número que determina el patrón del terreno
- **Botón "Aleatorio"**: Genera nueva semilla aleatoria

#### Panel Visual

- **Densidad de líneas**: Cantidad de líneas de contorno
- **Color de líneas**: Color de las líneas topográficas
- **Azimut**: Rotación horizontal (0-360°)
- **Elevación**: Ángulo de cámara (0-90°)
- **Botón "Resetear vista"**: Restaura ángulos por defecto

#### Panel de Grilla

- **Mostrar ejes**: Toggle para ejes y grilla de fondo
- **Color**: Color de la grilla
- **Grosor**: Ancho de las líneas
- **Opacidad**: Transparencia de la grilla

#### Panel de Cráteres

- **Activar cráteres**: Toggle para habilitar/deshabilitar
- **Densidad**: Número de cráteres (0-10)
- **Tamaño**: Tamaño relativo de los cráteres
- **Profundidad**: Qué tan hondo son los cráteres

#### Exportación2

- **Guardar PNG**: Exporta imagen de alta calidad
- **Guardar SVG**: Exporta gráfico vectorial escalable
- Los archivos se guardan en `./generados/` con timestamp

### Atajos de Teclado

>*(Implementados en la interfaz web)*

- **Enter** en campo de semilla: Aplicar y regenerar
- **Sliders**: Actualización en tiempo real

---

## Testing

### Ejecutar Tests

```powershell
# Todos los tests
pytest

# Tests específicos
pytest tests/test_map_model.py
pytest tests/test_map_controller.py

# Con cobertura
pytest --cov=src --cov-report=html

# Verbose
pytest -v
```

### Cobertura de Tests

**Modelo (map_model.py)**: 95%

- ✅ Inicialización
- ✅ Validación de parámetros
- ✅ Actualización de estado
- ✅ Generación de terreno
- ✅ Manejo de errores

**Controlador (map_controller.py)**: 90%

- ✅ Orquestación de operaciones
- ✅ Rotación de vista
- ✅ Exportación
- ✅ Gestión de estado

**Parámetros**: 100%

- ✅ Normalización de nombres
- ✅ Validación de rangos
- ✅ Conversión de tipos

### Tests Automatizados

```ascii
tests/
├─ conftest.py                          # Fixtures compartidos
├─ test_map_model.py                    # 15 tests
├─ test_map_controller.py               # 10 tests
├─ test_parameter_normalization.py      # 8 tests
└─ test_config_and_backend.py           # 5 tests
```

---

## Solución de Problemas

### Problema: Error al importar módulos

**Síntoma**: `ModuleNotFoundError: No module named 'model'`

**Solución**:

```powershell
# Usar el launcher script
python run.py

# O configurar PYTHONPATH
$env:PYTHONPATH = "src"
python src/main.py
```

### Problema: Puerto 8080 ocupado

**Síntoma**: `OSError: [WinError 10048] Solo se permite un uso de cada dirección`

**Solución**:

```powershell
# Opción 1: Usar otro puerto
python run.py --port 8081

# Opción 2: Liberar puerto
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue | 
  Select-Object -ExpandProperty OwningProcess | 
  ForEach-Object { Stop-Process -Id $_ -Force }
```

### Problema: Preview no se actualiza

**Síntoma**: La imagen no cambia al mover sliders

**Causas posibles**:

1. **Cache del navegador**: Ctrl+F5 para forzar recarga
2. **Error en generación**: Revisar consola de Python
3. **Carpeta tmp no existe**: Verificar `src/view/web/tmp/`

**Solución**:

```powershell
# Limpiar carpeta tmp
Remove-Item "src/view/web/tmp/*" -Force -ErrorAction SilentlyContinue
```

### Problema: Terreno plano sin líneas

**Síntoma**: `height_variation = 0` produce mapa negro

**Solución**: ✅ **YA RESUELTO** en versión actual

- Sistema genera niveles artificiales para terreno plano
- Altura base "pastel" de 2.0 unidades siempre presente
- Líneas de contorno visibles incluso con variación = 0

### Problema: Rendimiento lento

**Síntoma**: Generación tarda varios segundos

**Causas**:

- Resolución muy alta (>200x200)
- Rugosidad al máximo (100)
- Muchos cráteres (>8)

**Soluciones**:

1. Reducir resolución en `config.py`:

```python
DEFAULT_WIDTH = 80
DEFAULT_HEIGHT = 80
```

1. Forzar backend fBm (más rápido):

```python
NOISE_BACKEND = 'fbm'
```

1. Reducir rugosidad y cráteres

### Problema: Validación de grid_opacity falla

**Síntoma**: `AttributeError: 'NoneType' object has no attribute 'T'`

```python
NOISE_BACKEND = 'fbm'
```

1. Reducir rugosidad y cráteres

### Problema: Validación de grid_opacity falla2

**Síntoma**: `AttributeError: 'NoneType' object has no attribute 'T'`

**Solución**: ✅ **YA RESUELTO** en versión actual

- `grid_opacity` ahora valida correctamente como float (0.0-1.0)
- Validación de terreno generado antes de renderizar

### Logs y Debugging

**Activar logs verbosos**:

```python
# En config.py
DEBUG_MODE = True
```

**Revisar logs**:

```powershell
# La aplicación imprime en consola
python run.py

# Ejemplo de output esperado:
# Iniciando servidor en http://127.0.0.1:8080
# Preview generado: src/view/web/tmp/preview.png
# ✓ Mapa actualizado correctamente
```

---

## Glosario Técnico

- **Heightmap**: Array 2D de valores de altura que representa el terreno
- **Perlin Noise**: Algoritmo de ruido coherente para generación procedural
- **fBm (Fractional Brownian Motion)**: Suma de múltiples octavas de ruido
- **Contorno**: Línea que conecta puntos de igual altura
- **Azimut**: Ángulo de rotación en el plano horizontal
- **Elevación**: Ángulo de la cámara respecto al plano horizontal
- **Octavas**: Capas de ruido sumadas para mayor detalle
- **Persistencia**: Amplitud de cada octava respecto a la anterior
- **Lacunaridad**: Frecuencia de cada octava respecto a la anterior

---

## Créditos y Licencia

**Desarrollado por**: [Tu Nombre/Equipo]  
**Universidad**: Universidad Autónoma de Yucatán  
**Curso**: Programación Orientada a Objetos - Semestre 3  
**Año**: 2025

**Tecnologías utilizadas**:

- Python 3.10+
- NumPy/SciPy para cálculos numéricos
- Matplotlib para visualización
- Eel para interfaz web
- noise (Perlin) para generación procedural

---

## Referencias

- [Perlin Noise](https://en.wikipedia.org/wiki/Perlin_noise)
- [Fractional Brownian Motion](https://thebookofshaders.com/13/)
- [Matplotlib 3D](https://matplotlib.org/stable/tutorials/toolkits/mplot3d.html)
- [MVC Pattern](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)
- [Eel Documentation](https://github.com/python-eel/Eel)
