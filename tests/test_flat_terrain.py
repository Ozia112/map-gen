import numpy as np
import sys
sys.path.insert(0, 'src')

from controller.terrain_generator import TopographicMapGenerator

print("=" * 60)
print("TEST: Verificación de BASE_HEIGHT (forma de pastel)")
print("=" * 60)

# Crear generador
generator = TopographicMapGenerator(width=100, height=100)

# Caso 1: Variación mínima (0.1)
print("\n1. Generando terreno con height_variation=0.1...")
generator.generate_terrain(
    terrain_roughness=50,
    height_variation=0.1,
    seed=42,
    crater_enabled=False,
    num_craters=0,
    crater_size=0.5,
    crater_depth=0.6
)

min_h = float(generator.terrain.min())
max_h = float(generator.terrain.max())
mean_h = float(generator.terrain.mean())

print(f"   Altura mínima: {min_h:.4f}")
print(f"   Altura máxima: {max_h:.4f}")
print(f"   Altura promedio: {mean_h:.4f}")
print(f"   Rango de variación: {max_h - min_h:.4f}")

if min_h >= 2.0:
    print("   ✅ BASE_HEIGHT aplicado correctamente (min >= 2.0)")
else:
    print(f"   ❌ BASE_HEIGHT NO aplicado (min < 2.0)")

# Caso 2: Variación normal (8.0)
print("\n2. Generando terreno con height_variation=8.0...")
generator.generate_terrain(
    terrain_roughness=50,
    height_variation=8.0,
    seed=42,
    crater_enabled=False,
    num_craters=0,
    crater_size=0.5,
    crater_depth=0.6
)

min_h2 = float(generator.terrain.min())
max_h2 = float(generator.terrain.max())
mean_h2 = float(generator.terrain.mean())

print(f"   Altura mínima: {min_h2:.4f}")
print(f"   Altura máxima: {max_h2:.4f}")
print(f"   Altura promedio: {mean_h2:.4f}")
print(f"   Rango de variación: {max_h2 - min_h2:.4f}")

if min_h2 >= 2.0:
    print("   ✅ BASE_HEIGHT aplicado correctamente (min >= 2.0)")
else:
    print(f"   ❌ BASE_HEIGHT NO aplicado (min < 2.0)")

print("\n" + "=" * 60)
print("CONCLUSIÓN:")
print("=" * 60)
if min_h >= 2.0 and min_h2 >= 2.0:
    print("✅ La forma de 'pastel' está correctamente implementada")
    print("   Todos los terrenos tienen una altura base mínima de 2.0")
else:
    print("❌ Hay un problema con la implementación del BASE_HEIGHT")

print("\nNOTA: El slider ahora va de 0.1 a 20.0 (min=0.1)")

