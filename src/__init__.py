"""
VISTAR - Generador de Mapas Topográficos 3D
Sistema de generación y visualización de terrenos procedurales
"""

# Importar componentes principales del paquete para acceso directo
from .model import MapModel
from .controller import MapController
from .controller.terrain_generator import TopographicMapGenerator
from .config import (
    TERRAIN_PARAMS,
    VISUAL_PARAMS,
    CRATER_PARAMS,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT
)

__version__ = "1.0.0"
__author__ = "Ozia"

__all__ = [
    'MapModel',
    'MapController',
    'TopographicMapGenerator',
    'TERRAIN_PARAMS',
    'VISUAL_PARAMS',
    'CRATER_PARAMS',
    'DEFAULT_WIDTH',
    'DEFAULT_HEIGHT'
]