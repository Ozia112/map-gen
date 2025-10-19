# 📊 Diagramas del Sistema

> Diagramas de flujo y UML del Generador de Mapas Topográficos 3D

---

## 1. Diagrama de Flujo - Generación de Terreno e Interacción con UI

Este diagrama muestra el flujo completo desde el inicio de la aplicación, pasando por la generación de terreno, hasta la interacción en tiempo real con el usuario.

### Inicio y Generación Inicial

```ascii
┌──────────────────────────────────────────────────────────────────────┐
│                    INICIO DE LA APLICACIÓN                           │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   run.py        │
                    │ (Launcher)      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   main.py       │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
  ┌──────────┐       ┌──────────────┐     ┌──────────────┐
  │ MapModel │       │MapController │     │WebViewController│
  └────┬─────┘       └──────┬───────┘     └──────┬───────┘
       │                    │                     │
       ▼                    │                     │
┌────────────────┐          │                     │
│TerrainGenerator│          │                     │
└────────────────┘          │                     │
```

### Pipeline de Generación de Terreno

```ascii
┌─────────────────────────────────────────────────────────────────┐
│                   GENERACIÓN DE TERRENO                         │
└─────────────────────────────────────────────────────────────────┘

1. SELECCIÓN DE BACKEND
   ┌───────────────────────────────────┐
   │ Resolución < 160k píxeles?        │
   └───────┬───────────────┬───────────┘
           │ Sí            │ No
           ▼               ▼
    ┌─────────────┐  ┌─────────────┐
    │ Perlin 3D   │  │ fBm         │
    │ (Preciso)   │  │ (Rápido)    │
    └──────┬──────┘  └──────┬──────┘
           └────────┬────────┘
                    ▼

2. GENERACIÓN DE RUIDO BASE
   ┌────────────────────────────────┐
   │ Parámetros:                    │
   │ • scale = f(roughness)         │
   │ • octaves = f(roughness)       │
   │ • persistence = f(roughness)   │
   │ • seed (normalizado)           │
   └───────────────┬────────────────┘
                   ▼
   ┌────────────────────────────────┐
   │ Numpy Array [width x height]  │
   │ Valores: [-1.0, 1.0]           │
   └───────────────┬────────────────┘
                   ▼
3. ESCALADO POR ALTURA
   ┌────────────────────────────────┐
   │ terrain *= height_variation    │
   └───────────────┬────────────────┘
                   ▼

4. SUAVIZADO GAUSSIANO
   ┌────────────────────────────────┐
   │ gaussian_filter(terrain, σ=0.8)│
   └───────────────┬────────────────┘
                   ▼

5. NORMALIZACIÓN
   ┌────────────────────────────────┐
   │ terrain -= terrain.min()       │
   │ (Base en 0)                    │
   └───────────────┬────────────────┘
                   ▼

6. CRÁTERES (Si están activados)
   ┌────────────────────────────────┐
   │ For crater in num_craters:     │
   │   • Centro hundido             │
   │   • Transición suave           │
   │   • Rim elevado                │
   └───────────────┬────────────────┘
                   ▼

7. ALTURA BASE "PASTEL"
   ┌────────────────────────────────┐
   │ terrain += BASE_HEIGHT (2.0)   │
   │ (Siempre visible)              │
   └───────────────┬────────────────┘
                   ▼
           ┌───────────────┐
           │   HEIGHTMAP   │
           │   COMPLETO    │
           └───────────────┘
```

### Renderizado de Preview

```ascii
┌─────────────────────────────────────────────────────────────────┐
│                      RENDERIZADO                                │
└─────────────────────────────────────────────────────────────────┘

HEIGHTMAP → RenderController.render_preview()
                    │
                    ▼
            ┌───────────────┐
            │ visualization │
            │ .export_      │
            │ preview_image │
            └───────┬───────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
┌─────────┐  ┌─────────────┐  ┌─────────────┐
│ Compute │  │   Draw      │  │   Draw      │
│ Levels  │→ │  Contours   │→ │  Supports   │
│(30)     │  │  (3D Lines) │  │  & Grid     │
└─────────┘  └─────────────┘  └─────────────┘
                    │
                    ▼
            ┌──────────────┐
            │ preview.png  │
            │ (web/tmp/)   │
            └──────────────┘
```

### Interacción en Tiempo Real

