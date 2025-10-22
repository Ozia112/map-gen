# 💻 Referencia de Código - Map Generator

> Snippets de código, patrones de implementación y ejemplos consolidados

---

## 📑 Tabla de Contenidos

- [Arquitectura MVC](#arquitectura-mvc)
- [Generación de Terreno](#generación-de-terreno)
- [Optimización SVG](#optimización-svg)
- [Renderizado y Exportación](#renderizado-y-exportación)
- [Validación de Parámetros](#validación-de-parámetros)
- [Testing](#testing)
- [Patrones de Diseño](#patrones-de-diseño)

---

## Arquitectura MVC

### Modelo (MapModel)

**Archivo**: `src/model/map_model.py`

```python
class MapModel:
    """
    Modelo del mapa - Gestión de estado y validación
    
    Responsabilidades:
    - Almacenar estado de parámetros
    - Validar rangos y tipos
    - Normalizar valores
    - Lógica de negocio pura
    """
    
    def __init__(self):
        # Parámetros de terreno
        self.height_variation = TERRAIN_PARAMS['height_variation']['default']
        self.terrain_roughness = TERRAIN_PARAMS['terrain_roughness']['default']
        self.seed = TERRAIN_PARAMS['seed']['default']
        
        # Parámetros visuales
        self.azimuth_angle = VISUAL_PARAMS['azimuth_angle']['default']
        self.elevation_angle = VISUAL_PARAMS['elevation_angle']['default']
        self.grid_opacity = VISUAL_PARAMS['grid_opacity']['default']
        
        # Parámetros de cráteres
        self.crater_density = CRATER_PARAMS['crater_density']['default']
        
    def validate_terrain_params(self, params: dict) -> dict:
        """
        Valida parámetros de terreno contra rangos definidos
        
        Args:
            params: Diccionario con parámetros a validar
            
        Returns:
            dict: Parámetros validados y normalizados
            
        Raises:
            ValueError: Si algún parámetro está fuera de rango
        """
        validated = {}
        
        for key, value in params.items():
            if key not in TERRAIN_PARAMS:
                raise ValueError(f"Parámetro desconocido: {key}")
            
            param_config = TERRAIN_PARAMS[key]
            
            # Validar rango
            if 'min' in param_config and value < param_config['min']:
                raise ValueError(
                    f"{key} debe ser >= {param_config['min']}, got {value}"
                )
            if 'max' in param_config and value > param_config['max']:
                raise ValueError(
                    f"{key} debe ser <= {param_config['max']}, got {value}"
                )
            
            # Convertir tipo
            expected_type = param_config.get('type', float)
            validated[key] = expected_type(value)
        
        return validated
```

### Controlador (MapController)

**Archivo**: `src/controller/map_controller.py`

```python
class MapController:
    """
    Controlador principal - Orquesta la lógica de negocio
    
    Responsabilidades:
    - Coordinar Modelo y Vista
    - Gestionar flujo de generación
    - Manejar eventos de usuario
    - Delegar tareas específicas
    """
    
    def __init__(self):
        self.model = MapModel()
        self.generator = TopographicMapGenerator()
        self.render_controller = RenderController(self.generator, self.model)
    
    def update_parameters(self, params: dict) -> dict:
        """
        Actualiza parámetros del modelo con validación
        
        Args:
            params: Nuevos parámetros del usuario
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            # Clasificar parámetros por tipo
            terrain_params = {
                k: v for k, v in params.items() 
                if k in TERRAIN_PARAMS
            }
            visual_params = {
                k: v for k, v in params.items() 
                if k in VISUAL_PARAMS
            }
            crater_params = {
                k: v for k, v in params.items() 
                if k in CRATER_PARAMS
            }
            
            # Validar cada conjunto
            if terrain_params:
                validated_terrain = self.model.validate_terrain_params(terrain_params)
                for key, value in validated_terrain.items():
                    setattr(self.model, key, value)
            
            if visual_params:
                validated_visual = self.model.validate_visual_params(visual_params)
                for key, value in validated_visual.items():
                    setattr(self.model, key, value)
            
            if crater_params:
                validated_crater = self.model.validate_crater_params(crater_params)
                for key, value in validated_crater.items():
                    setattr(self.model, key, value)
            
            return {"success": True, "message": "Parámetros actualizados"}
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def generate_map(self) -> dict:
        """
        Genera un nuevo mapa con los parámetros actuales
        
        Returns:
            dict: {"success": bool, "message": str, "preview": str}
        """
        try:
            # Generar terreno
            self.generator.generate(
                width=self.model.width,
                height=self.model.height,
                height_variation=self.model.height_variation,
                roughness=self.model.terrain_roughness,
                seed=self.model.seed
            )
            
            # Añadir cráteres si aplica
            if self.model.crater_density > 0:
                self.generator.add_craters(
                    density=self.model.crater_density
                )
            
            # Renderizar preview
            preview_html = self.render_controller.render_preview()
            
            return {
                "success": True,
                "message": "Mapa generado exitosamente",
                "preview": preview_html
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}
```

### Vista (Visualization)

**Archivo**: `src/view/visualization.py`

```python
def export_map_clean(generator, filename, fmt='png', 
                     azimuth=315, elevation=30, 
                     grid_opacity=0.35, **visual_params):
    """
    Exporta mapa con optimización automática para SVG
    
    Args:
        generator: TopographicMapGenerator con terreno
        filename: Ruta completa de salida
        fmt: Formato ('png' o 'svg')
        azimuth: Ángulo horizontal (0-360°)
        elevation: Ángulo vertical (0-90°)
        grid_opacity: Opacidad del grid (0.0-1.0)
        **visual_params: Parámetros adicionales
        
    Returns:
        bool: True si exportación exitosa
    """
    if generator.terrain is None:
        raise ValueError("No hay terreno generado")
    
    # Crear figura matplotlib
    temp_fig = plt.figure(figsize=(10, 10), facecolor='black')
    ax = temp_fig.add_subplot(111, projection='3d', facecolor='black')
    
    # Configurar vista 3D
    ax.view_init(elev=elevation, azim=azimuth)
    
    # Renderizar terreno
    _render_terrain_to_axis(ax, generator, grid_opacity, **visual_params)
    
    # Exportar según formato
    if str(fmt).lower() == 'svg':
        # FLUJO DE OPTIMIZACIÓN SVG
        
        # 1. Crear archivo temporal
        temp_fd, temp_path = tempfile.mkstemp(suffix='.svg', prefix='map_temp_')
        os.close(temp_fd)
        
        # 2. Guardar matplotlib a temporal
        temp_fig.savefig(
            temp_path, 
            format='svg',
            bbox_inches='tight',
            facecolor='black',
            pad_inches=0
        )
        
        # 3. Agregar metadata
        _add_svg_metadata(temp_path, visual_params)
        
        # 4. Optimizar estructura
        safe_print("\n[>] Optimizando estructura SVG...")
        from utils.svg_optimizer import optimize_svg
        optimize_svg(temp_path, filename)
        
        # 5. Eliminar temporal
        try:
            os.unlink(temp_path)
        except Exception as e:
            safe_print(f"[!] No se pudo eliminar temporal: {e}")
        
        safe_print(f"[✓] SVG optimizado guardado en: {filename}")
        
    else:
        # Exportación PNG directa
        temp_fig.savefig(
            filename,
            format=fmt,
            bbox_inches='tight',
            facecolor='black',
            dpi=300
        )
        safe_print(f"[✓] {fmt.upper()} guardado en: {filename}")
    
    plt.close(temp_fig)
    return True
```

---

## Generación de Terreno

### Algoritmo Perlin Noise

**Archivo**: `src/controller/terrain_generator.py`

```python
class TopographicMapGenerator:
    """
    Generador de terreno procedural usando Perlin Noise
    """
    
    def generate(self, width=256, height=256, 
                 height_variation=50, roughness=0.5, seed=None):
        """
        Genera heightmap usando Perlin Noise 3D
        
        Args:
            width: Ancho en píxeles
            height: Alto en píxeles
            height_variation: Variación de altura (0-100)
            roughness: Rugosidad del terreno (0.1-2.0)
            seed: Semilla para reproducibilidad
            
        Returns:
            np.ndarray: Matriz heightmap
        """
        # Normalizar semilla
        seed = self._normalize_seed(seed)
        np.random.seed(seed)
        
        # Seleccionar backend según resolución
        total_pixels = width * height
        use_perlin3d = total_pixels < 160000
        
        if use_perlin3d:
            # Perlin 3D puro (más rápido para baja resolución)
            heightmap = self._generate_perlin3d(
                width, height, roughness, seed
            )
        else:
            # fBm vectorizado (mejor para alta resolución)
            heightmap = self._generate_fbm(
                width, height, roughness, seed
            )
        
        # Escalar por variación de altura
        scale_factor = height_variation / 100.0
        heightmap = heightmap * scale_factor * 10.0
        
        # Añadir base "pastel"
        heightmap += BASE_HEIGHT  # 2.0 unidades
        
        self.terrain = heightmap
        self.width = width
        self.height = height
        
        return heightmap
    
    def _generate_fbm(self, width, height, roughness, seed):
        """
        Fractional Brownian Motion (fBm) para textura natural
        """
        x, y = self._get_meshgrid(width, height)
        
        # Múltiples octavas de ruido
        noise = np.zeros((height, width))
        frequency = 1.0
        amplitude = 1.0
        max_value = 0.0
        
        octaves = int(4 + roughness * 2)
        persistence = 0.5
        
        for _ in range(octaves):
            # Generar octava de ruido
            octave_noise = self._noise_layer(
                x * frequency, 
                y * frequency, 
                seed
            )
            
            noise += octave_noise * amplitude
            max_value += amplitude
            
            amplitude *= persistence
            frequency *= 2.0
        
        # Normalizar a [-1, 1]
        noise = noise / max_value
        
        return noise
    
    def add_craters(self, density=50, min_radius=5, max_radius=30):
        """
        Añade cráteres realistas al terreno
        
        Args:
            density: Densidad de cráteres (0-100)
            min_radius: Radio mínimo en píxeles
            max_radius: Radio máximo en píxeles
        """
        if self.terrain is None:
            raise ValueError("Genere terreno primero")
        
        # Calcular número de cráteres
        area = self.width * self.height
        num_craters = int((density / 100.0) * (area / 10000))
        
        for _ in range(num_craters):
            # Posición aleatoria
            cx = np.random.randint(0, self.width)
            cy = np.random.randint(0, self.height)
            
            # Radio aleatorio
            radius = np.random.uniform(min_radius, max_radius)
            
            # Profundidad basada en radio (física de impacto)
            depth = radius * 0.3
            
            # Aplicar cráter
            self._apply_crater(cx, cy, radius, depth)
    
    def _apply_crater(self, cx, cy, radius, depth):
        """
        Aplica un cráter individual con perfil realista
        """
        # Crear máscara circular
        y_indices, x_indices = np.ogrid[
            :self.height, 
            :self.width
        ]
        
        # Distancia desde el centro
        distance = np.sqrt(
            (x_indices - cx)**2 + 
            (y_indices - cy)**2
        )
        
        # Perfil del cráter (función gaussiana invertida)
        mask = distance < radius
        crater_profile = np.exp(-((distance / radius) ** 2) * 2)
        
        # Aplicar depresión
        self.terrain[mask] -= depth * crater_profile[mask]
```

---

## Optimización SVG

### Clasificación Multi-Criterio

**Archivo**: `src/utils/svg_optimizer.py`

```python
class SVGOptimizer:
    """
    Optimizador de estructura SVG con clasificación inteligente
    
    Proceso:
    1. Clasificar elementos (grid, axis, terrain, labels)
    2. Reorganizar jerarquía
    3. Renombrar IDs descriptivamente
    4. Preservar metadata
    """
    
    def optimize_svg(self, input_path: str, output_path: str):
        """
        Optimiza estructura SVG completa
        
        Args:
            input_path: Ruta del SVG de matplotlib
            output_path: Ruta del SVG optimizado
        """
        # Parsear SVG
        tree = etree.parse(input_path)
        root = tree.getroot()
        
        # PASO 1: Clasificar elementos
        classified = self._classify_elements(root)
        
        # PASO 2: Reorganizar estructura
        new_root = self._reorganize_structure(root, classified)
        
        # PASO 3: Optimizar y guardar
        self._write_optimized(new_root, output_path)
    
    def _classify_elements(self, root):
        """
        Clasifica elementos SVG usando múltiples criterios
        
        Returns:
            dict: {
                'grid_bbox': [...],  # 12 líneas estructurales
                'axis_height': [...], # Elementos eje Z
                'axis_y': [...],      # Elementos eje Y
                'axis_x': [...],      # Elementos eje X
                'terrain': [...],     # Vectores de terreno
                'labels': [...]       # Labels de ejes
            }
        """
        classified = {
            'grid_bbox': [],
            'axis_height': [],
            'axis_y': [],
            'axis_x': [],
            'terrain': [],
            'labels': []
        }
        
        # Encontrar todos los grupos
        groups = root.findall('.//{http://www.w3.org/2000/svg}g')
        
        for group in groups:
            group_id = group.get('id', '')
            
            # 1. GRID BOUNDING BOX (12 líneas)
            if group_id == 'grid3d_0':
                lines = group.findall('.//{http://www.w3.org/2000/svg}path')
                if len(lines) == 12:
                    classified['grid_bbox'].append(group)
                    continue
            
            # 2. AXIS HEIGHT (Paralels + Label)
            if group_id == 'grid3d_3':  # Líneas paralelas
                classified['axis_height'].append(group)
            elif group_id == 'axis3d_2':  # Label "Altura"
                # Detectar labels (tienen text_N children)
                has_label = self._has_text_children(group)
                if has_label:
                    classified['labels'].append(('height', group))
                else:
                    classified['axis_height'].append(group)
            
            # 3. AXIS Y (Paralels + Label)
            elif group_id == 'grid3d_2':
                classified['axis_y'].append(group)
            elif group_id == 'axis3d_1':
                has_label = self._has_text_children(group)
                if has_label:
                    classified['labels'].append(('y', group))
                else:
                    classified['axis_y'].append(group)
            
            # 4. AXIS X (Paralels + Label)
            elif group_id == 'grid3d_1':
                classified['axis_x'].append(group)
            elif group_id == 'axis3d_0':
                has_label = self._has_text_children(group)
                if has_label:
                    classified['labels'].append(('x', group))
                else:
                    classified['axis_x'].append(group)
            
            # 5. TERRAIN (line2d_N)
            elif 'line2d' in group_id:
                classified['terrain'].append(group)
        
        return classified
    
    def _has_text_children(self, group):
        """
        Detecta si un grupo contiene elementos de texto (labels)
        
        Args:
            group: Elemento SVG <g>
            
        Returns:
            bool: True si contiene text_N children
        """
        for child in group:
            child_id = child.get('id', '')
            if 'text_' in child_id:
                return True
        return False
    
    def _reorganize_structure(self, old_root, classified):
        """
        Reorganiza estructura SVG con jerarquía lógica
        
        Nueva estructura:
        <svg>
          <defs>...</defs>
          <metadata>...</metadata>
          <g id="Grid">
            <g id="Grid BoundingBox">...</g>
          </g>
          <g id="Axis (Height)">
            <g id="Axis Label (Height)">...</g>
            <g id="Axis Ticks (Height)">...</g>
            <g id="Axis Paralels (Height)">...</g>
          </g>
          <g id="Axis (Y)">...</g>
          <g id="Axis (X)">...</g>
          <g id="Terrain">
            <g id="Terrain Vector 1">...</g>
            <g id="Terrain Vector 2">...</g>
            ...
          </g>
          <g id="Terrain Base">...</g>
        </svg>
        """
        # Crear nuevo root
        new_root = etree.Element(
            '{http://www.w3.org/2000/svg}svg',
            attrib=old_root.attrib
        )
        
        # Preservar defs y metadata
        for child in old_root:
            tag = child.tag
            if 'defs' in tag or 'metadata' in tag:
                new_root.append(child)
        
        # Crear jerarquía Grid
        if classified['grid_bbox']:
            grid_group = etree.SubElement(new_root, 'g', id='Grid')
            bbox_group = etree.SubElement(grid_group, 'g', id='Grid BoundingBox')
            bbox_group.append(classified['grid_bbox'][0])
        
        # Crear jerarquía Axis Height
        if classified['axis_height']:
            axis_group = etree.SubElement(new_root, 'g', id='Axis (Height)')
            
            # Label
            height_labels = [l for axis, l in classified['labels'] if axis == 'height']
            if height_labels:
                label_group = etree.SubElement(axis_group, 'g', id='Axis Label (Height)')
                label_group.set('opacity', '0.8')
                self._add_label_content(label_group, height_labels[0])
            
            # Ticks y paralelas
            for i, elem in enumerate(classified['axis_height']):
                elem.set('id', f'Axis Element (Height) {i+1}')
                axis_group.append(elem)
        
        # Similar para Axis Y y Axis X...
        
        # Crear jerarquía Terrain
        if classified['terrain']:
            terrain_group = etree.SubElement(new_root, 'g', id='Terrain')
            for i, terrain_elem in enumerate(classified['terrain']):
                terrain_elem.set('id', f'Terrain Vector {i+1}')
                terrain_group.append(terrain_elem)
        
        return new_root
    
    def _add_label_content(self, label_group, original_label):
        """
        Preserva estructura correcta de labels (NO extraer paths)
        
        Estructura correcta:
        <g id="Axis Label (Height)" opacity="0.8">
          <g style="fill: #ffffff" transform="translate(...) rotate(...)">
            <defs>
              <path id="DejaVuSans-41" d="..."/>
              ...
            </defs>
            <use xlink:href="#DejaVuSans-41"/>
            <use xlink:href="#DejaVuSans-6c" transform="translate(...)"/>
            ...
          </g>
        </g>
        """
        # Extraer el <g> interno con transformaciones
        for g_child in original_label:
            if g_child.tag == '{http://www.w3.org/2000/svg}g':
                # Actualizar estilo a blanco
                style = g_child.get('style', '')
                style = style.replace('fill: #00ffff', 'fill: #ffffff')
                style = style.replace('fill:#00ffff', 'fill:#ffffff')
                # Remover opacity del style (lo ponemos en el grupo padre)
                style = style.replace('opacity: 0.35', '').replace('opacity:0.35', '')
                g_child.set('style', style.strip().rstrip(';'))
                
                # Añadir grupo completo (con defs y use)
                label_group.append(g_child)
```

### Preservación de Metadata

```python
def _add_svg_metadata(svg_path: str, visual_params: dict):
    """
    Inyecta metadata de parámetros como comentarios XML
    
    Args:
        svg_path: Ruta del SVG
        visual_params: Parámetros de renderizado
    """
    tree = etree.parse(svg_path)
    root = tree.getroot()
    
    # Crear comentario con parámetros
    metadata_text = "\n".join([
        f"{key}: {value}" 
        for key, value in visual_params.items()
    ])
    
    comment = etree.Comment(f"\nRender Parameters:\n{metadata_text}\n")
    
    # Insertar al principio
    root.insert(0, comment)
    
    # Guardar
    tree.write(svg_path, encoding='utf-8', xml_declaration=True)
```

---

## Renderizado y Exportación

### Renderizado 3D con Matplotlib

```python
def _render_terrain_to_axis(ax, generator, grid_opacity=0.35, **visual_params):
    """
    Renderiza terreno 3D en un eje matplotlib
    
    Args:
        ax: Axis 3D de matplotlib
        generator: TopographicMapGenerator con terreno
        grid_opacity: Opacidad del grid (0.0-1.0)
        **visual_params: Colores, estilos, etc.
    """
    terrain = generator.terrain
    width, height = generator.width, generator.height
    
    # Crear meshgrid
    x = np.linspace(0, width, width)
    y = np.linspace(0, height, height)
    X, Y = np.meshgrid(x, y)
    
    # Calcular niveles de contorno
    levels = _compute_levels(terrain)
    
    # Dibujar líneas de contorno "flotantes"
    for level in levels:
        # Contour3D crea líneas a altura constante
        ax.contour3D(
            X, Y, terrain,
            levels=[level],
            colors=visual_params.get('contour_color', '#ffffff'),
            linewidths=visual_params.get('line_width', 0.8),
            alpha=0.7
        )
    
    # Dibujar "pastel" base (superficie sólida)
    base_height = BASE_HEIGHT  # 2.0
    base_color = visual_params.get('base_color', '#8B4513')
    
    # Superficie inferior
    ax.plot_surface(
        X, Y, np.full_like(terrain, 0),
        color=base_color,
        alpha=0.8,
        shade=False
    )
    
    # Superficie superior (terreno real)
    ax.plot_surface(
        X, Y, terrain,
        color=base_color,
        alpha=0.6,
        shade=True
    )
    
    # Conectar bordes (paredes laterales)
    _draw_side_walls(ax, X, Y, terrain, base_color)
    
    # Configurar grid
    ax.grid(True, alpha=grid_opacity, color='#ffffff', linewidth=0.5)
    
    # Configurar límites
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_zlim(0, terrain.max() + 2)
    
    # Labels de ejes
    ax.set_xlabel('X', color='white')
    ax.set_ylabel('Y', color='white')
    ax.set_zlabel('Altura', color='white')
```

### Cálculo de Niveles de Contorno

```python
def _compute_levels(terrain, num_levels=12):
    """
    Calcula niveles de contorno inteligentemente
    
    Args:
        terrain: Heightmap numpy array
        num_levels: Número de niveles deseados
        
    Returns:
        list: Lista de alturas para contornos
    """
    min_h = float(terrain.min())
    max_h = float(terrain.max())
    
    # Caso especial: terreno plano
    if abs(max_h - min_h) < 0.1:
        # Crear niveles artificiales uniformes
        base = BASE_HEIGHT
        return [base + i * 0.5 for i in range(num_levels)]
    
    # Caso normal: distribución uniforme
    return np.linspace(min_h, max_h, num_levels).tolist()
```

---

## Validación de Parámetros

### Sistema de Validación Centralizado

**Archivo**: `src/controller/config.py`

```python
# Definición de parámetros con validación
TERRAIN_PARAMS = {
    'height_variation': {
        'type': float,
        'min': 0.0,
        'max': 100.0,
        'default': 50.0,
        'description': 'Variación de altura del terreno'
    },
    'terrain_roughness': {
        'type': float,
        'min': 0.1,
        'max': 2.0,
        'default': 0.5,
        'description': 'Rugosidad/detalle del terreno'
    },
    'seed': {
        'type': int,
        'min': 0,
        'max': 2147483647,  # Max int32
        'default': None,
        'description': 'Semilla para reproducibilidad'
    }
}

VISUAL_PARAMS = {
    'azimuth_angle': {
        'type': float,
        'min': 0.0,
        'max': 360.0,
        'default': 315.0,
        'description': 'Ángulo de rotación horizontal'
    },
    'elevation_angle': {
        'type': float,
        'min': 0.0,
        'max': 90.0,
        'default': 30.0,
        'description': 'Ángulo de elevación'
    },
    'grid_opacity': {
        'type': float,
        'min': 0.0,
        'max': 1.0,
        'default': 0.35,
        'description': 'Opacidad del grid (0=invisible, 1=opaco)'
    }
}

CRATER_PARAMS = {
    'crater_density': {
        'type': float,
        'min': 0.0,
        'max': 100.0,
        'default': 0.0,
        'description': 'Densidad de cráteres'
    }
}
```

### Función de Validación

```python
def validate_parameter(param_name: str, value, param_config: dict) -> any:
    """
    Valida un parámetro individual
    
    Args:
        param_name: Nombre del parámetro
        value: Valor a validar
        param_config: Configuración del parámetro
        
    Returns:
        Valor validado y convertido al tipo correcto
        
    Raises:
        ValueError: Si validación falla
    """
    # Convertir tipo
    expected_type = param_config.get('type', float)
    try:
        converted_value = expected_type(value)
    except (ValueError, TypeError):
        raise ValueError(
            f"{param_name} debe ser de tipo {expected_type.__name__}, "
            f"recibido {type(value).__name__}"
        )
    
    # Validar rango mínimo
    if 'min' in param_config:
        if converted_value < param_config['min']:
            raise ValueError(
                f"{param_name} debe ser >= {param_config['min']}, "
                f"recibido {converted_value}"
            )
    
    # Validar rango máximo
    if 'max' in param_config:
        if converted_value > param_config['max']:
            raise ValueError(
                f"{param_name} debe ser <= {param_config['max']}, "
                f"recibido {converted_value}"
            )
    
    return converted_value
```

---

## Testing

### Test de Modelo

**Archivo**: `tests/test_map_model.py`

```python
import pytest
from src.model.map_model import MapModel

class TestMapModel:
    """Tests para MapModel"""
    
    def setup_method(self):
        """Setup antes de cada test"""
        self.model = MapModel()
    
    def test_initialization(self):
        """Test de inicialización con valores por defecto"""
        assert self.model.height_variation == 50.0
        assert self.model.terrain_roughness == 0.5
        assert self.model.azimuth_angle == 315.0
    
    def test_validate_terrain_params_valid(self):
        """Test de validación con parámetros válidos"""
        params = {
            'height_variation': 75.0,
            'terrain_roughness': 1.2
        }
        validated = self.model.validate_terrain_params(params)
        
        assert validated['height_variation'] == 75.0
        assert validated['terrain_roughness'] == 1.2
    
    def test_validate_terrain_params_out_of_range(self):
        """Test de validación con parámetros fuera de rango"""
        params = {'height_variation': 150.0}  # max es 100.0
        
        with pytest.raises(ValueError) as exc_info:
            self.model.validate_terrain_params(params)
        
        assert "debe ser <=" in str(exc_info.value)
    
    def test_validate_unknown_parameter(self):
        """Test de rechazo de parámetros desconocidos"""
        params = {'unknown_param': 42}
        
        with pytest.raises(ValueError) as exc_info:
            self.model.validate_terrain_params(params)
        
        assert "Parámetro desconocido" in str(exc_info.value)
    
    def test_grid_opacity_range(self):
        """Test de validación de grid_opacity (0.0-1.0)"""
        # Válido
        valid_params = {'grid_opacity': 0.5}
        validated = self.model.validate_visual_params(valid_params)
        assert validated['grid_opacity'] == 0.5
        
        # Inválido (fuera de rango)
        invalid_params = {'grid_opacity': 1.5}
        with pytest.raises(ValueError):
            self.model.validate_visual_params(invalid_params)
```

### Test de Controlador

**Archivo**: `tests/test_map_controller.py`

```python
import pytest
from src.controller.map_controller import MapController

class TestMapController:
    """Tests para MapController"""
    
    def setup_method(self):
        """Setup antes de cada test"""
        self.controller = MapController()
    
    def test_update_parameters_success(self):
        """Test de actualización exitosa de parámetros"""
        params = {
            'height_variation': 80.0,
            'azimuth_angle': 45.0
        }
        
        result = self.controller.update_parameters(params)
        
        assert result['success'] is True
        assert self.controller.model.height_variation == 80.0
        assert self.controller.model.azimuth_angle == 45.0
    
    def test_update_parameters_invalid(self):
        """Test de actualización con parámetros inválidos"""
        params = {'height_variation': -10.0}  # negativo inválido
        
        result = self.controller.update_parameters(params)
        
        assert result['success'] is False
        assert "debe ser >=" in result['message']
    
    def test_generate_map_without_terrain(self):
        """Test de generación de mapa exitosa"""
        result = self.controller.generate_map()
        
        assert result['success'] is True
        assert 'preview' in result
        assert self.controller.generator.terrain is not None
```

### Test de Optimización SVG

**Archivo**: `tests/test_svg_optimizer.py`

```python
import pytest
import tempfile
import os
from src.utils.svg_optimizer import SVGOptimizer
from lxml import etree

class TestSVGOptimizer:
    """Tests para SVGOptimizer"""
    
    def setup_method(self):
        """Setup antes de cada test"""
        self.optimizer = SVGOptimizer()
    
    def test_classify_grid_bbox(self):
        """Test de clasificación de Grid BoundingBox (12 líneas)"""
        # Crear SVG de prueba con 12 líneas
        root = etree.fromstring('''
        <svg xmlns="http://www.w3.org/2000/svg">
          <g id="grid3d_0">
            <path d="M 0,0 L 100,0"/>
            <path d="M 0,0 L 0,100"/>
            <!-- ... 10 líneas más ... -->
          </g>
        </svg>
        ''')
        
        # Clasificar
        classified = self.optimizer._classify_elements(root)
        
        # Verificar
        assert len(classified['grid_bbox']) == 1
        assert classified['grid_bbox'][0].get('id') == 'grid3d_0'
    
    def test_label_detection(self):
        """Test de detección de labels (text_N children)"""
        root = etree.fromstring('''
        <svg xmlns="http://www.w3.org/2000/svg">
          <g id="axis3d_2">
            <g id="text_1">
              <g>
                <defs>
                  <path id="DejaVuSans-41" d="..."/>
                </defs>
                <use xlink:href="#DejaVuSans-41"/>
              </g>
            </g>
          </g>
        </svg>
        ''')
        
        classified = self.optimizer._classify_elements(root)
        
        # Debe detectarse como label, no como axis regular
        assert len(classified['labels']) == 1
        assert classified['labels'][0][0] == 'height'
    
    def test_optimize_svg_integration(self):
        """Test de integración completa"""
        # Crear SVG temporal de entrada
        input_svg = '''
        <svg xmlns="http://www.w3.org/2000/svg">
          <g id="grid3d_0">
            <path d="M 0,0 L 100,0"/>
            <!-- ... más paths ... -->
          </g>
          <g id="line2d_1">
            <path d="M 10,10 L 20,20"/>
          </g>
        </svg>
        '''
        
        input_fd, input_path = tempfile.mkstemp(suffix='.svg')
        output_fd, output_path = tempfile.mkstemp(suffix='.svg')
        
        try:
            # Escribir input
            with os.fdopen(input_fd, 'w', encoding='utf-8') as f:
                f.write(input_svg)
            os.close(output_fd)
            
            # Optimizar
            self.optimizer.optimize_svg(input_path, output_path)
            
            # Verificar output
            tree = etree.parse(output_path)
            root = tree.getroot()
            
            # Debe tener estructura reorganizada
            grid_group = root.find('.//[@id="Grid"]', root.nsmap)
            terrain_group = root.find('.//[@id="Terrain"]', root.nsmap)
            
            assert grid_group is not None
            assert terrain_group is not None
            
        finally:
            # Limpiar
            os.unlink(input_path)
            os.unlink(output_path)
```

---

## Patrones de Diseño

### Patrón MVC

```python
# MODELO - Gestión de estado puro
class MapModel:
    def __init__(self):
        self.state = {}
    
    def validate(self, params):
        # Lógica de validación pura
        pass

# VISTA - Presentación y rendering
class Visualization:
    def render(self, data):
        # Lógica de presentación
        pass

# CONTROLADOR - Coordinación
class MapController:
    def __init__(self):
        self.model = MapModel()
        self.view = Visualization()
    
    def handle_action(self, params):
        # Coordina modelo y vista
        validated = self.model.validate(params)
        self.view.render(validated)
```

### Patrón Strategy (Backends de Ruido)

```python
class NoiseStrategy:
    """Interfaz para estrategias de generación de ruido"""
    
    def generate(self, width, height, roughness, seed):
        raise NotImplementedError

class Perlin3DStrategy(NoiseStrategy):
    """Estrategia Perlin 3D para baja resolución"""
    
    def generate(self, width, height, roughness, seed):
        # Implementación Perlin 3D
        pass

class FBMStrategy(NoiseStrategy):
    """Estrategia fBm para alta resolución"""
    
    def generate(self, width, height, roughness, seed):
        # Implementación fBm vectorizada
        pass

class TerrainGenerator:
    def __init__(self):
        self.strategy = None
    
    def select_strategy(self, resolution):
        """Selecciona estrategia según resolución"""
        if resolution < 160000:
            self.strategy = Perlin3DStrategy()
        else:
            self.strategy = FBMStrategy()
    
    def generate(self, width, height, roughness, seed):
        self.select_strategy(width * height)
        return self.strategy.generate(width, height, roughness, seed)
```

### Patrón Template Method (Exportación)

```python
class Exporter:
    """Clase base para exportadores"""
    
    def export(self, data, filename):
        """Template method - define el flujo"""
        # 1. Preparar datos
        prepared = self.prepare_data(data)
        
        # 2. Crear archivo temporal si es necesario
        temp_path = self.create_temp_file()
        
        # 3. Renderizar
        self.render(prepared, temp_path or filename)
        
        # 4. Post-procesar
        if temp_path:
            self.post_process(temp_path, filename)
            self.cleanup(temp_path)
    
    def prepare_data(self, data):
        """Hook method - subclases pueden override"""
        return data
    
    def create_temp_file(self):
        """Hook method"""
        return None
    
    def render(self, data, path):
        """Abstract method - subclases DEBEN implementar"""
        raise NotImplementedError
    
    def post_process(self, temp_path, final_path):
        """Hook method"""
        pass
    
    def cleanup(self, temp_path):
        """Hook method"""
        pass

class SVGExporter(Exporter):
    """Exportador SVG con optimización"""
    
    def create_temp_file(self):
        fd, path = tempfile.mkstemp(suffix='.svg')
        os.close(fd)
        return path
    
    def render(self, data, path):
        # Renderizar con matplotlib
        plt.savefig(path, format='svg')
    
    def post_process(self, temp_path, final_path):
        # Optimizar estructura SVG
        optimizer = SVGOptimizer()
        optimizer.optimize_svg(temp_path, final_path)
    
    def cleanup(self, temp_path):
        os.unlink(temp_path)

class PNGExporter(Exporter):
    """Exportador PNG sin post-procesamiento"""
    
    def render(self, data, path):
        plt.savefig(path, format='png', dpi=300)
```

---

## Referencias Cruzadas

### Ver También

- **[INDEX.md](INDEX.md)** - Documentación principal y guías
- **[CHANGELOG.md](CHANGELOG.md)** - Historia completa de desarrollo
- **[architecture.md](architecture.md)** - Análisis arquitectónico detallado
- **[testing.md](testing.md)** - Estrategias de testing completas

### Enlaces Rápidos

- [Flujo de Generación](INDEX.md#flujo-de-datos)
- [Parámetros Configurables](configuration.md)
- [Solución de Problemas](troubleshooting.md)

---

**Última actualización**: Octubre 21, 2025
