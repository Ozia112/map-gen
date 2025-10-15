"""
Módulo de configuración de parámetros
"""

# Parámetros de generación del terreno
TERRAIN_PARAMS = {
    'terrain_roughness': 50,
    'height_variation': 8.0,
    'seed': 42,
    'crater_enabled': False,
    'num_craters': 3,
    'crater_size': 0.5,
    'crater_depth': 0.6
}

# Parámetros de visualización
VISUAL_PARAMS = {
    'num_contour_levels': 20,
    'elevation_angle': 20,
    'azimuth_angle': 340,
    'line_color': '#ff7825',
    # Controles de ejes y grilla (UI web)
    'show_axis_labels': True,
    'grid_color': '#00ffff',
    'grid_width': 0.6,       # px aprox -> linewidth mpl
    'grid_opacity': 0.35     # 0..1 para mpl
}

# Configuración de la ventana
WINDOW_CONFIG = {
    'figsize': (16, 9),
    'facecolor': '#1a1a1a',
    'subplots_adjust': {
        'left': 0.02,
        'bottom': 0.18,
        'right': 0.98,
        'top': 0.98
    }
}

# Dimensiones del terreno (16:9)
TERRAIN_SIZE = {
    'width': 160,
    'height': 90
}

# Backend y límites de robustez
# Backend de ruido: 'perlin' o 'fbm' (fbm recomendado para alto rendimiento)
NOISE_BACKEND = 'fbm'

# Límites para evitar bloqueos por valores extremos
SEED_MIN = 1
SEED_MAX = 10_000_000
MAX_OCTAVES = 7
# Si la resolución es muy alta, conmutar Perlin -> fBm automáticamente
PERLIN_MAX_PIXELS = 160_000
