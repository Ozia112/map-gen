"""
Render Controller - Maneja el renderizado y exportación de mapas
Actúa como capa de abstracción entre el controlador y las funciones de visualización
"""
import os
import sys
from typing import Dict, Any

# Asegurar que el directorio src esté en el path
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar funciones de visualización
from view.visualization import (
    export_preview_image as _export_preview,
    export_map_clean as _export_clean,
    export_with_dialog as _export_dialog,
    ensure_unique_path
)


class RenderController:
    """
    Controlador de renderizado que encapsula la lógica de visualización.
    Responsable de:
    - Generar previews para la UI
    - Exportar mapas en diferentes formatos
    - Manejar diálogos de exportación
    """
    
    def __init__(self):
        pass
    
    def render_preview(self, generator, visual_params: Dict[str, Any], output_path: str) -> str:
        """
        Genera una imagen de preview del mapa.
        
        Args:
            generator: Instancia de TopographicMapGenerator
            visual_params: Parámetros de visualización
            output_path: Ruta donde guardar el preview
            
        Returns:
            Ruta del archivo generado
        """
        _export_preview(generator, visual_params, output_path)
        return output_path
    
    def export_map(
        self,
        generator,
        visual_params: Dict[str, Any],
        fmt: str = 'png',
        save_path: str = None,
        include_grid: bool = None,
        scale: int = 1
    ) -> bool:
        """
        Exporta el mapa en el formato especificado.
        
        Args:
            generator: Instancia de TopographicMapGenerator
            visual_params: Parámetros de visualización
            fmt: Formato de salida ('png' o 'svg')
            save_path: Ruta de guardado (None para auto-generar)
            include_grid: Incluir grid y ejes (None usa visual_params)
            scale: Factor de escala (1, 2, o 4)
            
        Returns:
            True si la exportación fue exitosa
        """
        return _export_clean(
            generator,
            visual_params,
            fmt=fmt,
            save_path=save_path,
            include_grid=include_grid,
            scale=scale
        )
    
    def export_with_dialog(self, generator, visual_params: Dict[str, Any]) -> bool:
        """
        Abre un diálogo nativo para exportar el mapa.
        
        Args:
            generator: Instancia de TopographicMapGenerator
            visual_params: Parámetros de visualización
            
        Returns:
            True si el usuario completó la exportación
        """
        return _export_dialog(generator, visual_params)
    
    @staticmethod
    def get_unique_path(path: str) -> str:
        """
        Genera una ruta única agregando (n) si el archivo existe.
        
        Args:
            path: Ruta base del archivo
            
        Returns:
            Ruta única que no sobrescribe archivos existentes
        """
        return ensure_unique_path(path)


# Instancia singleton para uso global
render_controller = RenderController()
