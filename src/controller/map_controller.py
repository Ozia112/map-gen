import os
import sys
from typing import Dict, Any, Optional

# Asegurar que el directorio src esté en el path
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.map_model import MapModel
from controller.render_controller import RenderController
from config import VISUAL_PARAMS

class MapController:
    """
    Controlador principal para operaciones del mapa
    Orquesta las interacciones entre la vista y el modelo
    """
    def __init__(self, model: MapModel):
        self.model = model
        self.render_controller = RenderController()
    
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
                self.model.update_terrain_params(**params['terrain'])
            
            if 'visual' in params:
                self.model.update_visual_params(**params['visual'])
            
            if 'craters' in params:
                self.model.update_crater_params(**params['craters'])

            # Regenerar terreno
            heightmap = self.model.generate()

            return {
                'ok': True,
                'params': self.model.get_all_params()
            }
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

    def handle_rotation(self, azimuth_angle: float, elevation_angle: float) -> Dict[str, Any]:
        """
        Update view angles without regenerating terrain
        Args:
            azimuth_angle: azimuth angle (0-360)
            elevation_angle: elevation angle (0-90)

        Returns:
            Dict with result
        """
        try:
            self.model.update_visual_params(
                azimuth_angle=azimuth_angle,
                elevation_angle=elevation_angle
            )

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
        return {
            'params': self.model.get_all_params(),
            'has_terrain': self.model.heightmap is not None
        }

    def reset(self) -> Dict[str, Any]:
        """Reset model to default state"""
        self.model.reset_to_defaults()
        return self.initialize_map()