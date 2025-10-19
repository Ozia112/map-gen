"""
Tests unitarios para MapController
Verifica la orquestación entre Modelo y Vista
"""
import pytest
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from model.map_model import MapModel
from controller.map_controller import MapController


class TestControllerInitialization:
    """Tests de inicialización del controlador"""
    
    def test_controller_creates_with_model(self):
        """El controlador se crea con un modelo"""
        model = MapModel()
        controller = MapController(model)
        
        assert controller.model is model
        assert controller.render_controller is not None
    
    def test_controller_creates_preview_directory(self):
        """El controlador crea el directorio de previews"""
        model = MapModel()
        preview_dir = "test_previews"
        controller = MapController(model, preview_dir=preview_dir)
        
        assert os.path.exists(preview_dir)
        
        # Limpiar
        os.rmdir(preview_dir)


class TestHandleUpdate:
    """Tests de actualización de parámetros"""
    
    def test_handle_update_terrain_success(self):
        """handle_update actualiza parámetros de terreno correctamente"""
        model = MapModel()
        controller = MapController(model)
        
        result = controller.handle_update({
            'terrain': {'seed': 555, 'vh': 10.0}
        })
        
        assert result['ok'] is True
        assert model.terrain_params['seed'] == 555
        assert model.terrain_params['vh'] == 10.0
    
    def test_handle_update_visual_success(self):
        """handle_update actualiza parámetros visuales correctamente"""
        model = MapModel()
        controller = MapController(model)
        
        result = controller.handle_update({
            'visual': {'azimuth': 200.0, 'elevation': 30.0}
        })
        
        assert result['ok'] is True
        assert model.visual_params['azimuth'] == 200.0
        assert model.visual_params['elevation'] == 30.0
    
    def test_handle_update_invalid_params(self):
        """handle_update maneja parámetros inválidos"""
        model = MapModel()
        controller = MapController(model)
        
        result = controller.handle_update({
            'terrain': {'vh': 999}  # Inválido
        })
        
        assert result['ok'] is False
        assert 'error' in result
    
    def test_handle_terrain_update_shortcut(self):
        """handle_terrain_update es un atajo funcional"""
        model = MapModel()
        controller = MapController(model)
        
        result = controller.handle_terrain_update(seed=888)
        
        assert result['ok'] is True
        assert model.terrain_params['seed'] == 888


class TestRotation:
    """Tests de rotación de vista"""
    
    def test_handle_rotation_success(self):
        """handle_rotation actualiza ángulos"""
        model = MapModel()
        controller = MapController(model)
        
        # Generar mapa primero
        controller.initialize_map()
        
        result = controller.handle_rotation(azimuth=90.0, elevation=45.0)
        
        assert result['ok'] is True
        assert model.visual_params['azimuth'] == 90.0
        assert model.visual_params['elevation'] == 45.0
    
    def test_handle_reset_rotation(self):
        """handle_reset_rotation restaura ángulos por defecto"""
        model = MapModel()
        controller = MapController(model)
        
        # Generar mapa y modificar rotación
        controller.initialize_map()
        controller.handle_rotation(azimuth=100.0, elevation=70.0)
        
        # Resetear
        result = controller.handle_reset_rotation()
        
        assert result['ok'] is True
        # Debería volver a valores por defecto (315, 45)
        assert model.visual_params['azimuth'] == 315
        assert model.visual_params['elevation'] == 45


class TestExport:
    """Tests de exportación"""
    
    def test_handle_export_without_map(self):
        """handle_export falla si no hay mapa generado"""
        model = MapModel()
        controller = MapController(model)
        
        result = controller.handle_export({
            'format': 'png',
            'path': 'test.png'
        })
        
        assert result['ok'] is False
        assert 'error' in result


class TestStateManagement:
    """Tests de gestión de estado"""
    
    def test_get_current_state(self):
        """get_current_state retorna el estado completo"""
        model = MapModel()
        controller = MapController(model)
        
        state = controller.get_current_state()
        
        assert 'params' in state
        assert 'preview' in state
        assert 'has_terrain' in state
    
    def test_reset_restores_defaults(self):
        """reset() restaura el modelo a valores por defecto"""
        model = MapModel()
        controller = MapController(model)
        
        # Modificar parámetros
        controller.handle_update({
            'terrain': {'seed': 999}
        })
        
        # Resetear
        result = controller.reset()
        
        assert result['ok'] is True
        # El seed debería haber cambiado del 999


class TestInitializeMap:
    """Tests de inicialización del mapa"""
    
    def test_initialize_map_generates_terrain(self):
        """initialize_map genera el terreno inicial"""
        model = MapModel()
        controller = MapController(model)
        
        result = controller.initialize_map()
        
        assert result['ok'] is True
        assert model.heightmap is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
