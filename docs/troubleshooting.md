# Solución de problemas

## Errores de importación

- Al ejecutar `src/main.py`, usa imports absolutos (`import config`) en lugar de relativos.

## Semillas grandes que cuelgan

- Se normalizan en UI y backend a `[SEED_MIN, SEED_MAX]`
- Backend `fbm` evita cuellos de botella de Perlin en resoluciones altas

## Rendimiento bajo

- Reduce `TERRAIN_SIZE` temporalmente para previsualizar
- Baja `MAX_OCTAVES` si la rugosidad es alta
- Revisa `docs/performance.md`
