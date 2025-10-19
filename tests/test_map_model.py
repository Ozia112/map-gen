"""
Tests unitarios para MapModel
Verifica la encapsulación del estado y validación de parámetros
"""
import pytest
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from model.map_model import MapModel


class TestMapModelInitialization:
    """Tests de inicialización del modelo"""
    
    def test_model_creates_with_defaults(self):
        """El modelo se crea con parámetros por defecto"""
        model = MapModel()
        
        assert model.terrain_params is not None
        assert model.visual_params is not None
        assert model.crater_params is not None
        assert model.generator is not None
    
    def test_model_creates_with_custom_size(self):
        """El modelo acepta dimensiones personalizadas"""
        model = MapModel(width=200, height=100)
        
        assert model.generator.width == 200
        assert model.generator.height == 100


class TestTerrainParametersValidation:
    """Tests de validación de parámetros de terreno"""
    
    def test_valid_vh_parameter(self):
        """VH válido se acepta"""
        model = MapModel()
        result = model.update_terrain_params(vh=10.0)
        
        assert 'vh' in result
        assert result['vh'] == 10.0
        assert model.terrain_params['vh'] == 10.0
    
    def test_invalid_vh_too_high(self):
        """VH mayor a 20 lanza ValueError"""
        model = MapModel()
        
        with pytest.raises(ValueError, match="vh debe estar entre 0 y 20"):
            model.update_terrain_params(vh=25.0)
    
    def test_invalid_vh_negative(self):
        """VH negativo lanza ValueError"""
        model = MapModel()
        
        with pytest.raises(ValueError, match="vh debe estar entre 0 y 20"):
            model.update_terrain_params(vh=-5.0)
    
    def test_valid_roughness_parameter(self):
        """Roughness válido se acepta"""
        model = MapModel()
        result = model.update_terrain_params(roughness=75)
        
        assert result['roughness'] == 75
        assert model.terrain_params['roughness'] == 75
    
    def test_invalid_roughness_too_high(self):
        """Roughness mayor a 100 lanza ValueError"""
        model = MapModel()
        
        with pytest.raises(ValueError, match="roughness debe estar entre 0 y 100"):
            model.update_terrain_params(roughness=150)
    
    def test_valid_seed_parameter(self):
        """Seed válida se acepta"""
        model = MapModel()
        result = model.update_terrain_params(seed=999)
        
        assert result['seed'] == 999
        assert model.terrain_params['seed'] == 999
    
    def test_invalid_seed_negative(self):
        """Seed negativa lanza ValueError"""
        model = MapModel()
        
        with pytest.raises(ValueError, match="seed debe ser positivo"):
            model.update_terrain_params(seed=-1)
    
    def test_multiple_params_update(self):
        """Múltiples parámetros se actualizan correctamente"""
        model = MapModel()
        result = model.update_terrain_params(vh=12.0, roughness=60, seed=777)
        
        assert result['vh'] == 12.0
        assert result['roughness'] == 60
        assert result['seed'] == 777


class TestVisualParametersValidation:
    """Tests de validación de parámetros visuales"""
    
    def test_valid_azimuth(self):
        """Azimuth válido se acepta"""
        model = MapModel()
        result = model.update_visual_params(azimuth=180.0)
        
        assert result['azimuth'] == 180.0
    
    def test_azimuth_normalization(self):
        """Azimuth se normaliza a [0, 360)"""
        model = MapModel()
        result = model.update_visual_params(azimuth=400.0)
        
        assert result['azimuth'] == 40.0  # 400 % 360
    
    def test_valid_elevation(self):
        """Elevation válido se acepta"""
        model = MapModel()
        result = model.update_visual_params(elevation=45.0)
        
        assert result['elevation'] == 45.0
    
    def test_invalid_elevation_too_high(self):
        """Elevation mayor a 90 lanza ValueError"""
        model = MapModel()
        
        with pytest.raises(ValueError, match="elevation debe estar entre 0 y 90"):
            model.update_visual_params(elevation=100.0)
    
    def test_valid_line_color(self):
        """Color hexadecimal válido se acepta"""
        model = MapModel()
        result = model.update_visual_params(line_color='#FF0000')
        
        assert result['line_color'] == '#FF0000'
    
    def test_invalid_line_color(self):
        """Color inválido lanza ValueError"""
        model = MapModel()
        
        with pytest.raises(ValueError, match="line_color debe ser un color hexadecimal"):
            model.update_visual_params(line_color='rojo')


class TestCraterParametersValidation:
    """Tests de validación de parámetros de cráteres"""
    
    def test_valid_density(self):
        """Densidad válida se acepta"""
        model = MapModel()
        result = model.update_crater_params(density=5)
        
        assert result['density'] == 5
    
    def test_invalid_density_too_high(self):
        """Densidad mayor a 10 lanza ValueError"""
        model = MapModel()
        
        with pytest.raises(ValueError, match="density debe estar entre 0 y 10"):
            model.update_crater_params(density=15)
    
    def test_valid_size(self):
        """Tamaño válido se acepta"""
        model = MapModel()
        result = model.update_crater_params(size=0.7)
        
        assert result['size'] == 0.7
    
    def test_invalid_size_too_small(self):
        """Tamaño menor a 0.1 lanza ValueError"""
        model = MapModel()
        
        with pytest.raises(ValueError, match="size debe estar entre 0.1 y 1.0"):
            model.update_crater_params(size=0.05)


class TestMapGeneration:
    """Tests de generación de mapas"""
    
    def test_generate_creates_heightmap(self):
        """generate() crea un heightmap"""
        model = MapModel()
        heightmap = model.generate()
        
        assert heightmap is not None
        assert model.heightmap is not None
        assert heightmap is model.heightmap
    
    def test_generate_with_custom_params(self):
        """generate() usa parámetros actualizados"""
        model = MapModel()
        model.update_terrain_params(seed=123, vh=15.0)
        
        heightmap = model.generate()
        
        assert heightmap is not None
        # El seed debería haberse usado
        assert model.terrain_params['seed'] == 123


class TestModelUtilities:
    """Tests de métodos utilitarios"""
    
    def test_get_all_params(self):
        """get_all_params() retorna todos los parámetros"""
        model = MapModel()
        all_params = model.get_all_params()
        
        assert 'terrain' in all_params
        assert 'visual' in all_params
        assert 'crater' in all_params
    
    def test_reset_to_defaults(self):
        """reset_to_defaults() restaura valores iniciales"""
        model = MapModel()
        
        # Modificar parámetros
        model.update_terrain_params(seed=999)
        model.update_visual_params(azimuth=100.0)
        
        # Resetear
        model.reset_to_defaults()
        
        # Verificar que se restauraron
        assert model.terrain_params['seed'] != 999
        assert model.visual_params['azimuth'] != 100.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
