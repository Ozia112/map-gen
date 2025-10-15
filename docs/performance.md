# Rendimiento y tuning

## Recomendaciones

- Usa backend `fbm` por defecto (`config.NOISE_BACKEND = 'fbm'`)
- Limita `MAX_OCTAVES` (p.ej. 5–7) para balances buenos
- Evita resoluciones excesivas; o usa exportaciones escaladas
- Mantén `meshgrid` cacheado (ya implementado)

## Conmutación automática

- Si `NOISE_BACKEND='perlin'` y `width*height > PERLIN_MAX_PIXELS`, se conmutará a `fbm` automáticamente

## Futuras mejoras (opcionales)

- Implementar OpenSimplex/FastNoiseLite (bindings C++)
- Numba en rutas críticas si se agregan bucles Python
