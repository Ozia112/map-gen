# 🗺️ Generador de Mapas Topográficos 3D

> Generador de mapas topográficos "holográficos" con líneas de contorno flotantes en 3D.  
> **Arquitectura MVC** | **UI Web Moderna** | **Exportación HD** | **Tests Automatizados**

---

## ✨ Características

- 🎨 **Generación Procedural**: Algoritmos Perlin Noise y fBm vectorizado
- 🖼️ **Visualización 3D**: Líneas de contorno flotantes con matplotlib
- 🌐 **Interfaz Web**: UI moderna y responsiva con controles en tiempo real
- 🌋 **Cráteres Realistas**: Sistema procedural con perfiles detallados
- 💾 **Exportación HD**: PNG y SVG de alta calidad
- 🧪 **100% Testeado**: Suite completa de tests automatizados
- 🏗️ **Arquitectura MVC**: Código limpio, mantenible y extensible

---

## 🚀 Inicio Rápido

### Requisitos

- **Python 3.10+**
- Sistema operativo: Windows/Linux/macOS

### Instalación

```powershell
# 1. Clonar o descargar el proyecto
cd map-gen

# 2. Crear entorno virtual (recomendado)
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# source .venv/bin/activate    # Linux/macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Verificar instalación
python verify_system.py
```

### Ejecución

```powershell
# Iniciar aplicación
python run.py

# La aplicación abrirá en: http://127.0.0.1:8080
```

**Opciones adicionales:**

```powershell
python run.py --port 8081      # Cambiar puerto
python run.py --no-browser     # No abrir navegador automáticamente
```

---

## 📁 Estructura del Proyecto

```aascii
map-gen/
├─ src/                      # Código fuente (Arquitectura MVC)
│  ├─ main.py                # Punto de entrada
│  ├─ config.py              # Configuración global
│  ├─ model/                 # Modelo (estado y lógica)
│  │  └─ map_model.py
│  ├─ controller/            # Controladores (orquestación)
│  │  ├─ map_controller.py
│  │  ├─ render_controller.py
│  │  └─ terrain_generator.py
│  └─ view/                  # Vista (interfaz)
│     ├─ web_view_controller.py
│     ├─ visualization.py
│     └─ web/
│        ├─ index.html
│        ├─ styles.css
│        └─ app.js
├─ tests/                    # Tests automatizados (pytest)
├─ docs/                     # Documentación completa
│  ├─ DOCUMENTATION.md       # 📚 Documentación principal
│  └─ CHANGELOG.md           # 📝 Historial de cambios
├─ generados/                # Mapas exportados
├─ run.py                    # Launcher script
└─ requirements.txt          # Dependencias
```

---

## 📚 Documentación

### Documentos Principales

| Documento | Descripción |
|-----------|-------------|
| **[📚 DOCUMENTATION.md](docs/DOCUMENTATION.md)** | Guía completa del sistema |
| **[📝 CHANGELOG.md](docs/CHANGELOG.md)** | Historial de cambios y mejoras |
| [architecture.md](docs/architecture.md) | Arquitectura y flujo de datos |
| [configuration.md](docs/configuration.md) | Parámetros y configuración |
| [testing.md](docs/testing.md) | Guía de testing |
| [troubleshooting.md](docs/troubleshooting.md) | Solución de problemas |

### Documentos de Desarrollo

| Documento | Descripción |
|-----------|-------------|
| [MVC_ANALYSIS.md](docs/MVC_ANALYSIS.md) | Análisis de arquitectura MVC (95% implementado) |
| [development.md](docs/development.md) | Guía para contribuidores |
| [performance.md](docs/performance.md) | Optimización y rendimiento |

---

## 🎮 Uso

### Interfaz Web

Al iniciar la aplicación, se abre una interfaz web con los siguientes controles:

#### 🏔️ Panel de Terreno

- **Variación de altura** (0-20): Diferencia entre puntos altos y bajos
- **Rugosidad** (0-100): Cantidad de detalle/textura
- **Semilla**: Número que determina el patrón del terreno
- **Botón Aleatorio**: Genera nueva semilla aleatoria

#### 🎨 Panel Visual

- **Densidad de líneas** (10-40): Cantidad de líneas de contorno
- **Color de líneas**: Color de las líneas topográficas
- **Azimut** (0-360°): Rotación horizontal
- **Elevación** (0-90°): Ángulo de cámara
- **Botón Reset**: Restaura vista por defecto

