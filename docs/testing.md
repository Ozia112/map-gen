# Pruebas automatizadas

Las pruebas usan `pytest` y cubren la lógica principal del proyecto.

## Ejecutar

```powershell
pytest -q
```

## Áreas cubiertas

- Normalización de semilla y límites (SEED_MIN/SEED_MAX)
- Selección de backend (Perlin vs fBm) y conmutación automática
- Utilidades de visualización (z-base y niveles seguros)

## Escribir nuevas pruebas

- Coloca los archivos en `tests/` con prefijo `test_*.py`
- Evita pruebas frágiles con gráficos; prueba invariantes de datos y límites
