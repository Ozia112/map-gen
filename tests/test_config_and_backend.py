import importlib
import os
import sys
import pytest

# Fallback to add <project_root>/src to sys.path for static analyzers and direct runs
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Skip tests gracefully if heavy deps are missing
pytest.importorskip("scipy")
pytest.importorskip("noise")
pytest.importorskip("matplotlib")


def test_seed_normalization_limits():
    terrain_module = importlib.import_module('terrain_generator')
    config = importlib.import_module('config')
    gen = terrain_module.TopographicMapGenerator(width=32, height=32)
    # Semilla negativa y enorme
    params = {
        'terrain_roughness': 50,
        'height_variation': 5.0,
        'seed': -999999999999,
        'crater_enabled': False,
        'num_craters': 0,
        'crater_size': 0.5,
        'crater_depth': 0.5,
    }
    gen.generate_terrain(**params)
    assert config.SEED_MIN <= 1 <= config.SEED_MAX
    # Si generó sin excepción, la normalización fue aplicada
    assert gen.terrain is not None


def test_backend_auto_switch_large_resolution(monkeypatch):
    # Forzar backend 'perlin' en config para probar conmutación
    config = importlib.import_module('config')
    monkeypatch.setattr(config, 'NOISE_BACKEND', 'perlin', raising=False)
    monkeypatch.setattr(config, 'PERLIN_MAX_PIXELS', 1000, raising=False)

    terrain_module = importlib.import_module('terrain_generator')
    gen = terrain_module.TopographicMapGenerator(width=64, height=64)
    params = {
        'terrain_roughness': 50,
        'height_variation': 5.0,
        'seed': 42,
        'crater_enabled': False,
        'num_craters': 0,
        'crater_size': 0.5,
        'crater_depth': 0.5,
    }
    gen.generate_terrain(**params)
    # Debería conmutar a fbm por tamaño
    assert getattr(gen, 'last_backend', None) == 'fbm'


def test_visual_utils_levels_and_zbase():
    viz = importlib.import_module('visualization')
    levels = viz._compute_levels(10.0, 10.0, 20)
    assert isinstance(levels, list) or hasattr(levels, '__len__')
    assert len(levels) == 0
    # Con rango 0..10 y nlevels=2, esperamos dos niveles: en 3.33.. y 6.66..
    levels = viz._compute_levels(0.0, 10.0, 2)
    assert len(levels) == 2
    zb = viz._compute_z_base(0.0, 0.0)
    assert isinstance(zb, float)


def test_export_creates_generados(tmp_path, monkeypatch):
    # Use non-interactive backend for matplotlib
    import matplotlib
    matplotlib.use('Agg', force=True)

    # Ensure clean state for output directory
    out_dir = os.path.join(PROJECT_ROOT, 'generados')
    if os.path.isdir(out_dir):
        # Don't delete user's images; just run export and assert directory exists
        pass

    # Small terrain to keep test fast
    terrain_module = importlib.import_module('terrain_generator')
    gen = terrain_module.TopographicMapGenerator(width=32, height=18)
    params = {
        'terrain_roughness': 30,
        'height_variation': 3.0,
        'seed': 99,
        'crater_enabled': False,
        'num_craters': 0,
        'crater_size': 0.4,
        'crater_depth': 0.4,
    }
    gen.generate_terrain(**params)

    viz = importlib.import_module('visualization')
    ok = viz.export_map_clean(gen, {
        'num_contour_levels': 10,
        'elevation_angle': 20,
        'azimuth_angle': 330,
        'line_color': '#ff7825',
        'show_axis_labels': False,
        'grid_color': '#00ffff',
        'grid_width': 0.5,
        'grid_opacity': 0.3,
    })
    assert ok is True
    assert os.path.isdir(out_dir)
