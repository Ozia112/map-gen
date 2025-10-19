"""
Test para verificar que terrain_stats se devuelva correctamente
"""
import sys
sys.path.insert(0, 'src')

from model.map_model import MapModel
from controller.map_controller import MapController

# Crear modelo y controlador
model = MapModel()
controller = MapController(model)

# Generar mapa inicial
result = controller.initialize_map()
print("=== Resultado de initialize_map ===")
print(f"OK: {result.get('ok')}")
print(f"Preview: {result.get('preview')}")

# Verificar params
if 'params' in result:
    params = result['params']
    print("\n=== Parámetros ===")
    print(f"Terrain: {params.get('terrain', {}).keys()}")
    print(f"Visual: {params.get('visual', {}).keys()}")
    print(f"Crater: {params.get('crater', {}).keys()}")
    
    if 'terrain_stats' in params:
        stats = params['terrain_stats']
        print(f"\n✅ terrain_stats encontrado:")
        print(f"   Min height: {stats.get('min_height')}")
        print(f"   Max height: {stats.get('max_height')}")
    else:
        print("\n❌ terrain_stats NO encontrado en params")

# Probar get_all_params directamente
print("\n=== Prueba directa de get_all_params ===")
all_params = model.get_all_params()
print(f"Keys: {all_params.keys()}")
if 'terrain_stats' in all_params:
    print(f"✅ terrain_stats: {all_params['terrain_stats']}")
else:
    print("❌ terrain_stats NO está en get_all_params")