```ascii
┌──────────────────────────────────────────────────────────────────┐
│           ACTUALIZACIÓN EN TIEMPO REAL (Usuario)                 │
└──────────────────────────────────────────────────────────────────┘

USUARIO mueve slider
        │
        ▼
┌───────────────────────┐
│ app.js                │
│ • Captura evento      │
│ • Actualiza estado    │
│ • Debounce (300ms)    │
└──────────┬────────────┘
           │
           │ eel.api_update(params)
           ▼
┌──────────────────────────────┐
│ WebViewController            │
│ @eel.expose api_update()     │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ MapController                │
│ .handle_update()             │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ MapModel                     │
│ • update_*_params()          │
│ • Validación de parámetros   │
│ • generate()                 │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ NUEVO HEIGHTMAP              │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ RenderController             │
│ .render_preview()            │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ NUEVO preview.png            │
└──────────┬───────────────────┘
           │
           │ return {'ok': true}
           ▼
┌──────────────────────────────┐
│ app.js                       │
│ • Actualiza <img>            │
│ • showLoader(false)          │
│ • Usuario ve nuevo mapa      │
└──────────────────────────────┘

TIEMPO TOTAL: ~500ms - 2s
(Depende de resolución y parámetros)
```

### Exportación de Alta Calidad

```ascii
┌──────────────────────────────────────────────────────────────────┐
│                    EXPORTACIÓN HD                                │
└──────────────────────────────────────────────────────────────────┘

USUARIO click "Guardar PNG/SVG"
        │
        ▼
┌───────────────────────┐
│ app.js                │
│ els.btnExport.onclick │
└──────────┬────────────┘
           │
           │ eel.api_export({format, filename})
           ▼
┌──────────────────────────────┐
│ WebViewController            │
│ @eel.expose api_export()     │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ MapController                │
│ .handle_export()             │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ RenderController             │
│ .export_map()                │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ visualization                │
│ .export_map_clean()          │
│ • Sin UI                     │
│ • Alta resolución (300 DPI)  │
│ • Respeta vista actual       │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ ./generados/                 │
│ map_YYYYMMDD_HHMMSS.png      │
└──────────┬───────────────────┘
           │
           │ return {'ok': true, 'path': '...'}
           ▼
┌──────────────────────────────┐
│ showToast('✓ Guardado')      │
└──────────────────────────────┘
```

---

## 2. Diagrama de Clases UML

### Vista General del Sistema

```ascii
┌────────────────────────────────────────────────────────────────┐
│                   ARQUITECTURA MVC                             │
└────────────────────────────────────────────────────────────────┘

┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   MODEL     │         │  CONTROLLER  │         │     VIEW     │
│             │←────────│              │────────→│              │
│  MapModel   │  uses   │MapController │ updates │WebViewController│
│             │         │              │         │              │
└──────┬──────┘         └──────┬───────┘         └──────┬───────┘
       │                       │                        │
       │ contains              │ uses                   │ serves
       ▼                       ▼                        ▼
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│  Terrain    │         │  Render      │         │  Web         │
│  Generator  │         │  Controller  │         │  Interface   │
└─────────────┘         └──────────────┘         └──────────────┘
```

### Clases Principales

#### MapModel (Modelo)

```ascii
┌─────────────────────────────────────────────────────────────┐
│                      <<Model>>                              │
│                      MapModel                               │
├─────────────────────────────────────────────────────────────┤
│ ATRIBUTOS                                                   │
│ - terrain_params: Dict[str, Any]                            │
│   · height_variation: float (0-20)                          │
│   · terrain_roughness: int (0-100)                          │
│   · seed: int (1-10000000)                                  │
│                                                             │
│ - visual_params: Dict[str, Any]                             │
│   · num_contour_levels: int (10-40)                         │
│   · azimuth_angle: float (0-360)                            │
│   · elevation_angle: float (0-90)                           │
│   · line_color: str                                         │
│   · show_axis_labels: bool                                  │
│   · grid_color, grid_width, grid_opacity                    │
│                                                             │
│ - crater_params: Dict[str, Any]                             │
│   · enabled: bool                                           │
│   · density: int (0-10)                                     │
│   · size: float (0.1-1.0)                                   │
│   · depth: float (0.1-1.0)                                  │
│                                                             │
│ - _generator: TopographicMapGenerator                       │
│ - _last_heightmap: Optional[np.ndarray]                     │
├─────────────────────────────────────────────────────────────┤
│ MÉTODOS PÚBLICOS                                            │
│ + __init__(width: int, height: int)                         │
│ + generator @property                                       │
│ + heightmap @property                                       │
│ + update_terrain_params(**kwargs) : Dict                    │
│ + update_visual_params(**kwargs) : Dict                     │
│ + update_crater_params(**kwargs) : Dict                     │
│ + generate() : np.ndarray                                   │
│ + get_all_params() : Dict                                   │
│ + random_seed() : int                                       │
│                                                             │
│ MÉTODOS PRIVADOS                                            │
│ - _validate_terrain_params(params) : Dict                   │
│ - _validate_visual_params(params) : Dict                    │
│ - _validate_crater_params(params) : Dict                    │
└─────────────────────────────────────────────────────────────┘
```

