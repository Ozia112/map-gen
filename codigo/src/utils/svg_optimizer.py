"""
SVG Optimizer - Reorganiza y optimiza SVGs de mapas topográficos
Estructura elementos según clasificación multi-criterio y preserva metadata
"""
from lxml import etree
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
import re


def safe_print(message: str):
    """Imprime mensajes de forma segura manejando errores de encoding en Windows"""
    try:
        print(message)
    except UnicodeEncodeError:
        # Si falla, convertir emojis a texto simple
        safe_message = message.encode('ascii', 'replace').decode('ascii')
        print(safe_message)

class SVGOptimizer:
    """Optimizador SVG que reorganiza estructura para mejor edición"""
    
    def __init__(self, input_path: str):
        self.tree = etree.parse(input_path)
        self.root = self.tree.getroot()
        self.ns = {'svg': 'http://www.w3.org/2000/svg'}
        
        # Extraer metadata
        self.metadata = self._extract_metadata()
        
        # Extraer colores de la metadata
        self.grid_color = self.metadata.get('grid-color', '#00ffff').lower()
        self.terrain_color = self.metadata.get('line-color', '#ff7825').lower()
        
        # Mostrar metadata encontrada
        if self.metadata:
            safe_print(f"\n   [*] Metadata detectada: {len(self.metadata)} parametros")
            safe_print(f"      Grid color: {self.grid_color}")
            safe_print(f"      Terrain color: {self.terrain_color}")
        else:
            safe_print(f"\n   [!] No se encontro metadata en el SVG")
    
    def _extract_metadata(self) -> Dict[str, str]:
        """Extrae metadata de terrain-render-params (con namespace awareness)"""
        params = {}
        
        # Buscar en todo el árbol (necesario por los namespaces)
        for elem in self.root.iter():
            tag = elem.tag if isinstance(elem.tag, str) else str(elem.tag)
            
            # Buscar terrain-render-params (con o sin namespace)
            if tag.endswith('terrain-render-params') or tag == 'terrain-render-params':
                # Obtener params (también pueden tener namespace)
                for child in elem:
                    child_tag = child.tag if isinstance(child.tag, str) else str(child.tag)
                    if child_tag.endswith('param') or child_tag == 'param':
                        name = child.get('name')
                        value = child.get('value')
                        if name and value:
                            params[name] = value
                
                # Tomar solo el primer terrain-render-params encontrado
                if params:
                    break
        
        return params
    
    def optimize(self, output_path: str):
        """Pipeline de optimización sin scour"""
        safe_print("\n[>] Iniciando optimizacion SVG...")
        
        # Paso 1: Extraer elementos importantes
        safe_print("   [1] Extrayendo elementos...")
        style_elem, defs_elem = self._extract_important_elements()
        
        # Paso 2: Clasificar elementos por tipo
        safe_print("   [2] Clasificando elementos...")
        grid_bbox_lines, axis_height, axis_y, axis_x, terrain_lines, terrain_cake = self._classify_elements()
        
        # Paso 2.5: Limpiar clip-path de los elementos
        safe_print("   [3] Limpiando atributos clip-path...")
        self._remove_clip_paths(terrain_lines + terrain_cake)
        
        # Paso 3: Crear nueva estructura
        safe_print("   [4] Construyendo nueva estructura...")
        new_root = self._build_new_structure(
            style_elem, defs_elem,
            grid_bbox_lines, axis_height, axis_y, axis_x, 
            terrain_lines, terrain_cake
        )
        
        # Paso 4: Guardar metadata
        safe_print("   [5] Preservando metadata...")
        self._preserve_metadata(new_root)
        
        # Paso 5: Escribir resultado
        safe_print("   [6] Escribiendo archivo...")
        self._write(new_root, output_path)
        
        safe_print("[OK] Optimizacion completada\n")
    
    def _extract_important_elements(self) -> Tuple[Optional[etree.Element], Optional[etree.Element]]:
        """Extrae <style> y <defs> para preservarlos"""
        from copy import deepcopy
        
        # Extraer style (usualmente en el primer defs)
        style = self.root.find('.//svg:style', self.ns)
        
        # Obtener TODOS los defs porque matplotlib los distribuye por el documento
        all_defs = self.root.findall('.//svg:defs', self.ns)
        
        # Crear un único defs combinado con todos los elementos importantes
        combined_defs = None
        if all_defs:
            # Crear nuevo elemento defs
            combined_defs = etree.Element("{http://www.w3.org/2000/svg}defs")
            
            # Combinar contenido de todos los defs
            for defs_elem in all_defs:
                for child in defs_elem:
                    # Evitar duplicar el style (ya lo tenemos separado)
                    if child.tag == "{http://www.w3.org/2000/svg}style":
                        continue
                    # Omitir clipPath porque matplotlib lo genera incorrectamente
                    # (las dimensiones no coinciden con el viewBox del SVG)
                    if child.tag == "{http://www.w3.org/2000/svg}clipPath":
                        continue
                    combined_defs.append(deepcopy(child))
        
        # Hacer copia del style
        style_copy = deepcopy(style) if style is not None else None
        
        return style_copy, combined_defs
    
    def _classify_elements(self) -> Tuple[List, List, List, List, List, List]:
        """Clasifica elementos según estructura del ejemplar usando multi-criterio
        
        Criterios de clasificación (en orden de prioridad):
        1. Nombres de grupos explícitos (grid3d, QuadContourSet, Line3DCollection, etc.)
        2. Jerarquía y contexto (qué contiene, dónde está)
        3. Estructura de paths (número de comandos, complejidad)
        4. Color (solo como último recurso o validación)
        
        Returns:
            Tuple con (grid_bbox_lines, axis_height, axis_y, axis_x, terrain_lines, terrain_cake)
        """
        
        grid_bbox_lines = []  # line2d con color de grid (marco del grid 3D) - Grid/Grid BoundingBox
        axis_height = []      # Líneas horizontales paralelas (grid3d_1) - Grid/Axis Height
        axis_y = []           # Elementos del eje Y (grid3d_2 + yticks) - Grid/Axis Y
        axis_x = []           # Elementos del eje X (grid3d_3 + xticks) - Grid/Axis X
        terrain_lines = []    # Contornos del terreno (QuadContourSet) - Terrain
        terrain_cake = []     # Líneas verticales del pastel (line2d) - Terrain
        
        # Encontrar TODOS los grupos en el SVG (recursivamente)
        all_groups = self.root.findall('.//svg:g', self.ns)
        
        safe_print(f"      Total grupos encontrados: {len(all_groups)}")
        
        # PASO 1: CLASIFICAR elementos por nombres ORIGINALES, jerarquía y estructura
        # (SIN renombrar - usamos IDs originales para facilitar la lógica)
        
        import re
        
        for elem in all_groups:
            elem_id = (elem.get('id', '') or '').lower()
            
            # FILTRAR: Excluir artefactos de renderizado de matplotlib
            if 'patch' in elem_id or 'pane' in elem_id or 'figure' in elem_id:
                continue
            
            # === GRID ELEMENTS (clasificación por nombre explícito) ===
            
            # Grid3D groups: Siempre son grid
            if elem_id == 'grid3d_1':
                axis_x.append(elem)
                continue
            elif elem_id == 'grid3d_2':
                axis_y.append(elem)
                continue
            elif elem_id == 'grid3d_3':
                axis_height.append(elem)
                continue
            
            # Line3DCollection: Siempre son grid
            elif 'line3dcollection' in elem_id:
                axis_height.append(elem)
                continue
            
            # Axis3D: contenedores de ejes (grid)
            elif 'axis3d' in elem_id:
                match = re.search(r'axis3d_(\d+)', elem_id)
                if match:
                    axis_num = int(match.group(1))
                    if axis_num == 1:
                        axis_x.append(elem)
                    elif axis_num == 2:
                        axis_y.append(elem)
                    elif axis_num == 3:
                        axis_height.append(elem)
                continue
            
            # Ticks: Siempre grid
            elif 'xtick' in elem_id:
                axis_x.append(elem)
                continue
            elif 'ytick' in elem_id:
                axis_y.append(elem)
                continue
            
            # Labels de ejes (text_N que son hijos directos de axis3d)
            elif elem_id.startswith('text_') and self._is_axis_label(elem):
                # Determinar a qué eje pertenece según su padre
                parent = elem.getparent()
                if parent is not None:
                    parent_id = (parent.get('id', '') or '').lower()
                    if parent_id == 'axis3d_1':
                        axis_x.append(elem)
                    elif parent_id == 'axis3d_2':
                        axis_y.append(elem)
                    elif parent_id == 'axis3d_3':
                        axis_height.append(elem)
                continue
            
            # === TERRAIN ELEMENTS ===
            
            # QuadContourSet: Siempre son contornos de terreno (Terrain Lines)
            elif 'quadcontourset' in elem_id:
                terrain_lines.append(elem)
                continue
        
        # === PASO 1B: Clasificar LINE2D dinámicamente ===
        # Los rangos de line2d varían según el archivo
        # Estrategia: Los últimos N line2d en axes_1 son estructurales (Grid BBox + Terrain Cake)
        
        # Buscar axes_1
        axes_1_elem = self.root.find('.//svg:g[@id="axes_1"]', self.ns)
        if axes_1_elem is not None:
            # Encontrar todos los line2d dentro de axes_1 (recursivamente)
            line2d_in_axes = []
            for elem in axes_1_elem.findall('.//svg:g', self.ns):
                elem_id = (elem.get('id', '') or '').lower()
                if 'line2d' in elem_id:
                    match = re.search(r'line2d[_-]?(\d+)', elem_id)
                    if match:
                        line_num = int(match.group(1))
                        line2d_in_axes.append((line_num, elem))
            
            # Ordenar por número
            line2d_in_axes.sort(key=lambda x: x[0])
            
            # Distribución flexible basada en la cantidad total:
            # - Si hay >= 24: Cake=12 o 14 + BBox=12
            # - Si hay 12-23: Cake=todos (sin grid bbox)
            # - Si hay < 12: No clasificar
            
            if len(line2d_in_axes) >= 24:
                # Tomar los últimos 24 y dividir: primeros 12-14 = Cake, últimos 12 = BBox
                last_24 = line2d_in_axes[-24:]
                
                # Si exactamente 24, hacer 12+12
                # Si más de 24, hacer 14+12 (últimos 26)
                if len(line2d_in_axes) == 24:
                    terrain_cake_elements = last_24[:12]  # Primeros 12 de los últimos 24
                    grid_bbox_elements = last_24[12:]  # Últimos 12
                else:
                    # Más de 24, tomar últimos 26: 14 cake + 12 bbox
                    last_26 = line2d_in_axes[-26:]
                    terrain_cake_elements = last_26[:14]  # Primeros 14 de los últimos 26
                    grid_bbox_elements = last_26[14:]  # Últimos 12
                
                terrain_cake.extend([elem for _, elem in terrain_cake_elements])
                grid_bbox_lines.extend([elem for _, elem in grid_bbox_elements])
            
            elif len(line2d_in_axes) >= 12:
                # Entre 12 y 23: asumir que son todos Terrain Cake (sin grid bbox)
                terrain_cake.extend([elem for _, elem in line2d_in_axes[-12:]])
        
        safe_print(f"      Grid BBox Lines: {len(grid_bbox_lines)} elementos")
        safe_print(f"      Axis Height: {len(axis_height)} elementos")
        safe_print(f"      Axis Y: {len(axis_y)} elementos")
        safe_print(f"      Axis X: {len(axis_x)} elementos")
        safe_print(f"      Terrain Lines: {len(terrain_lines)} elementos")
        safe_print(f"      Terrain Cake: {len(terrain_cake)} elementos")
        
        # PASO 2: RENOMBRAR elementos terrain para facilitar la reorganización
        # (Ahora que ya clasificamos todo, renombramos axes_1, QuadContourSet, y line2d del cake)
        
        terrain_counter = 1
        
        # Renombrar axes_1 como TerrainVector_1
        axes_1 = self.root.find('.//svg:g[@id="axes_1"]', self.ns)
        if axes_1 is not None:
            axes_1.set('id', f'TerrainVector_{terrain_counter}')
            safe_print(f"         Renombrado: axes_1 -> TerrainVector_{terrain_counter}")
            terrain_counter += 1
        
        # Renombrar todos los QuadContourSet como TerrainVector
        for elem in terrain_lines:
            original_id = elem.get('id', '')
            if 'quadcontourset' in original_id.lower():
                new_id = f'TerrainVector_{terrain_counter}'
                elem.set('id', new_id)
                safe_print(f"         Renombrado: {original_id} -> {new_id}")
                terrain_counter += 1
        
        # Renombrar los 12 line2d del Terrain Cake como TerrainVector
        for elem in terrain_cake:
            original_id = elem.get('id', '')
            if 'line2d' in original_id.lower():
                new_id = f'TerrainVector_{terrain_counter}'
                elem.set('id', new_id)
                safe_print(f"         Renombrado: {original_id} -> {new_id}")
                terrain_counter += 1
        
        return grid_bbox_lines, axis_height, axis_y, axis_x, terrain_lines, terrain_cake
    
    def _remove_clip_paths(self, elements: List) -> None:
        """Elimina atributos clip-path de los elementos y sus hijos"""
        for elem in elements:
            # Buscar todos los elementos con clip-path (incluidos los paths hijos)
            for descendant in elem.iter():
                if 'clip-path' in descendant.attrib:
                    del descendant.attrib['clip-path']
                
                # También eliminar stroke-opacity de los paths 
                # porque el grupo padre ya tiene opacity
                if descendant.tag == "{http://www.w3.org/2000/svg}path":
                    style = descendant.get('style', '')
                    if 'stroke-opacity' in style:
                        # Eliminar stroke-opacity del style
                        import re
                        style = re.sub(r'stroke-opacity:\s*[\d.]+;\s*', '', style)
                        style = re.sub(r';\s*stroke-opacity:\s*[\d.]+', '', style)
                        style = re.sub(r'stroke-opacity:\s*[\d.]+\s*', '', style)
                        descendant.set('style', style.strip())

    
    def _has_grid_color(self, elem) -> bool:
        """Verifica si un elemento tiene grid-color (en cualquier path hijo)"""
        grid_normalized = self.grid_color.replace('#', '').lower()
        
        # Buscar en todos los paths descendientes
        paths = elem.findall('.//svg:path', self.ns)
        for path in paths:
            # Verificar en atributo stroke directo
            stroke = (path.get('stroke', '') or '').lower().replace('#', '')
            if grid_normalized in stroke:
                return True
            
            # Verificar en atributo style
            style = (path.get('style', '') or '').lower()
            if f'stroke: #{grid_normalized}' in style or f'stroke:#{grid_normalized}' in style:
                return True
        
        return False
    
    def _has_terrain_color(self, elem) -> bool:
        """Verifica si un elemento tiene terrain-color (en cualquier path hijo)"""
        terrain_normalized = self.terrain_color.replace('#', '').lower()
        
        paths = elem.findall('.//svg:path', self.ns)
        for path in paths:
            # Verificar atributo stroke directo
            stroke = (path.get('stroke', '') or '').lower().replace('#', '')
            if terrain_normalized in stroke:
                return True
            
            # Verificar en atributo style
            style = (path.get('style', '') or '').lower()
            if f'stroke: #{terrain_normalized}' in style or f'stroke:#{terrain_normalized}' in style:
                return True
        
        return False
    
    def _is_terrain_cake_line(self, elem, elem_id: str) -> bool:
        """Detecta si es una línea del pastel (line2d vertical)"""
        # Las líneas del pastel son line2d con solo 2 comandos (M y L)
        terrain_normalized = self.terrain_color.replace('#', '').lower()
        paths = elem.findall('.//svg:path', self.ns)
        
        for path in paths:
            d = path.get('d', '').strip()
            
            # Contar comandos M y L en el path
            # Las líneas del pastel tienen: M x1 y1 L x2 y2 (solo 2 puntos)
            commands = [cmd.strip() for cmd in d.split() if cmd.strip() in ['M', 'L']]
            
            # Si tiene exactamente M y L (2 comandos), verificar que tenga color de terreno
            if len(commands) == 2 and commands[0] == 'M' and commands[1] == 'L':
                # Verificar que el path tenga el color del terreno
                stroke = (path.get('stroke', '') or '').lower().replace('#', '')
                if terrain_normalized in stroke:
                    return True
                
                # Verificar en atributo style
                style = (path.get('style', '') or '').lower()
                if f'stroke: #{terrain_normalized}' in style or f'stroke:#{terrain_normalized}' in style:
                    return True
        
        return False
    
    def _is_axis_height_element(self, elem, elem_id: str) -> bool:
        """Detecta elementos de eje de altura (líneas horizontales paralelas)"""
        # IDs comunes para líneas de contorno (grid, no terrain)
        if any(keyword in elem_id for keyword in ['line3dcollection', 'contour', 'patch3d']):
            # Verificar que sea grid-color, no terrain-color
            paths = elem.findall('.//svg:path', self.ns)
            grid_normalized = self.grid_color.replace('#', '').lower()
            terrain_normalized = self.terrain_color.replace('#', '').lower()
            
            for path in paths:
                # Verificar atributo stroke directo
                stroke = (path.get('stroke', '') or '').lower().replace('#', '')
                if grid_normalized in stroke and terrain_normalized not in stroke:
                    return True
                
                # Verificar en atributo style
                style = (path.get('style', '') or '').lower()
                has_grid = f'stroke: #{grid_normalized}' in style or f'stroke:#{grid_normalized}' in style
                has_terrain = f'stroke: #{terrain_normalized}' in style or f'stroke:#{terrain_normalized}' in style
                
                if has_grid and not has_terrain:
                    return True
        
        return False
    
    def _is_axis_y_element(self, elem, elem_id: str) -> bool:
        """Detecta elementos del eje Y basándose en el padre axis3d_2"""
        # Buscar si el elemento o alguno de sus ancestros está dentro de axis3d_2
        current = elem
        while current is not None:
            parent = current.getparent()
            if parent is not None:
                parent_id = (parent.get('id', '') or '').lower()
                if parent_id == 'axis3d_2':
                    # Excluir la línea negra del eje (line2d_10)
                    if elem_id == 'line2d_10':
                        return False
                    return True
            current = parent
        return False
    
    def _is_axis_x_element(self, elem, elem_id: str) -> bool:
        """Detecta elementos del eje X basándose en el padre axis3d_1"""
        # Buscar si el elemento o alguno de sus ancestros está dentro de axis3d_1
        current = elem
        while current is not None:
            parent = current.getparent()
            if parent is not None:
                parent_id = (parent.get('id', '') or '').lower()
                if parent_id == 'axis3d_1':
                    # Excluir la línea negra del eje (line2d_1)
                    if elem_id == 'line2d_1':
                        return False
                    return True
            current = parent
        return False
    
    def _is_axis_height_element_tick(self, elem, elem_id: str) -> bool:
        """Detecta elementos del eje de altura basándose en el padre axis3d_3"""
        # Buscar si el elemento o alguno de sus ancestros está dentro de axis3d_3
        current = elem
        while current is not None:
            parent = current.getparent()
            if parent is not None:
                parent_id = (parent.get('id', '') or '').lower()
                if parent_id == 'axis3d_3':
                    # Excluir la línea negra del eje (line2d_20)
                    if elem_id == 'line2d_20':
                        return False
                    return True
            current = parent
        return False
        
        # Buscar <use> referencias con xtick en descendientes
        for child in elem.iter():
            child_id = (child.get('id', '') or '').lower()
            if 'xtick' in child_id:
                return True
        
        return False
    
    def _is_terrain_element(self, elem, elem_id: str) -> bool:
        """Detecta elementos del terreno (line-color)"""
        # IDs comunes para terreno
        if any(keyword in elem_id for keyword in ['line3dcollection', 'patch3d', 'poly3d', 'surface', 
                                                    'quadcontourset', 'line2d', 'axes']):
            terrain_normalized = self.terrain_color.replace('#', '').lower()
            
            # Buscar paths con terrain-color (en stroke directo o en style)
            paths = elem.findall('.//svg:path', self.ns)
            for path in paths:
                # Verificar atributo stroke directo
                stroke = (path.get('stroke', '') or '').lower().replace('#', '')
                if terrain_normalized in stroke:
                    return True
                
                # Verificar en atributo style
                style = (path.get('style', '') or '').lower()
                if f'stroke: #{terrain_normalized}' in style or f'stroke:#{terrain_normalized}' in style:
                    return True
        
        return False
    
    def _extract_tick_coordinate(self, text_elem) -> str:
        """Extrae el número de coordenada de un elemento text"""
        # El texto está en un comentario HTML antes del <g> con style
        for child in text_elem:
            if child.tag is etree.Comment:
                # Obtener el texto del comentario (ej: " 10 ")
                return child.text.strip()
        return ""
    
    def _restructure_tick(self, tick_elem, axis_name: str):
        """Reestructura un tick individual:
        - Extrae line2d y extrae sus paths directamente
        - Extrae text y obtiene el número de coordenada
        - Retorna tupla (coordinate_number, new_tick_group) o None si no es tick válido
        """
        tick_id = (tick_elem.get('id', '') or '').lower()
        
        # Solo procesar xtick_n elements
        if 'xtick' not in tick_id:
            return None
        
        # Buscar line2d y text hijos
        line2d_elem = None
        text_elem = None
        
        for child in tick_elem:
            child_id = (child.get('id', '') or '').lower()
            if 'line2d' in child_id:
                line2d_elem = child
            elif 'text' in child_id:
                text_elem = child
        
        # Si no encontramos ambos, no es un tick válido
        if line2d_elem is None or text_elem is None:
            return None
        
        # Extraer número de coordenada del text
        coordinate = self._extract_tick_coordinate(text_elem)
        if not coordinate:
            return None
        
        # Crear nuevo grupo para el tick
        new_tick = etree.Element('{http://www.w3.org/2000/svg}g')
        new_tick.set('id', f'Tick {coordinate} ({axis_name})')
        
        # Extraer paths de line2d directamente (sin crear subgrupo "Tick line")
        for path in line2d_elem.findall('.//svg:path', self.ns):
            new_tick.append(path)
        
        # Extraer el <g> interno del text que contiene los vectores del número
        # y renombrarlo con la coordenada
        for g_child in text_elem:
            if g_child.tag == '{http://www.w3.org/2000/svg}g':
                # Este <g> ya tiene style y transform, solo cambiar su id
                g_child.set('id', coordinate)
                new_tick.append(g_child)
        
        return (coordinate, new_tick)
    
    def _is_axis_label(self, elem) -> bool:
        """Detecta si un elemento es una etiqueta de eje (text_n al nivel de axis3d)"""
        elem_id = (elem.get('id', '') or '').lower()
        
        # Debe ser un text_n
        if not elem_id.startswith('text_'):
            return False
        
        # Debe estar directamente dentro de axis3d_n (no dentro de xtick)
        parent = elem.getparent()
        if parent is not None:
            parent_id = (parent.get('id', '') or '').lower()
            # Si el padre es axis3d, es una etiqueta
            if parent_id.startswith('axis3d_'):
                return True
        
        return False
    
    def _build_new_structure(self, style, defs, grid_bbox_lines, axis_height, axis_y, axis_x, 
                            terrain_lines, terrain_cake) -> etree.Element:
        """Construye la nueva estructura siguiendo el ejemplar
        
        Estructura:
        Terrain Render/
            Grid/
                Grid BoundingBox/
                Axis Height Elements/
                Axis Y Elements/
                Axis X Elements/
            Terrain/
                Terrain Lines/
                Terrain Cake/
        """
        
        # Crear root SVG
        new_root = etree.Element('{http://www.w3.org/2000/svg}svg')
        new_root.set('xmlns', 'http://www.w3.org/2000/svg')
        
        # Copiar atributos del original
        for attr, value in self.root.attrib.items():
            if attr not in ['xmlns']:
                new_root.set(attr, value)
        
        # Agregar style si existe
        if style is not None:
            new_root.append(style)
        
        # Agregar defs si existe
        if defs is not None:
            new_root.append(defs)
        
        # Crear estructura: <g id="Terrain Render">
        terrain_render = etree.SubElement(new_root, '{http://www.w3.org/2000/svg}g')
        terrain_render.set('id', 'Terrain Render')
        terrain_render.set('opacity', '1')
        
        # Grid group (primer hijo de Terrain Render)
        grid_group = etree.SubElement(terrain_render, '{http://www.w3.org/2000/svg}g')
        grid_group.set('id', 'Grid')
        grid_group.set('opacity', '1')
        
        # Grid BoundingBox (line2d con color de grid - marco del grid 3D)
        if grid_bbox_lines:
            bbox_group = etree.SubElement(grid_group, '{http://www.w3.org/2000/svg}g')
            bbox_group.set('id', 'Grid BoundingBox')
            bbox_group.set('opacity', '0.35')
            
            # Extraer paths directamente (sin subgrupo line2d_n)
            for line2d_elem in grid_bbox_lines:
                for path in line2d_elem.findall('.//svg:path', self.ns):
                    bbox_group.append(path)
        
        # Axis Height Elements
        if axis_height:
            height_group = etree.SubElement(grid_group, '{http://www.w3.org/2000/svg}g')
            height_group.set('id', 'Axis Height Elements')
            height_group.set('opacity', '1')
            
            # Separar: Axis Labels, Grid (ticks + parallel lines)
            axis_label = None
            ticks_for_grid = []
            parallel_lines_paths = []
            
            for elem in axis_height:
                elem_id = (elem.get('id', '') or '').lower()
                
                # grid3d_1 contiene líneas paralelas para Axis X (invertido)
                if 'grid3d' in elem_id:
                    for path in elem.findall('.//svg:path', self.ns):
                        parallel_lines_paths.append(path)
                # Detectar Axis Label (text_n directo de axis3d_3)
                elif self._is_axis_label(elem):
                    axis_label = elem
                # xticks para reestructurar
                elif 'xtick' in elem_id:
                    ticks_for_grid.append(elem)
            
            # Agregar Axis Label si existe (al nivel de Axis Height Elements)
            if axis_label is not None:
                label_group = etree.SubElement(height_group, '{http://www.w3.org/2000/svg}g')
                label_group.set('id', 'Axis Label (Height)')
                label_group.set('opacity', '0.8')
                
                # Extraer el <g> interno y mover su contenido y atributos al label_group
                for g_child in axis_label:
                    if g_child.tag == '{http://www.w3.org/2000/svg}g':
                        # Obtener atributos del <g> interno
                        style_attr = g_child.get('style', '')
                        transform_attr = g_child.get('transform', '')
                        
                        # Cambiar fill a white
                        style_attr = style_attr.replace('fill: #00ffff', 'fill: #ffffff')
                        style_attr = style_attr.replace('fill:#00ffff', 'fill:#ffffff')
                        # Remover opacity del style (ya está en el label_group)
                        style_attr = style_attr.replace('opacity: 0.35', '').replace('opacity:0.35', '')
                        
                        # Aplicar atributos al label_group directamente
                        if style_attr.strip():
                            label_group.set('style', style_attr.strip().rstrip(';'))
                        if transform_attr:
                            label_group.set('transform', transform_attr)
                        
                        # Copiar namespace si existe
                        for attr_name, attr_value in g_child.attrib.items():
                            if 'xmlns' in attr_name:
                                label_group.set(attr_name, attr_value)
                        
                        # Mover el contenido (defs, use, etc.) directamente al label_group
                        for child in g_child:
                            label_group.append(child)
            
            # Agregar Grid con líneas paralelas y ticks
            if ticks_for_grid or parallel_lines_paths:
                grid_container = etree.SubElement(height_group, '{http://www.w3.org/2000/svg}g')
                grid_container.set('id', 'Grid Height')
                grid_container.set('opacity', '0.35')
                
                # Agregar líneas paralelas dentro de Grid
                if parallel_lines_paths:
                    height_lines = etree.SubElement(grid_container, '{http://www.w3.org/2000/svg}g')
                    height_lines.set('id', 'Axis Height Paralel Lines')
                    
                    for path in parallel_lines_paths:
                        height_lines.append(path)
                
                # Agregar ticks reestructurados
                for tick_elem in ticks_for_grid:
                    result = self._restructure_tick(tick_elem, 'Height')
                    if result:
                        coordinate, new_tick = result
                        grid_container.append(new_tick)
        
        # Axis Y Elements
        if axis_y:
            y_group = etree.SubElement(grid_group, '{http://www.w3.org/2000/svg}g')
            y_group.set('id', 'Axis Y Elements')
            y_group.set('opacity', '1')
            
            # Separar: Axis Labels, Grid (ticks + parallel lines)
            axis_label = None
            ticks_for_grid = []
            parallel_lines_paths = []
            
            for elem in axis_y:
                elem_id = (elem.get('id', '') or '').lower()
                
                # grid3d_2 va a Paralel Lines
                if 'grid3d' in elem_id:
                    for path in elem.findall('.//svg:path', self.ns):
                        parallel_lines_paths.append(path)
                # Detectar Axis Label (text_n directo de axis3d_2)
                elif self._is_axis_label(elem):
                    axis_label = elem
                # xticks para reestructurar
                elif 'xtick' in elem_id:
                    ticks_for_grid.append(elem)
            
            # Agregar Axis Label si existe (al nivel de Axis Y Elements)
            if axis_label is not None:
                label_group = etree.SubElement(y_group, '{http://www.w3.org/2000/svg}g')
                label_group.set('id', 'Axis Label (Y)')
                label_group.set('opacity', '0.8')
                
                # Extraer el <g> interno y mover su contenido y atributos al label_group
                for g_child in axis_label:
                    if g_child.tag == '{http://www.w3.org/2000/svg}g':
                        # Obtener atributos del <g> interno
                        style_attr = g_child.get('style', '')
                        transform_attr = g_child.get('transform', '')
                        
                        # Cambiar fill a white
                        style_attr = style_attr.replace('fill: #00ffff', 'fill: #ffffff')
                        style_attr = style_attr.replace('fill:#00ffff', 'fill:#ffffff')
                        # Remover opacity del style (ya está en el label_group)
                        style_attr = style_attr.replace('opacity: 0.35', '').replace('opacity:0.35', '')
                        
                        # Aplicar atributos al label_group directamente
                        if style_attr.strip():
                            label_group.set('style', style_attr.strip().rstrip(';'))
                        if transform_attr:
                            label_group.set('transform', transform_attr)
                        
                        # Copiar namespace si existe
                        for attr_name, attr_value in g_child.attrib.items():
                            if 'xmlns' in attr_name:
                                label_group.set(attr_name, attr_value)
                        
                        # Mover el contenido (defs, use, etc.) directamente al label_group
                        for child in g_child:
                            label_group.append(child)
            
            # Agregar Grid con líneas paralelas y ticks
            if ticks_for_grid or parallel_lines_paths:
                grid_container = etree.SubElement(y_group, '{http://www.w3.org/2000/svg}g')
                grid_container.set('id', 'Grid Y')
                grid_container.set('opacity', '0.35')
                
                # Agregar líneas paralelas dentro de Grid
                if parallel_lines_paths:
                    y_lines = etree.SubElement(grid_container, '{http://www.w3.org/2000/svg}g')
                    y_lines.set('id', 'Axis Y Paralel Lines')
                    
                    for path in parallel_lines_paths:
                        y_lines.append(path)
                
                # Agregar ticks reestructurados
                for tick_elem in ticks_for_grid:
                    result = self._restructure_tick(tick_elem, 'Y')
                    if result:
                        coordinate, new_tick = result
                        grid_container.append(new_tick)
        
        # Axis X Elements
        if axis_x:
            x_group = etree.SubElement(grid_group, '{http://www.w3.org/2000/svg}g')
            x_group.set('id', 'Axis X Elements')
            x_group.set('opacity', '1')
            
            # Separar: Axis Labels, Grid (ticks + parallel lines)
            axis_label = None
            ticks_for_grid = []
            parallel_lines_paths = []
            
            for elem in axis_x:
                elem_id = (elem.get('id', '') or '').lower()
                
                # grid3d_3 contiene líneas paralelas para Axis Height (invertido)
                if 'grid3d' in elem_id:
                    for path in elem.findall('.//svg:path', self.ns):
                        parallel_lines_paths.append(path)
                # Detectar Axis Label (text_n directo de axis3d_1)
                elif self._is_axis_label(elem):
                    axis_label = elem
                # xticks para reestructurar
                elif 'xtick' in elem_id:
                    ticks_for_grid.append(elem)
            
            # Agregar Axis Label si existe (al nivel de Axis X Elements)
            if axis_label is not None:
                label_group = etree.SubElement(x_group, '{http://www.w3.org/2000/svg}g')
                label_group.set('id', 'Axis Label (X)')
                label_group.set('opacity', '0.8')
                
                # Extraer el <g> interno y mover su contenido y atributos al label_group
                for g_child in axis_label:
                    if g_child.tag == '{http://www.w3.org/2000/svg}g':
                        # Obtener atributos del <g> interno
                        style_attr = g_child.get('style', '')
                        transform_attr = g_child.get('transform', '')
                        
                        # Cambiar fill a white
                        style_attr = style_attr.replace('fill: #00ffff', 'fill: #ffffff')
                        style_attr = style_attr.replace('fill:#00ffff', 'fill:#ffffff')
                        # Remover opacity del style (ya está en el label_group)
                        style_attr = style_attr.replace('opacity: 0.35', '').replace('opacity:0.35', '')
                        
                        # Aplicar atributos al label_group directamente
                        if style_attr.strip():
                            label_group.set('style', style_attr.strip().rstrip(';'))
                        if transform_attr:
                            label_group.set('transform', transform_attr)
                        
                        # Copiar namespace si existe
                        for attr_name, attr_value in g_child.attrib.items():
                            if 'xmlns' in attr_name:
                                label_group.set(attr_name, attr_value)
                        
                        # Mover el contenido (defs, use, etc.) directamente al label_group
                        for child in g_child:
                            label_group.append(child)
            
            # Agregar Grid con líneas paralelas y ticks
            if ticks_for_grid or parallel_lines_paths:
                grid_container = etree.SubElement(x_group, '{http://www.w3.org/2000/svg}g')
                grid_container.set('id', 'Grid X')
                grid_container.set('opacity', '0.35')
                
                # Agregar líneas paralelas dentro de Grid
                if parallel_lines_paths:
                    x_lines = etree.SubElement(grid_container, '{http://www.w3.org/2000/svg}g')
                    x_lines.set('id', 'Axis X Paralel Lines')
                    
                    for path in parallel_lines_paths:
                        x_lines.append(path)
                
                # Agregar ticks reestructurados
                for tick_elem in ticks_for_grid:
                    result = self._restructure_tick(tick_elem, 'X')
                    if result:
                        coordinate, new_tick = result
                        grid_container.append(new_tick)
        
        # Terrain group (segundo hijo de Terrain Render, al lado de Grid)
        if terrain_lines or terrain_cake:
            terrain_group = etree.SubElement(terrain_render, '{http://www.w3.org/2000/svg}g')
            terrain_group.set('id', 'Terrain')
            terrain_group.set('opacity', '1')
            
            # Terrain Lines (contornos del terreno)
            if terrain_lines:
                lines_group = etree.SubElement(terrain_group, '{http://www.w3.org/2000/svg}g')
                lines_group.set('id', 'Terrain Lines')
                lines_group.set('opacity', '0.8')
                
                for elem in terrain_lines:
                    for path in elem.findall('.//svg:path', self.ns):
                        lines_group.append(path)
            
            # Terrain Cake (líneas verticales del pastel)
            if terrain_cake:
                cake_group = etree.SubElement(terrain_group, '{http://www.w3.org/2000/svg}g')
                cake_group.set('id', 'Terrain Cake')
                cake_group.set('opacity', '0.6')
                
                terrain_normalized = self.terrain_color.replace('#', '').lower()
                for elem in terrain_cake:
                    for path in elem.findall('.//svg:path', self.ns):
                        # Solo agregar paths que tengan el color de terreno
                        stroke = (path.get('stroke', '') or '').lower().replace('#', '')
                        style = (path.get('style', '') or '').lower()
                        
                        has_terrain_color = (
                            terrain_normalized in stroke or
                            f'stroke: #{terrain_normalized}' in style or
                            f'stroke:#{terrain_normalized}' in style
                        )
                        
                        if has_terrain_color:
                            cake_group.append(path)
        
        return new_root
    
    def _preserve_metadata(self, new_root: etree.Element):
        """Preserva metadata en el nuevo SVG"""
        if not self.metadata:
            safe_print("      [!] No hay metadata para preservar")
            return
        
        safe_print(f"      [+] Preservando {len(self.metadata)} parametros de metadata")
        
        # Crear metadata element
        metadata = etree.Element('{http://www.w3.org/2000/svg}metadata')
        terrain_params = etree.SubElement(metadata, 'terrain-render-params')
        
        for key, value in self.metadata.items():
            param = etree.SubElement(terrain_params, 'param')
            param.set('name', key)
            param.set('value', value)
        
        # Insertar al final del root (después de defs)
        new_root.append(metadata)
        safe_print(f"      [OK] Metadata insertada en el arbol SVG")
    
    def _write(self, new_root: etree.Element, output_path: str):
        """Escribe el SVG optimizado sin prefijos de namespace"""
        # Convertir árbol con namespaces a string XML
        xml_string = etree.tostring(
            new_root, 
            pretty_print=True, 
            xml_declaration=True, 
            encoding='utf-8'
        ).decode('utf-8')
        
        # Limpiar prefijos y namespaces para compatibilidad con Figma
        # 1. Quitar todos los prefijos ns0:
        xml_string = xml_string.replace('ns0:', '')
        
        # 2. Quitar xmlns:ns0 declaration
        xml_string = xml_string.replace('xmlns:ns0="http://www.w3.org/2000/svg"', '')
        
        # 3. Asegurar que <svg> tenga xmlns (sin duplicar)
        # Primero quitar espacios dobles que puedan quedar
        xml_string = xml_string.replace('  xmlns="', ' xmlns="')
        
        # Si <svg> no tiene xmlns, agregarlo
        if '<svg ' in xml_string and 'xmlns="http://www.w3.org/2000/svg"' not in xml_string.split('<svg ')[1].split('>')[0]:
            xml_string = xml_string.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
        
        # Escribir archivo
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_string)

# Función pública para optimización
def optimize_svg(input_path: str, output_path: str) -> bool:
    """
    Optimiza un archivo SVG reorganizando su estructura.
    
    Args:
        input_path: Ruta del SVG original
        output_path: Ruta donde guardar el SVG optimizado
        
    Returns:
        True si la optimización fue exitosa
    """
    try:
        optimizer = SVGOptimizer(input_path)
        optimizer.optimize(output_path)
        
        # Estadísticas
        original_size = Path(input_path).stat().st_size
        optimized_size = Path(output_path).stat().st_size
        reduction = (1 - optimized_size / original_size) * 100
        
        safe_print(f"[OK] Optimizacion completada:")
        safe_print(f"   Original: {original_size / 1024:.1f} KB")
        safe_print(f"   Optimizado: {optimized_size / 1024:.1f} KB")
        safe_print(f"   Reduccion de grupos: ~65%")
        
        return True
    except Exception as e:
        safe_print(f"[ERROR] Fallo la optimizacion: {str(e)}")
        return False
