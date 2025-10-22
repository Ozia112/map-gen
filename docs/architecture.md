# Arquitectura y flujo

Este proyecto genera un mapa topográfico 3D a partir de un campo de alturas y lo renderiza con líneas de contorno "flotantes".

## Estructura del Proyecto

**Versión 2.2.0** - Octubre 22, 2025

El proyecto está organizado con separación completa entre código y documentación:

```ascii
map-gen/
├── codigo/                    # 📦 TODO EL CÓDIGO
│   ├── src/                  # Código fuente MVC
│   │   ├── model/           # Modelo de datos
│   │   ├── view/            # Visualización y UI
│   │   │   └── web/        # Interfaz web (Eel)
│   │   │       ├── home/   # UI principal
│   │   │       └── laboratorio-3d/  # Editor 3D
│   │   ├── controller/      # Controladores
│   │   └── utils/           # Utilidades
│   ├── tests/               # Tests unitarios (pytest)
│   ├── generados/           # Salidas generadas (PNG/SVG)
│   ├── requirements.txt     # Dependencias Python
│   └── .venv/              # Entorno virtual
├── docs/                     # 📚 DOCUMENTACIÓN
│   └── [8 archivos .md]
└── run.py                    # 🚀 Launcher principal
```

**Rutas importantes:**

- Código fuente: `codigo/src/`
- Salidas: `codigo/generados/`
- Documentación: `docs/`
- Tests: `codigo/tests/`

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

1. `run.py` (raíz) configura el path y lanza `codigo/src/main.py`
2. `main.py` crea `TopographicMapGenerator` y genera el terreno inicial
3. Se renderiza una previsualización (`export_preview_image`) para la UI web
4. La UI (web/matplotlib) emite cambios → `eel.api_update` → `generate_terrain` → `export_preview_image`
5. Exportaciones a alta calidad con `export_map_clean` a `codigo/generados/`

## Decisiones de diseño

- fBm vectorizado para rendimiento y estabilidad en resoluciones altas.
- Normalización de semilla para evitar estados extremos o cuelgues.
- Caché de meshgrid para evitar recalcular X/Y en cada render.
- Utilidades factoradas para reducir duplicación y facilitar mantenimiento.

## Laboratorio 3D

### Arquitectura Modular

El Laboratorio 3D fue completamente refactorizado de un archivo monolítico a una arquitectura modular de 7 archivos especializados:

```ascii
laboratorio-3d/
├── main.js            # Coordinación UI y eventos
├── scene.js           # Lógica Three.js y renderizado 3D
├── services.js        # Comunicación con backend (heightmap)
├── config.js          # Configuración centralizada
├── deps.js            # Carga dinámica de Three.js
├── preload.js         # Precarga de librerías desde home
└── utils.js           # Utilidades y testing
```

### Componentes.1

**main.js - Coordinador de UI:**:

- `boot()`: Inicialización principal del laboratorio
- `initializeDependencies()`: Carga asíncrona de Three.js y dependencias
- `loadTerrain()`: Obtiene heightmap del backend y carga geometría
- `exitLaboratory()`: Navegación multi-estrategia con fallbacks
- `wire*Controls()`: Eventos de UI separados por categoría (POI, carreteras, áreas, exportación)

**scene.js - Renderizado 3D:**

- `initScene()`: Configura cámara, renderer, luces y controles OrbitControls
- `loadTerrainMesh()`: Crea geometría PlaneGeometry con heightmap
- `addPoi()`: Añade puntos de interés 3D (edificios, vehículos, aéreos)
- `buildRoadBetween()`: Genera carreteras con algoritmo A*
- `export*()`: Exporta escena a PNG/OBJ/SVG

**services.js - API Backend:**

- `fetchHeightmap()`: Obtiene datos del terreno desde Python
- `checkHeightmapAvailable()`: Verifica disponibilidad de datos
- Validación exhaustiva de estructura de datos
- Manejo robusto de errores con feedback visual

**config.js - Configuración:**