#### TopographicMapGenerator

```ascii
┌─────────────────────────────────────────────────────────────┐
│                    <<Generator>>                            │
│              TopographicMapGenerator                        │
├─────────────────────────────────────────────────────────────┤
│ ATRIBUTOS                                                   │
│ + width: int                                                │
│ + height: int                                               │
│ + terrain: Optional[np.ndarray]                             │
│ + fig: Optional[Figure]                                     │
│ + ax: Optional[Axes3D]                                      │
│ + last_backend: Optional[str]  # 'perlin' o 'fbm'           │
├─────────────────────────────────────────────────────────────┤
│ MÉTODOS PÚBLICOS                                            │
│ + __init__(width: int, height: int)                         │
│ + generate_terrain(                                         │
│     terrain_roughness: int,                                 │
│     height_variation: float,                                │
│     seed: int,                                              │
│     crater_enabled: bool,                                   │
│     num_craters: int,                                       │
│     crater_size: float,                                     │
│     crater_depth: float,                                    │
│     base_height: float = 20.0                               │
│   ) : None                                                  │
│                                                             │
│ MÉTODOS PRIVADOS                                            │
│ - _generate_fbm_terrain(...) : np.ndarray                   │
│   · Fractal Brownian Motion vectorizado                     │
│   · Múltiples octavas                                       │
│   · Rápido para resoluciones altas                          │
│                                                             │
│ - _apply_craters_visible(...) : None                        │
│   · Crea cráteres realistas                                 │
│   · Centro hundido + rim elevado                            │
│   · Transición suave                                        │
└─────────────────────────────────────────────────────────────┘
```

#### MapController (Controlador Principal)

```ascii
┌─────────────────────────────────────────────────────────────┐
│                    <<Controller>>                           │
│                   MapController                             │
├─────────────────────────────────────────────────────────────┤
│ ATRIBUTOS                                                   │
│ + model: MapModel                                           │
│ + render_controller: RenderController                       │
├─────────────────────────────────────────────────────────────┤
│ MÉTODOS                                                     │
│ + __init__(model: MapModel)                                 │
│                                                             │
│ # Gestión de parámetros                                     │
│ + handle_update(params: Dict) : Dict[str, Any]              │
│ + handle_terrain_update(**kwargs) : Dict                    │
│ + handle_visual_update(**kwargs) : Dict                     │
│ + handle_crater_update(**kwargs) : Dict                     │
│                                                             │
│ # Rotación de vista                                         │
│ + handle_rotation(azimuth, elevation) : Dict                │
│ + handle_reset_rotation() : Dict                            │
│                                                             │
│ # Inicialización y estado                                   │
│ + initialize_map() : Dict                                   │
│ + get_current_state() : Dict                                │
│ + handle_random_seed() : Dict                               │
│                                                             │
│ # Exportación                                               │
│ + handle_export(export_params: Dict) : Dict                 │
└─────────────────────────────────────────────────────────────┘
```

#### RenderController

```ascii
┌─────────────────────────────────────────────────────────────┐
│                    <<Controller>>                           │
│                   RenderController                          │
├─────────────────────────────────────────────────────────────┤
│ ATRIBUTOS                                                   │
│ (Stateless - sin atributos de instancia)                    │
├─────────────────────────────────────────────────────────────┤
│ MÉTODOS                                                     │
│ + render_preview(                                           │
│     generator: TopographicMapGenerator,                     │
│     visual_params: Dict,                                    │
│     path: str                                               │
│   ) : bool                                                  │
│   · Genera preview rápido para UI web                       │
│                                                             │
│ + export_map(                                               │
│     generator: TopographicMapGenerator,                     │
│     visual_params: Dict,                                    │
│     format: str,                                            │
│     path: str                                               │
│   ) : bool                                                  │
│   · Exporta mapa de alta calidad                            │
│                                                             │
│ + export_with_dialog(                                       │
│     generator: TopographicMapGenerator,                     │
│     visual_params: Dict,                                    │
│     format: str                                             │
│   ) : Optional[str]                                         │
│   · Muestra diálogo de guardado                             │
└─────────────────────────────────────────────────────────────┘
```

#### WebViewController (Vista - Adaptador)

