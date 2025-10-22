import os
import sys
from typing import Optional, Dict, Any

# Asegurar que el directorio src esté en el path
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller.terrain_generator import TopographicMapGenerator
from controller.config import (
    TERRAIN_PARAMS,
    VISUAL_PARAMS,
    CRATER_PARAMS,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT
)

class MapModel:
    """
    Model class that encapsulates the state of the topographic map and their generator.
    Responsible for:
    - Storing and updating terrain and visual parameters.
    - Validating changes to parameters.
    - Coordinating the terrain generation process.
    """
    def __init__(self, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT):
        # Deep copy of default parameters to avoid mutation
        self.terrain_params = TERRAIN_PARAMS.copy()  # Initialize terrain parameters
        self.visual_params = VISUAL_PARAMS.copy()    # Initialize visual parameters
        self.crater_params = CRATER_PARAMS.copy()    # Initialize crater parameters

        # Initialize the terrain generator
        self._generator = TopographicMapGenerator(width, height)

        # Internal state
        self._last_heightmap: Optional[Any] = None
    
    @property
    def generator(self) -> TopographicMapGenerator:
        """Acces to the generator"""
        return self._generator
    
    @property
    def heightmap(self):
        """Last generated heightmap"""
        return self._last_heightmap
    
    #================ Parameters update ======================

    def update_terrain_params(self, **kwargs) -> Dict[str, Any]:
        """
        Update parameters of terrain with validation.

        Args:
            **kwargs: Terrain parameters to update (vh, roughness, seed, etc.)
        
        Returns:
            Dict[str, Any]: Updated terrain parameters.

        Raises:
            ValueError: If any parameter is invalid.
        """
        validated = self._validate_terrain_params(kwargs)
        # Also include alias keys expected by legacy/tests
        result = dict(validated)
        if 'height_variation' in validated:
            result['vh'] = validated['height_variation']
        if 'terrain_roughness' in validated:
            result['roughness'] = validated['terrain_roughness']
        # Persist both canonical and alias keys
        self.terrain_params.update(result)
        return result
        
    def update_visual_params(self, **kwargs) -> Dict[str, Any]:
        """
        Update parameters of visual with validation.

        Args:
            **kwargs: Visual parameters to update (line density, line_color, etc.)

        Returns:
            Dict with updated parameters
        
        Raises:
            ValueError: If any parameter is invalid
        """
        validated = self._validate_visual_params(kwargs)
        # Also include alias keys expected by legacy/tests
        result = dict(validated)
        if 'azimuth_angle' in validated:
            result['azimuth'] = validated['azimuth_angle']
        if 'elevation_angle' in validated:
            result['elevation'] = validated['elevation_angle']
        self.visual_params.update(result)
        return result
    
    def update_crater_params(self, **kwargs) -> Dict[str, Any]:
        """
        Update crater paramters with validation.

        Args:
            **kwargs: Crater parameters to update (enabled, density, size,  depth).

        Returns:
            Dict with validated parameters
        """
        validated = self._validate_crater_params(kwargs)
        self.crater_params.update(validated)
        return validated
    
    # =============== VALIDATION ========================
       
    def _validate_terrain_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters of terrain"""
        validated = {}

        # Backward compat: allow 'vh' and 'roughness'
        if 'vh' in params and 'height_variation' not in params:
            params = dict(params)
            params['height_variation'] = params.pop('vh')

        if 'height_variation' in params:
            vh = float(params['height_variation'])
            if not 0 <= vh <= 20:
                # Match tests message for 'vh'
                raise ValueError(f"vh debe estar entre 0 y 20")
            validated['height_variation'] = vh

        if 'roughness' in params and 'terrain_roughness' not in params:
            params = dict(params)
            params['terrain_roughness'] = params.pop('roughness')

        if 'terrain_roughness' in params:
            roughness = int(params['terrain_roughness'])
            if not 0 <= roughness <= 100:
                # Match tests message for 'roughness'
                raise ValueError("roughness debe estar entre 0 y 100")
            validated['terrain_roughness'] = roughness

        if 'base_height' in params:
            base_h = float(params['base_height'])
            if not 5.0 <= base_h <= 30.0:
                raise ValueError(f"base_height debe estar entre 5.0 y 30.0, recibido: {base_h}")
            validated['base_height'] = base_h

        if 'seed' in params:
            seed = int(params['seed'])
            if seed < 1:
                raise ValueError(f"seed debe ser positivo, recibido: {seed}")
            validated['seed'] = seed
            return validated
        
        return validated
    
    def _validate_visual_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters of visual"""
        validated = {}

        # Backward compat: support 'azimuth' and 'elevation' aliases
        if 'azimuth' in params and 'azimuth_angle' not in params:
            params = dict(params)
            params['azimuth_angle'] = params.pop('azimuth')
        if 'elevation' in params and 'elevation_angle' not in params:
            params = dict(params)
            params['elevation_angle'] = params.pop('elevation')

        if 'line_color' in params:
            color = params['line_color']
            if not isinstance(color, str) or not color.startswith('#'):
                # Match tests error substring
                raise ValueError("line_color debe ser un color hexadecimal")
            validated['line_color'] = color

        if 'azimuth_angle' in params:
            az = float(params['azimuth_angle'])
            validated['azimuth_angle'] = az % 360  # Normalize to [0, 360)

        if 'elevation_angle' in params:
            el = float(params['elevation_angle'])
            if not 0 <= el <= 90:
                # Match tests message
                raise ValueError("elevation debe estar entre 0 y 90")
            validated['elevation_angle'] = el
        
        if 'num_contour_levels' in params:
            levels = int(params['num_contour_levels'])
            if not 10 <= levels <= 40:
                raise ValueError(f"num_contour_levels debe estar entre 10 y 40, recibido: {levels}")
            validated['num_contour_levels'] = levels

        if 'show_axis_labels' in params:
            validated['show_axis_labels'] = bool(params['show_axis_labels'])

        if 'grid_color' in params:
            validated['grid_color'] = params['grid_color']

        if 'grid_width' in params:
            width = float(params['grid_width'])
            if not 0.2 <= width <= 2.0:
                raise ValueError(f"grid_width debe estar entre 0.2 y 2.0, recibido: {width}")
            validated['grid_width'] = width

        if 'grid_opacity' in params:
            opacity = float(params['grid_opacity'])
            if not 0.0 <= opacity <= 1.0:
                raise ValueError(f"grid_opacity debe estar entre 0.0 y 1.0, recibido: {opacity}")
            validated['grid_opacity'] = opacity

        if 'sea_level' in params:
            sea_level = float(params['sea_level'])
            # No hay límites fijos, depende de la altura del terreno
            validated['sea_level'] = sea_level

        return validated
    
    def _validate_crater_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parameters of craters"""
        validated = {}

        if 'enabled' in params:
            validated['enabled'] = bool(params['enabled'])

        if 'density' in params:
            density = int(params['density'])
            if not 0 <= density <= 10:
                raise ValueError(f"density debe estar entre 0 y 10, recibido: {density}")
            validated['density'] = density

        if 'size' in params:
            size = float(params['size'])
            if not 0.1 <= size <= 1.0:
                raise ValueError(f"size debe estar entre 0.1 y 1.0, recibido: {size}")
            validated['size'] = size

        if 'depth' in params:
            depth = float(params['depth'])
            if not 0.1 <= depth <= 1.0:
                raise ValueError(f"depth debe estar entre 0.1 y 1.0, recibido: {depth}")
            validated['depth'] = depth

        return validated
    
    # =============== TERRAIN GENERATION ========================

    def generate(self) -> Any:
        """
        Generate terrain using current parameters
        
        Returns:
            Generated heightmap(numpy array)
        """
        # Preparar parámetros usando los nombres normalizados
        gen_params = {
            'terrain_roughness': self.terrain_params.get('terrain_roughness', 50),
            'height_variation': self.terrain_params.get('height_variation', 8.0),
            'seed': self.terrain_params.get('seed', 42),
            'crater_enabled': self.crater_params.get('enabled', False),
            'num_craters': self.crater_params.get('density', 3),
            'crater_size': self.crater_params.get('size', 0.5),
            'crater_depth': self.crater_params.get('depth', 0.6),
            'base_height': self.terrain_params.get('base_height', 20.0)
        }

        # Generar terreno con todos los parámetros
        self._generator.generate_terrain(**gen_params)

        # Guardar el heightmap generado
        self._last_heightmap = self._generator.terrain
        return self._last_heightmap
    
    # =============== Utilidades ========================

    def get_all_params(self) -> Dict[str, Any]:
        """Get all current parameters"""
        result = {
            'terrain': self.terrain_params,
            'visual': self.visual_params,
            'crater': self.crater_params
        }
        # Agregar estadísticas del terreno si existe
        if self._last_heightmap is not None:
            result['terrain_stats'] = {
                'min_height': float(self._last_heightmap.min()),
                'max_height': float(self._last_heightmap.max())
            }
        return result

    def reset_to_defaults(self):
        """Reset all parameters to their default values"""
        self.terrain_params = TERRAIN_PARAMS.copy()
        self.visual_params = VISUAL_PARAMS.copy()
        self.crater_params = CRATER_PARAMS.copy()
        self._last_heightmap = None
        # Provide alias keys for compatibility after reset
        if 'height_variation' in self.terrain_params:
            self.terrain_params['vh'] = self.terrain_params['height_variation']
        if 'terrain_roughness' in self.terrain_params:
            self.terrain_params['roughness'] = self.terrain_params['terrain_roughness']
        if 'azimuth_angle' in self.visual_params:
            self.visual_params['azimuth'] = self.visual_params['azimuth_angle']
        if 'elevation_angle' in self.visual_params:
            self.visual_params['elevation'] = self.visual_params['elevation_angle']