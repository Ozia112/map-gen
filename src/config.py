"""
Módulo de configuración de parámetros
Separado en: Configuración del servidor y configuración del mapa
"""

# ============================================================
# CONFIGURACIÓN DEL SERVIDOR
# ============================================================

SERVER_CONFIG = {
    'default_host': '127.0.0.1',
    'default_port': 8080,
    'allow_lan': False,  # Si es True, usa 0.0.0.0
    'window_size': (1280, 800),
}

# ============================================================
# CONFIGURACIÓN DEL MAPA
# ============================================================

# Parámetros de generación del terreno
TERRAIN_PARAMS = {
    'height_variation': 8.0,
    'terrain_roughness': 50,
    'seed': 42,
    'base_height': 20.0,  # Altura mínima del "pastel"
}

# Parámetros de cráteres
CRATER_PARAMS = {
    'enabled': False,
    'density': 3,
    'size': 0.5,
    'depth': 0.6
}

# Parámetros de visualización
VISUAL_PARAMS = {
    'num_contour_levels': 20,
    'elevation_angle': 20,
    'azimuth_angle': 340,
    'line_color': '#ff7825',
    'sea_level': 0.0,        # Nivel del mar (líneas bajo este nivel son punteadas)
    # Controles de ejes y grilla (UI web)
    'show_axis_labels': True,
    'grid_color': '#00ffff',
    'grid_width': 0.6,       # px aprox -> linewidth mpl
    'grid_opacity': 0.35     # 0..1 para mpl
}

# Configuración de la visualización matplotlib (legacy)
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

# Configuración de renderizado
RENDER_CONFIG = {
    'preview_dpi': 150,
    'export_dpi': 300,
    'default_format': 'png',
    'available_scales': [1, 2, 4],
}

# Dimensiones del terreno (16:9)
TERRAIN_SIZE = {
    'width': 160,
    'height': 90
}

# Valores por defecto para dimensiones
DEFAULT_WIDTH = 160
DEFAULT_HEIGHT = 90

# Backend y límites de robustez
# Backend de ruido: 'perlin' o 'fbm' (fbm recomendado para alto rendimiento)
NOISE_BACKEND = 'fbm'

# Límites para evitar bloqueos por valores extremos
SEED_MIN = 1
SEED_MAX = 10_000_000
MAX_OCTAVES = 7
# Si la resolución es muy alta, conmutar Perlin -> fBm automáticamente
PERLIN_MAX_PIXELS = 160_000