```ascii
┌─────────────────────────────────────────────────────────────┐
│                 <<View Controller>>                         │
│                 WebViewController                           │
├─────────────────────────────────────────────────────────────┤
│ ATRIBUTOS                                                   │
│ + map_controller: MapController                             │
│ + web_dir: str                                              │
│ + preview_dir: str                                          │
│ + preview_path: str                                         │
├─────────────────────────────────────────────────────────────┤
│ MÉTODOS PRINCIPALES                                         │
│ + __init__(map_controller, web_dir, preview_dir)            │
│ + setup_eel_routes() : None                                 │
│ + setup_http_routes() : None                                │
│ + start_server(host, port, mode, ...) : None                │
│                                                             │
│ MÉTODOS PRIVADOS                                            │
│ - _cleanup_old_files(keep_files) : None                     │
│ - _generate_preview() : None                                │
├─────────────────────────────────────────────────────────────┤
│ ENDPOINTS EEL (@eel.expose)                                 │
│ + api_get_state() : Dict                                    │
│   · Retorna estado actual del modelo                        │
│                                                             │
│ + api_update(params: Dict) : Dict                           │
│   · Actualiza parámetros y regenera                         │
│                                                             │
│ + api_rotate(azimuth, elevation) : Dict                     │
│   · Rota la vista sin regenerar terreno                     │
│                                                             │
│ + api_reset_rotation() : Dict                               │
│   · Resetea ángulos a valores por defecto                   │
│                                                             │
│ + api_export(format, filename) : Dict                       │
│   · Exporta mapa a archivo                                  │
│                                                             │
│ + api_random_seed() : Dict                                  │
│   · Genera semilla aleatoria                                │
└─────────────────────────────────────────────────────────────┘
```

### Diagrama de Relaciones

```ascii
┌─────────────────────────────────────────────────────────────┐
│                  RELACIONES ENTRE CLASES                    │
└─────────────────────────────────────────────────────────────┘

     MapModel ────────uses──────→ TopographicMapGenerator
        │                                   
        │                                   
        │ orchestrates                      
        ▼                                   
  MapController ──────uses──────→ RenderController
        │                              │
        │                              │
        │                              │ uses
        │                              ▼
        │                        visualization
        │                          (module)
        │
        │ delegates
        ▼
 WebViewController ──────serves──────→ Web Interface
        │                              (HTML/CSS/JS)
        │
        │ exposes via Eel
        ▼
   @eel.expose endpoints
   (API Bridge JS ↔ Python)
```

### Principios de Diseño Aplicados

```ascii
┌─────────────────────────────────────────────────────────────┐
│                 PRINCIPIOS SOLID                            │
└─────────────────────────────────────────────────────────────┘

✅ S - Single Responsibility Principle
   · MapModel: SOLO gestión de estado
   · MapController: SOLO orquestación
   · RenderController: SOLO renderizado
   · WebViewController: SOLO adaptación web

✅ O - Open/Closed Principle
   · Fácil agregar nuevos backends de ruido
   · Fácil agregar nuevos formatos de exportación
   · Sin modificar código existente

✅ L - Liskov Substitution
   · (No hay herencia en la arquitectura actual)

✅ I - Interface Segregation
   · Cada controlador expone solo métodos relevantes
   · No hay interfaces "gordas"

✅ D - Dependency Inversion
   · Controller depende de Model (abstracción)
   · View depende de Controller (abstracción)
   · Las dependencias fluyen hacia las abstracciones

┌─────────────────────────────────────────────────────────────┐
│              PATRONES DE DISEÑO                             │
└─────────────────────────────────────────────────────────────┘

✅ MVC (Model-View-Controller)
   · Separación clara de responsabilidades
   · Vista independiente del modelo
   · Controlador como orquestador

✅ Facade Pattern
   · MapController como fachada para operaciones complejas
   · Simplifica interacción entre componentes

✅ Strategy Pattern
   · Selección dinámica de backend (Perlin vs fBm)
   · Basado en resolución

✅ Singleton-like (Module Pattern)
   · visualization como módulo con funciones stateless
   · _meshgrid_cache para optimización
```

---

## Resumen de Flujos Principales

### 1. Generación Inicial

```ascii
run.py → main.py → MapModel → TerrainGenerator → Heightmap
    → RenderController → preview.png → WebViewController → Browser
```

### 2. Actualización de Parámetros

```ascii
User → app.js → eel.api_update() → WebViewController → MapController
    → MapModel → validate → generate → RenderController → preview.png
    → return JSON → app.js → update <img>
```

### 3. Rotación de Vista

```ascii
User → app.js → eel.api_rotate() → WebViewController → MapController
    → MapModel.update_visual_params() → RenderController → preview.png
    → return JSON → app.js → update <img>
```

### 4. Exportación

```ascii
User → app.js → eel.api_export() → WebViewController → MapController
    → RenderController.export_map() → visualization.export_map_clean()
    → save to ./generados/ → return JSON → app.js → showToast()
```

---

**Última actualización**: Octubre 18, 2025
