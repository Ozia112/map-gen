"""
Módulo de generación de terreno topográfico
"""
import numpy as np
from noise import pnoise3
from scipy.ndimage import gaussian_filter
from . import config


class TopographicMapGenerator:
    """Generador de mapas topográficos 3D"""
    
    def __init__(self, width=80, height=80):
        self.width = width
        self.height = height
        self.terrain = None
        self.fig = None
        self.ax = None
        self.last_backend = None
        
    def generate_terrain(self, terrain_roughness, height_variation, seed,
                         crater_enabled, num_craters, crater_size, crater_depth, base_height=20.0):
        """Genera el terreno usando Perlin noise 3D"""
        # Normalizar/limitar semillas muy grandes para evitar bloqueos o valores extremos
        try:
            seed = int(seed)
        except Exception:
            seed = config.SEED_MIN
        seed = abs(seed)
        seed = seed % getattr(config, 'SEED_MAX', 10_000_000)
        if seed < getattr(config, 'SEED_MIN', 1):
            seed = getattr(config, 'SEED_MIN', 1)
        np.random.seed(seed)
        rng = np.random.default_rng(int(seed))
        
        # Conversión de parámetros intuitivos a técnicos
        # Permitir valores mínimos bajos para terreno plano
        scale = 60.0 - max(terrain_roughness, 0) * 0.4
        octaves = max(1, int(1 + terrain_roughness * 0.05))
        octaves = min(octaves, getattr(config, 'MAX_OCTAVES', 7))
        persistence = 0.1 + terrain_roughness * 0.004
        # Desplazamiento z moderado para evitar enormes saltos con semillas gigantes
        z_offset = (seed % 100000) / 100.0
        # Backend automático
        pixels = int(self.width) * int(self.height)
        configured_backend = getattr(config, 'NOISE_BACKEND', 'fbm').lower()
        backend = configured_backend
        if configured_backend == 'perlin' and pixels > getattr(config, 'PERLIN_MAX_PIXELS', 160_000):
            backend = 'fbm'
        self.last_backend = backend

        # Generación del terreno base
        if backend == 'perlin':
            self.terrain = np.zeros((self.width, self.height), dtype=np.float32)
            base_val = int(seed % (2**31 - 1))
            for i in range(self.width):
                for j in range(self.height):
                    value = pnoise3(
                        i / scale, j / scale, z_offset,
                        octaves=octaves,
                        persistence=persistence,
                        lacunarity=2.0,
                        repeatx=1024, repeaty=1024, repeatz=1024,
                        base=base_val
                    )
                    self.terrain[i, j] = value
            self.terrain *= float(height_variation)
        else:
            self.terrain = self._generate_fbm_terrain(
                width=self.width,
                height=self.height,
                base_sigma=max(1.0, scale * 0.25),
                octaves=octaves,
                persistence=persistence,
                rng=rng
            ).astype(np.float32)
            self.terrain *= float(height_variation)

        # Suavizado del terreno
        self.terrain = gaussian_filter(self.terrain, sigma=0.8)

        # Normalizar terreno ANTES de cráteres para tener base consistente
        # Esto asegura que el terreno base esté en rango [0, height_variation]
        min_val = float(self.terrain.min())
        self.terrain -= min_val
        
        # Aplicar cráteres DESPUÉS de normalización
        # Así los cráteres se aplican sobre una base estable y mantienen su efecto
        if crater_enabled and num_craters > 0:
            self._apply_craters_visible(
                num_craters=int(num_craters),
                crater_size=float(crater_size),
                crater_depth=float(crater_depth),
                rng=rng
            )
        
        # Añadir altura base mínima para efecto "pastel" AL FINAL
        # Esto asegura que siempre haya profundidad visible
        self.terrain += float(base_height)

        np.random.seed(None)

    def _apply_craters_visible(self, num_craters, crater_size, crater_depth, rng):
        """Cráteres visibles para cualquier variación de altura/rugosidad.
        - Profundidad controlada por crater_depth (0.1 a 1.0)
        - Centro hundido con transición suave
        - Rim (borde) elevado más pronunciado
        - El cráter más nuevo domina en zonas solapadas
        """
        # Relieve global (evitar 0)
        relief = float(np.ptp(self.terrain)) or 1.0
        # Amplitud del cráter: componente ABSOLUTA + componente relativa
        # Esto asegura que los cráteres sean visibles incluso en terrenos planos
        depth_factor = np.clip(crater_depth, 0.1, 1.0)
        # Profundidad base absoluta (5.0 unidades) + profundidad relativa al terreno
        amp = (5.0 + relief * 0.35) * depth_factor
        # Aplanado del parche para ganar contraste (0..1)
        flatten = 0.6

        for _ in range(int(num_craters)):
            # Radio base según control de tamaño
            R = int(12 + crater_size * 25)
            R = max(5, min(R, min(self.width, self.height) // 2 - 2))
            rim_w = max(2, int(0.25 * R))  # Rim más ancho

            # Centro aleatorio evitando bordes
            margin = 6 + R + rim_w
            if (self.width <= 2 * margin) or (self.height <= 2 * margin):
                # Si el terreno es muy pequeño, caer en el centro
                cx = self.width // 2
                cy = self.height // 2
            else:
                cx = int(rng.integers(margin, self.width - margin))
                cy = int(rng.integers(margin, self.height - margin))

            # Ventana del parche
            ix0 = max(0, cx - (R + rim_w))
            ix1 = min(self.width, cx + (R + rim_w) + 1)
            jy0 = max(0, cy - (R + rim_w))
            jy1 = min(self.height, cy + (R + rim_w) + 1)

            # Malla de distancias (recordar: shape = (width, height))
            ii, jj = np.ogrid[ix0:ix1, jy0:jy1]
            r = np.sqrt((ii - cx) ** 2 + (jj - cy) ** 2)

            # Perfil lunar mejorado
            profile = np.zeros((ix1 - ix0, jy1 - jy0), dtype=float)
            r0 = 0.65 * R  # radio del fondo plano
            # Fondo plano hundido (más profundo según crater_depth)
            profile[r <= r0] = -amp
            # Transición suave al borde
            mask_trans = (r > r0) & (r <= R)
            if mask_trans.any():
                t = (r[mask_trans] - r0) / (R - r0)
                profile[mask_trans] = -amp * (1.0 - (3.0 * t**2 - 2.0 * t**3))
            # Rim elevado MÁS PRONUNCIADO
            mask_rim = (r > R) & (r <= R + rim_w)
            if mask_rim.any():
                tr = (r[mask_rim] - R) / rim_w
                # Elevación más alta y más visible
                bell = np.exp(-((tr - 0.35) ** 2) / (2 * 0.15**2))
                profile[mask_rim] += 0.8 * amp * bell  # Aumentado de 0.55 a 0.8

            # Aplanar el parche para aumentar contraste
            patch = self.terrain[ix0:ix1, jy0:jy1].copy()
            baseline = float(patch.mean())
            mask_all = r <= (R + rim_w)
            patch[mask_all] = (1 - flatten) * patch[mask_all] + flatten * baseline

            # Sobrescritura suave priorizando el cráter actual
            weight = np.clip(1.0 - (r / (R + rim_w)) ** 2, 0.0, 1.0)
            combined = patch * (1 - 0.85 * weight) + (baseline + profile) * (0.85 * weight)
            self.terrain[ix0:ix1, jy0:jy1] = np.where(mask_all, combined, self.terrain[ix0:ix1, jy0:jy1])

    def get_heightmap_payload(self):
        """Serializa el hieghmap para el visor WebGL"""
        hm = getattr(self, 'terrain', None)
        if hm is None:
            return {'width': int(self.width), 'height': int(self.height), 'z': []}
        return {
            'width': int(self.width),
            'height': int(self.height),
            'z': hm.astype(np.float32).tolist()
        }
    
    def set_heightmap(self, z, normalize=True):
        """Permite cargar un heightmap externo (Para segunda fase)"""
        z = np.asarray(z, dtype=np.float32)
        if normalize:
            mn, mx = float(z.min()), float(z.max())
            if mx > mn:
                z = (z - mn) / (mx - mn)
        self.terrain = z
        self.width, self.height = int(z.shape[0]), int(z.shape[1])

    def _generate_fbm_terrain(self, width, height, base_sigma, octaves, persistence, rng):
        """fBm 2D vectorizado usando suma de ruidos gaussianos multi-escala."""
        acc = np.zeros((width, height), dtype=np.float32)
        amp = 1.0
        sigma = float(base_sigma)
        for _ in range(int(octaves)):
            n = rng.standard_normal((width, height), dtype=np.float32)
            s = max(0.6, sigma)
            f = gaussian_filter(n, sigma=s, mode='reflect')
            std = float(f.std()) or 1.0
            f = f / std
            acc += amp * f
            amp *= float(persistence)
            sigma /= 2.0
        m = float(np.max(np.abs(acc))) or 1.0
        return (acc / m)