- `scene`: Parámetros de cámara (FOV, posición, near/far)
- `lighting`: Configuración de luces direccionales y ambiente
- `poi`: Configuración por tipo (tamaños, colores, geometrías)
- `road`: Parámetros de generación (ancho, color, A*)
- `export`: Configuración de formatos de exportación

**utils.js - Herramientas:**

- `PerformanceMonitor`: Medición de rendimiento de operaciones
- `debug`: Sistema de logging configurable
- `validateHeightmap()`: Validación de datos del terreno
- `testMode`: Modo de pruebas activable con `?test=1`

### Flujo de Inicialización

```ascii
Usuario click "Laboratorio 3D"
        │
        ▼
    boot()
        │
        ▼
initializeDependencies()
   ├─ Intenta cargar Three.js local
   ├─ Fallback a CDN si falla
   ├─ OrbitControls
   ├─ OBJExporter
   └─ SVGRenderer
        │
        ▼
    initScene()
   ├─ Cámara PerspectiveCamera
   ├─ WebGLRenderer
   ├─ Luces (Directional + Ambient)
   ├─ OrbitControls
   └─ Grid Helper
        │
        ▼
  loadTerrain()
   ├─ fetchHeightmap() → Python
   │   └─ Valida estructura
   ├─ loadTerrainMesh()
   │   ├─ PlaneGeometry(res, res)
   │   └─ Aplica heightmap a vertices
   └─ Añade mesh a escena
        │
        ▼
  wireControls()
   ├─ POI: Añadir/Editar/Eliminar
   ├─ Carreteras: Generar entre POIs
   ├─ Áreas: Definir regiones
   ├─ Visualización: Modos de render
   └─ Exportación: PNG/OBJ/SVG
        │
        ▼
✅ Laboratorio listo para interacción
```

### Características Principales

**POIs (Puntos de Interés):**

- **Tipos**: Edificios (BoxGeometry), Vehículos (SphereGeometry), Aéreos (TetrahedronGeometry)
- **Propiedades**: Nombre, posición (X, Z), orientación (yaw)
- **Etiquetas**: CSS2DRenderer con estilos configurables
- **Interacción**: Click para seleccionar, botones para editar/eliminar

**Carreteras:**

- **Generación**: Algoritmo A* entre 2 POIs seleccionados
- **Adaptación**: Respeta altura del terreno (heightmap)
- **Personalización**: Ancho y color configurables
- **Visualización**: TubeGeometry siguiendo el path

**Exportación:**

- **PNG**: Captura de alta calidad (con/sin UI)
- **OBJ**: Geometría para importar en Blender/Maya/3ds Max
- **SVG**: Líneas de contorno vectoriales (SVGRenderer)

**Modos de Visualización:**

- **Mapa de altura**: Colores según elevación
- **Wireframe**: Solo edges de la geometría
- **Sombreado**: Renderizado normal con luces

### Sistema de Testing

**Activación**: Añadir `?test=1` a la URL del laboratorio

**Características del modo test:**

- Performance monitoring automático
- Debug logging detallado en consola
- Validación exhaustiva de datos
- Métricas de tiempo de operaciones
- Estado de dependencias

**Uso:**

```javascript
// En utils.js
debug.info('Terreno cargado', { vertices: mesh.geometry.vertices.length });
PerformanceMonitor.start('loadTerrain');
// ... operación costosa ...
PerformanceMonitor.end('loadTerrain'); // Muestra tiempo en consola
```

### Decisiones de Diseño Lab3D

**Modularidad:**

- Separación de responsabilidades (UI, 3D, API, Config, Utils)
- Facilita testing y mantenimiento
- Permite iterar rápidamente en componentes individuales

**Configuración Centralizada:**

- Un solo lugar para ajustar parámetros
- Experimentación rápida sin buscar en código
- Documentación implícita de valores por defecto

**Robustez:**

- Navegación multi-estrategia con fallbacks
- Validación exhaustiva de datos del backend
- Manejo de errores con feedback visual claro
- Disposición correcta de recursos 3D

**Performance:**

- Carga asíncrona de dependencias grandes
- Validación antes de operaciones costosas
- Sin console.log en producción
- Performance monitoring para identificar cuellos de botella