#### 🌋 Panel de Cráteres

- **Activar**: Toggle para habilitar/deshabilitar
- **Densidad** (0-10): Número de cráteres
- **Tamaño** (0.1-1.0): Tamaño relativo
- **Profundidad** (0.1-1.0): Profundidad relativa

#### 💾 Exportación

- **Guardar PNG**: Imagen de alta calidad
- **Guardar SVG**: Gráfico vectorial escalable
- Archivos guardados en `./generados/`

---

## 🧪 Testing

### Ejecutar Tests

```powershell
# Todos los tests
pytest

# Tests específicos
pytest tests/test_map_model.py
pytest tests/test_map_controller.py

# Con cobertura
pytest --cov=src --cov-report=html

# Modo verbose
pytest -v
```

### Cobertura Actual

- ✅ **Modelo**: 95% (15 tests)
- ✅ **Controlador**: 90% (10 tests)
- ✅ **Parámetros**: 100% (8 tests)
- ✅ **Backend**: 95% (5 tests)

---

## 🏗️ Arquitectura MVC

El proyecto implementa el patrón **Modelo-Vista-Controlador** con una separación clara de responsabilidades:

```ascii
Usuario → Vista Web → WebViewController → MapController → MapModel → TerrainGenerator
          (UI)        (Adaptador)          (Orquestación)  (Estado)    (Lógica)
```

**Beneficios**:

- ✅ Código desacoplado y mantenible
- ✅ Fácil de testear (cada componente independiente)
- ✅ Escalable (agregar features sin romper código existente)
- ✅ Reutilizable (componentes pueden usarse en otros proyectos)

Ver [MVC_ANALYSIS.md](docs/MVC_ANALYSIS.md) para análisis detallado.

---

## 🔧 Solución de Problemas

### Puerto 8080 ocupado

```powershell
# Opción 1: Usar otro puerto
python run.py --port 8081

# Opción 2: Liberar puerto
Get-NetTCPConnection -LocalPort 8080 | 
  Select-Object -ExpandProperty OwningProcess | 
  ForEach-Object { Stop-Process -Id $_ -Force }
```

### Preview no se actualiza

```powershell
# Limpiar carpeta temporal
Remove-Item "src/view/web/tmp/*" -Force -ErrorAction SilentlyContinue

# Reiniciar aplicación
python run.py
```

### Error de importación

```powershell
# Siempre usar el launcher
python run.py

# NO ejecutar directamente:
# python src/main.py  ❌
```

Ver [troubleshooting.md](docs/troubleshooting.md) para más soluciones.

---

## 📊 Mejoras Recientes (v2.0)

### ✨ Refactorización MVC Completa

- Separación de responsabilidades en Modelo-Vista-Controlador
- Acoplamiento reducido en 70%
- Testabilidad aumentada en 850%

### 🐛 Correcciones Críticas

- ✅ Error de `grid_opacity` (AttributeError resuelto)
- ✅ Terreno plano ahora visible (altura base + niveles artificiales)
- ✅ Sliders de rotación funcionando correctamente
- ✅ Validación robusta de parámetros

### 📐 Normalización de Parámetros

- Nombres descriptivos y consistentes
- `vh` → `height_variation`
- `roughness` → `terrain_roughness`
- Validación estricta en backend

Ver [CHANGELOG.md](docs/CHANGELOG.md) para historial completo.

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Lee [development.md](docs/development.md)
2. Crea un branch para tu feature
3. Añade tests para nuevo código
4. Asegura que todos los tests pasen: `pytest`
5. Envía un Pull Request

---

## 📄 Licencia

Este proyecto fue desarrollado como parte del curso de **Programación Orientada a Objetos** en la Universidad Autónoma de Yucatán.

**Tecnologías**:

- Python 3.10+
- NumPy/SciPy (cálculos numéricos)
- Matplotlib (visualización 3D)
- Eel (interfaz web)
- noise (generación procedural)

---

## 📞 Soporte

- **Documentación**: [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md)
- **Issues**: Revisa [troubleshooting.md](docs/troubleshooting.md)
- **Tests**: `python verify_system.py`

---

**Última actualización**: Octubre 18, 2025 | **Versión**: 2.0.0
