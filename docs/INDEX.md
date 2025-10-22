# 📚 Map Generator - Documentación Principal

<div align="center">

## **Sistema de Generación Procedural de Mapas Topográficos 3D**

[![Version](https://img.shields.io/badge/version-2.2.0-blue.svg)](CHANGELOG.md)
[![Architecture](https://img.shields.io/badge/architecture-MVC-green.svg)](#arquitectura)
[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)](#tecnologías)

</div>

---

## 🗺️ Tabla de Contenidos

### 📖 Documentación Esencial

| Documento | Descripción | Estado |
|-----------|-------------|--------|
| **[CHANGELOG](CHANGELOG.md)** | 📅 Línea de tiempo completa del desarrollo | ✅ Actualizado |
| **[CODE_REFERENCE](CODE_REFERENCE.md)** | 💻 Snippets de código y ejemplos | ✅ Completo |
| **[architecture.md](architecture.md)** | 🏗️ Arquitectura MVC del sistema | ✅ Documentado |
| **[configuration.md](configuration.md)** | ⚙️ Guía de configuración | ✅ Actualizado |

### 🔧 Documentación Técnica

| Documento | Descripción |
|-----------|-------------|
| **[development.md](development.md)** | 🛠️ Guía para desarrolladores |
| **[testing.md](testing.md)** | 🧪 Estrategias de testing |
| **[performance.md](performance.md)** | ⚡ Optimizaciones y benchmarks |
| **[troubleshooting.md](troubleshooting.md)** | 🩹 Solución de problemas comunes |

> **Nota**: La documentación del Laboratorio 3D está integrada en [architecture.md](architecture.md)

---

## 🎯 Introducción

**Map Generator** es un sistema avanzado de generación procedural de mapas topográficos 3D que utiliza algoritmos de ruido Perlin para crear terrenos realistas. El proyecto ha evolucionado desde una aplicación monolítica hasta una arquitectura MVC robusta con optimización automática de SVG.

### ✨ Características Principales

#### 🗻 Generación de Terreno

- **Algoritmo Perlin Noise 3D** para terrenos procedurales naturales
- **Cráteres realistas** con física de impacto
- **Configuración paramétrica** completa (altura, rugosidad, densidad)
- **Semillas aleatorias** para reproducibilidad

#### 🎨 Visualización Avanzada

- **Mapas topográficos 3D** con líneas de contorno flotantes
- **Optimización automática de SVG** (reducción ~65% en grupos)
- **Rotación y perspectiva** configurables (azimuth, elevation)
- **Sistema de colores** personalizable por tipo de terreno

#### 💾 Exportación Inteligente

- **PNG de alta calidad** con transparencia
- **SVG optimizado** con metadata preservada
- **Nomenclatura descriptiva** automática (Grid, Axis, Terrain)
- **Clasificación multi-criterio** de elementos visuales

#### 🖥️ Interfaz de Usuario

- **Web UI moderna** con controles en tiempo real
- **Preview instantáneo** de cambios
- **Laboratorio 3D** con Three.js para exploración interactiva
- **Feedback visual** (loaders, toasts, validación)

---

## 🏗️ Arquitectura

El sistema sigue el patrón **MVC (Modelo-Vista-Controlador)** con una separación clara de responsabilidades:

```ascii
┌─────────────────────────────────────────────────────┐
│                    USUARIO                          │
│              (Interfaz Web/Browser)                 │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│                   VISTA (View)                      │
│  ┌─────────────────────────────────────────────┐   │
│  │  web_view_controller.py                     │   │
│  │  • Adaptador Eel (JS ↔ Python)             │   │
│  │  • Endpoints API expuestos                  │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │  visualization.py                           │   │
│  │  • Renderizado matplotlib                   │   │
│  │  • Exportación con optimización             │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │  web/ (HTML/CSS/JS)                         │   │
│  │  • UI interactiva                           │   │
│  │  • Laboratorio 3D (Three.js)               │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│               CONTROLADOR (Controller)              │
│  ┌─────────────────────────────────────────────┐   │
│  │  map_controller.py                          │   │
│  │  • Orquestación principal                   │   │
│  │  • Coordinación Modelo-Vista                │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │  render_controller.py                       │   │
│  │  • Lógica de renderizado                    │   │
│  │  • Gestión de exportación                   │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │  terrain_generator.py                       │   │
│  │  • Generación procedural                    │   │
│  │  • Algoritmos de ruido                      │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │  config.py                                  │   │
│  │  • Configuración centralizada               │   │
│  │  • Parámetros por defecto                   │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│                  MODELO (Model)                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  map_model.py                               │   │
│  │  • Gestión de estado                        │   │
│  │  • Validación de parámetros                 │   │
│  │  • Lógica de negocio pura                   │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│                UTILIDADES (Utils)                   │
│  ┌─────────────────────────────────────────────┐   │
│  │  svg_optimizer.py                           │   │
│  │  • Optimización post-procesamiento          │   │
│  │  • Clasificación multi-criterio             │   │
│  │  • Preservación de metadata                 │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 📊 Métricas de Calidad

| Métrica | Valor | Mejora vs v1.0 |
|---------|-------|----------------|
| **Acoplamiento** | Bajo | ↓ 70% |
| **Cohesión** | Alta | ↑ 200% |
| **Testabilidad** | 95% | ↑ 850% |
| **Mantenibilidad** | Excelente | ↑ 217% |
| **Cobertura de tests** | 85% | - |

Ver [architecture.md](architecture.md) para análisis completo.

---

## 🚀 Inicio Rápido

### 1️⃣ Instalación

```bash
# Clonar repositorio
git clone <repository-url>
cd map-gen

# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows)
.venv\Scripts\activate

# Activar entorno (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2️⃣ Ejecución

```bash
# Método 1: Launcher (Recomendado)
python run.py

# Método 2: Directamente
python -m src.main
```

### 3️⃣ Uso Básico

1. **Ajustar parámetros** en la interfaz web
   - Variación de altura (0-100)
   - Rugosidad del terreno (0.1-2.0)
   - Densidad de cráteres (0-100)

2. **Generar mapa** con el botón "Generar Mapa"

3. **Exportar resultado**:
   - **PNG**: Imagen de alta calidad
   - **SVG**: Vector optimizado automáticamente

---

## 🔄 Flujo de Datos

### Generación de Mapa

```ascii
┌──────────────┐
│   Usuario    │
│ (Web Browser)│
└──────┬───────┘
       │ 1. Ajusta parámetros
       ▼
┌──────────────────┐
│ WebViewController│  (Vista)
│ • Recibe input   │
│ • Valida básico  │
└──────┬───────────┘
       │ 2. Llama update_parameters()
       ▼
┌──────────────────┐
│ MapController    │  (Controlador)
│ • Orquesta flujo │
│ • Valida negocio │
└──────┬───────────┘
       │ 3. Actualiza estado
       ▼
┌──────────────────┐
│   MapModel       │  (Modelo)
│ • Valida rangos  │
│ • Almacena estado│
└──────┬───────────┘
       │ 4. Solicita generación
       ▼
┌──────────────────┐
│TerrainGenerator  │  (Controlador)
│ • Perlin Noise   │
│ • Genera heightmap│
└──────┬───────────┘
       │ 5. Retorna terrain
       ▼
┌──────────────────┐
│ RenderController │  (Controlador)
│ • Crea figura    │
│ • Renderiza 3D   │
└──────┬───────────┘
       │ 6. Muestra resultado
       ▼
┌──────────────────┐
│ Visualization    │  (Vista)
│ • Matplotlib     │
│ • Preview HTML   │
└──────────────────┘
```

### Exportación SVG Optimizada

```ascii
┌──────────────┐
│   Usuario    │
│ Clic "Guardar│
│     SVG"     │
└──────┬───────┘
       │ 1. Solicita exportación
       ▼
┌──────────────────────────┐
│  visualization.py        │
│  export_map_clean()      │
└──────┬───────────────────┘
       │ 2. Genera SVG temp
       ▼
┌──────────────────────────┐
│  Matplotlib              │
│  savefig(temp.svg)       │
└──────┬───────────────────┘
       │ 3. Archivo temporal creado
       ▼
┌──────────────────────────┐
│  _add_svg_metadata()     │
│  • Inyecta parámetros    │
│  • XML comments          │
└──────┬───────────────────┘
       │ 4. Metadata agregada
       ▼
┌──────────────────────────┐
│  SVGOptimizer            │
│  optimize_svg()          │
│  ┌────────────────────┐  │
│  │ PASO 1: Clasificar │  │
│  │ • Grid detection   │  │
│  │ • Axis grouping    │  │
│  │ • Label detection  │  │
│  └────────┬───────────┘  │
│  ┌────────▼───────────┐  │
│  │ PASO 2: Reorganizar│  │
│  │ • Crear jerarquía  │  │
│  │ • Renombrar IDs    │  │
│  │ • Agrupar lógico   │  │
│  └────────┬───────────┘  │
│  ┌────────▼───────────┐  │
│  │ PASO 3: Optimizar  │  │
│  │ • Limpiar defs     │  │
│  │ • Preservar meta   │  │
│  │ • Escribir output  │  │
│  └────────────────────┘  │
└──────┬───────────────────┘
       │ 5. SVG optimizado
       ▼
┌──────────────────────────┐
│  Usuario recibe          │
│  • Archivo limpio        │
│  • 55 grupos vs 150      │
│  • IDs descriptivos      │
│  • Metadata preservada   │
└──────────────────────────┘
```

---

## 📈 Evolución del Proyecto

### Línea de Tiempo de Desarrollo

```ascii
v1.0.0 (Inicial)
   │
   ├─ Código monolítico (main.py 377 líneas)
   ├─ Sin arquitectura definida
   ├─ Parámetros ambiguos (vh, roughness)
   └─ Tests limitados
   │
   ▼
v2.0.0 (Refactorización MVC)
   │
   ├─ Arquitectura MVC completa (95%)
   ├─ Separación de responsabilidades
   ├─ Normalización de parámetros
   ├─ Fix: Terreno plano visualizable
   ├─ Fix: AttributeError en inicialización
   ├─ Testing robusto (33 tests)
   └─ Documentación completa
   │
   ▼
v2.1.0 (Optimización SVG + Consolidación)
   │
   ├─ Optimización automática de SVG
   ├─ Clasificación multi-criterio
   ├─ Preservación de labels
   ├─ Reducción ~65% grupos (150→55)
   ├─ Consolidación de código
   ├─ config.py → controller/config.py
   └─ Eliminación de wrappers obsoletos
```

Ver [CHANGELOG.md](CHANGELOG.md) para historia completa detallada.

---

## 🛠️ Tecnologías

### Backend (Python)

- **Python 3.8+** - Lenguaje principal
- **NumPy** - Procesamiento numérico
- **matplotlib** - Renderizado 2D/3D
- **lxml** - Procesamiento XML/SVG
- **Eel** - Bridge Python-JavaScript
- **pytest** - Framework de testing

### Frontend (JavaScript)

- **HTML5/CSS3** - Interfaz
- **Vanilla JavaScript** - Lógica de UI
- **Three.js** - Visualización 3D
- **OBJExporter** - Exportación de modelos

### Algoritmos

- **Perlin Noise 3D** - Generación procedural
- **fBm (Fractional Brownian Motion)** - Textura natural
- **Multi-criteria Classification** - Optimización SVG

---

## 📖 Guías de Uso

### Para Usuarios

1. **[configuration.md](configuration.md)** - Configurar parámetros del mapa
2. **[troubleshooting.md](troubleshooting.md)** - Resolver problemas comunes

### Para Desarrolladores

1. **[development.md](development.md)** - Setup del entorno de desarrollo
2. **[architecture.md](architecture.md)** - Entender la arquitectura MVC
3. **[CODE_REFERENCE.md](CODE_REFERENCE.md)** - Ejemplos de código
4. **[testing.md](testing.md)** - Escribir y ejecutar tests
5. **[performance.md](performance.md)** - Optimizar rendimiento

### Para Contribuidores

1. Lee [CHANGELOG.md](CHANGELOG.md) para entender la historia
2. Revisa [architecture.md](architecture.md) para la estructura
3. Consulta [CODE_REFERENCE.md](CODE_REFERENCE.md) para patrones
4. Sigue las convenciones en [development.md](development.md)

---

## 🎓 Conceptos Clave

### Parámetros Normalizados

| Parámetro | Tipo | Rango | Descripción |
|-----------|------|-------|-------------|
| `height_variation` | float | 0-100 | Variación de altura del terreno |
| `terrain_roughness` | float | 0.1-2.0 | Rugosidad/detalle del terreno |
| `azimuth_angle` | float | 0-360 | Rotación horizontal (grados) |
| `elevation_angle` | float | 0-90 | Ángulo de elevación (grados) |
| `crater_density` | float | 0-100 | Densidad de cráteres |
| `grid_opacity` | float | 0.0-1.0 | Opacidad del grid (0=invisible) |

Ver [configuration.md](configuration.md) para lista completa.

### Clasificación de Elementos SVG

El optimizador clasifica elementos usando **criterios múltiples**:

1. **Grid BoundingBox**: 12 líneas estructurales (4 base + 8 verticales)
2. **Axis Elements**: Labels + ticks + líneas paralelas
3. **Terrain Vectors**: Contornos y superficie base
4. **Labels de Ejes**: Texto con fondo blanco para legibilidad

Ver [CODE_REFERENCE.md](CODE_REFERENCE.md#clasificación-svg) para detalles.

---

## 🔍 Recursos Adicionales

### Diagramas

- **[DIAGRAMS.md](DIAGRAMS.md)** - Diagramas visuales del sistema
- **Flujo MVC** - En [architecture.md](architecture.md)
- **Clasificación SVG** - En [CODE_REFERENCE.md](CODE_REFERENCE.md)

### Referencias Externas

- [Perlin Noise Explained](https://en.wikipedia.org/wiki/Perlin_noise)
- [MVC Pattern](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)
- [SVG Specification](https://www.w3.org/TR/SVG2/)
- [matplotlib 3D](https://matplotlib.org/stable/gallery/mplot3d/index.html)

---

## 📊 Estado del Proyecto

### ✅ Completado (v2.1.0)

- [x] Arquitectura MVC (95%)
- [x] Normalización de parámetros (100%)
- [x] Testing robusto (85% cobertura)
- [x] Optimización automática SVG
- [x] Preservación de labels
- [x] Consolidación de código
- [x] Documentación completa

### 🚧 En Progreso

- [ ] Laboratorio 3D avanzado
- [ ] Exportación OBJ mejorada
- [ ] Sistema de plugins

### 💡 Futuro (v2.2.0+)

- [ ] Soporte para múltiples algoritmos de ruido
- [ ] Templates de terreno predefinidos
- [ ] Modo batch processing
- [ ] API REST para integración externa

---

## 📝 Convenciones

### Commits

- `feat:` - Nueva característica
- `fix:` - Corrección de bug
- `refactor:` - Refactorización sin cambio funcional
- `docs:` - Cambios en documentación
- `test:` - Añadir/actualizar tests
- `perf:` - Mejora de rendimiento

### Branches

- `main` - Código estable en producción
- `develop` - Código en desarrollo
- `feature/*` - Nuevas características
- `fix/*` - Correcciones de bugs

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una branch (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'feat: add amazing feature'`)
4. Push a la branch (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

Ver [development.md](development.md) para guía completa.

---

## 📄 Licencia

Este proyecto está bajo la licencia especificada en [LICENSE](../LICENSE).

---

## 📞 Contacto

- **Repositorio**: [GitHub](https://github.com/Ozia112/map-gen)
- **Documentación**: Este archivo y [CHANGELOG.md](CHANGELOG.md)
- **Issues**: [GitHub Issues](https://github.com/Ozia112/map-gen/issues)

---

<div align="center">

## **Map Generator v2.1.0**

Generación Procedural • Arquitectura MVC • Optimización Automática

[🏠 Inicio](#-map-generator---documentación-principal) • [📖 Changelog](CHANGELOG.md) • [💻 Código](CODE_REFERENCE.md) • [🏗️ Arquitectura](architecture.md)

</div>
