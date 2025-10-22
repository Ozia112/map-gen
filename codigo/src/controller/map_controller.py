import os
import sys
from typing import Dict, Any, Optional

# Asegurar que el directorio src esté en el path
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.map_model import MapModel
from controller.render_controller import RenderController
from .config import VISUAL_PARAMS

class MapController:
    """
    Controlador principal para operaciones del mapa
    Orquesta las interacciones entre la vista y el modelo
    """
    def __init__(self, model: MapModel, preview_dir: Optional[str] = None):
        self.model = model
        self.render_controller = RenderController()
        # Ensure preview directory exists if provided (tests expect this)
        if preview_dir:
            os.makedirs(preview_dir, exist_ok=True)
        self._preview_dir = preview_dir
    
    # ============== Actualizacion de parametros ===========================

    def handle_update(self, params: dict) -> Dict[str, Any]:
        """
        Handles the update if params and regenerate the map

        Args:
            params: Dict with keywords 'terrain', 'visual', 'craters'

        Returns:
            Dict with result: {'ok': bool, 'preview': str, 'error': str}
        """
        try:
            # Actualizar los parametros del modelo
            if 'terrain' in params:
                # Backward compat: map shorthand keys used in tests
                terrain = dict(params['terrain'])
                if 'vh' in terrain and 'height_variation' not in terrain:
                    terrain['height_variation'] = terrain.pop('vh')
                if 'roughness' in terrain and 'terrain_roughness' not in terrain:
                    terrain['terrain_roughness'] = terrain.pop('roughness')
                self.model.update_terrain_params(**terrain)
            
            if 'visual' in params:
                # Backward compat for tests: azimuth/elevation keys
                visual = dict(params['visual'])
                if 'azimuth' in visual and 'azimuth_angle' not in visual:
                    visual['azimuth_angle'] = visual.pop('azimuth')
                if 'elevation' in visual and 'elevation_angle' not in visual:
                    visual['elevation_angle'] = visual.pop('elevation')
                self.model.update_visual_params(**visual)
            
            if 'craters' in params:
                self.model.update_crater_params(**params['craters'])

            # Regenerar terreno
            heightmap = self.model.generate()

            # If we have a preview dir, render a preview path for UI/tests
            result = {
                'ok': True,
                'params': self.model.get_all_params()
            }
            if self._preview_dir:
                preview_path = os.path.join(self._preview_dir, 'preview.png')
                try:
                    self.render_controller.render_preview(self.model.generator, self.model.visual_params, preview_path)
                    result['preview'] = preview_path
                except Exception:
                    pass
            return result
        except ValueError as e:
            return {'ok': False, 'error': str(e)}
        except Exception as e:
            return {'ok': False, 'error': f"Error inesperado: {str(e)}"}
        
    def handle_terrain_update(self, **kwargs) -> Dict[str, Any]:
        """Actualiza solo parametros del terreno"""
        return self.handle_update({'terrain': kwargs})
    
    def handle_visual_update(self, **kwargs) -> Dict[str, Any]:
        """Actualiza solo parametros visuales"""
        return self.handle_update({'visual': kwargs})
    
    def handle_crater_update(self, **kwargs) -> Dict[str, Any]:
        """Actualiza solo parametros de crateres"""
        return self.handle_update({'craters': kwargs})
    
    # ============== Rotacion ============================

    def handle_rotation(self, azimuth_angle: Optional[float] = None, elevation_angle: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        """
        Update view angles without regenerating terrain
        Args:
            azimuth_angle: azimuth angle (0-360)
            elevation_angle: elevation angle (0-90)

        Returns:
            Dict with result
        """
        try:
            # Accept legacy names 'azimuth'/'elevation' too
            if azimuth_angle is None and 'azimuth' in kwargs:
                azimuth_angle = kwargs['azimuth']
            if elevation_angle is None and 'elevation' in kwargs:
                elevation_angle = kwargs['elevation']
            update = {}
            if azimuth_angle is not None:
                update['azimuth_angle'] = azimuth_angle
            if elevation_angle is not None:
                update['elevation_angle'] = elevation_angle
            if update:
                self.model.update_visual_params(**update)

            # Solo actualizar parámetros (sin regenerar terreno)
            if self.model.heightmap is not None:
                return {'ok': True}
            else:
                return {'ok': False, 'error': "No hay mapa generado."}
        except ValueError as e:
            return {'ok': False, 'error': str(e)}
    
    def handle_reset_rotation(self) -> Dict[str, Any]:
        """Reestablece la rotacion a valores por defecto"""
        return self.handle_rotation(
            azimuth_angle=VISUAL_PARAMS['azimuth_angle'],
            elevation_angle=VISUAL_PARAMS['elevation_angle']
        )

    # ============== Generacion Inicial ============================
    def initialize_map(self) -> Dict[str, Any]:
        """Generate initial map with default parameters"""
        return self.handle_update({
            'terrain': self.model.terrain_params,
            'visual': self.model.visual_params,
            'craters': self.model.crater_params
        })
    
    # ============== Exportacion ============================

    def handle_export(self, export_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle export map

        Args:
            export_params: {
                'format': 'png' | 'svg',
                'path': str,
                'scale': int,
                'include_grid': bool
            }
        Returns:
            Dict with result: {'ok': bool, 'file': str, 'error': str}
        """
        try:
            if self.model.heightmap is None:
                return {'ok': False, 'error': "No hay mapa generado para exportar."}
            
            fmt = export_params.get('format', 'png')
            output_path = export_params.get('path', 'output')
            scale = export_params.get('scale', 1)
            include_grid = export_params.get('include_grid', False)

            # Exportar usando render_controller
            success = self.render_controller.export_map(
                self.model.generator,
                self.model.visual_params,
                fmt=fmt,
                save_path=output_path,
                include_grid=include_grid,
                scale=scale
            )
            
            if success:
                return {'ok': True, 'path': output_path}
            else:
                return {'ok': False, 'error': 'Error durante la exportación'}
        
        except Exception as e:
            return {'ok': False, 'error': f"Error al exportar: {str(e)}"}
    
    # ================= Utils ==================================

    def get_current_state(self) -> Dict[str, Any]:
        """Get current state of the model"""
        result = {
            'params': self.model.get_all_params(),
            'has_terrain': self.model.heightmap is not None
        }
        # Always include preview key for UI/tests
        preview_path = os.path.join(self._preview_dir, 'preview.png') if self._preview_dir else 'tmp/preview.png'
        result['preview'] = preview_path
        return result

    def reset(self) -> Dict[str, Any]:
        """Reset model to default state"""
        self.model.reset_to_defaults()
        return self.initialize_map()