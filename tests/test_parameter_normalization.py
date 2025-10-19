"""
Test rápido para verificar la normalización de parámetros
"""
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from model.map_model import MapModel
from controller.map_controller import MapController

def test_parameter_normalization():
    """Prueba que los parámetros normalizados funcionen correctamente"""
    print("=" * 60)
    print("Test de Normalización de Parámetros")
    print("=" * 60)
    
    # Crear modelo y controlador
    model = MapModel()
    controller = MapController(model)
    
    # Test 1: Parámetros de terreno normalizados
    print("\n1. Probando parámetros de terreno normalizados...")
    try:
        model.update_terrain_params(
            height_variation=10.0,
            terrain_roughness=75,
            seed=123
        )
        print("   ✅ height_variation y terrain_roughness aceptados")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Parámetros visuales normalizados
    print("\n2. Probando parámetros visuales normalizados...")
    try:
        model.update_visual_params(
            azimuth_angle=45.0,
            elevation_angle=30.0,
            num_contour_levels=25
        )
        print("   ✅ azimuth_angle y elevation_angle aceptados")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: Verificar que parámetros antiguos NO sean aceptados
    print("\n3. Probando que parámetros antiguos sean rechazados...")
    old_params_rejected = True
    
    # Intentar usar 'vh' (debería fallar silenciosamente - no hacer nada)
    try:
        model.update_terrain_params(vh=5.0)
        # Verificar que NO se actualizó
        if 'vh' in model.terrain_params:
            print("   ❌ 'vh' fue aceptado (no debería)")
            old_params_rejected = False
        else:
            print("   ✅ 'vh' no fue aceptado (correcto)")
    except Exception as e:
        print(f"   ✅ 'vh' rechazado con error: {e}")
    
    # Test 4: Handle rotation con parámetros normalizados
    print("\n4. Probando handle_rotation con parámetros normalizados...")
    try:
        # Generar mapa primero
        result = controller.initialize_map()
        if not result['ok']:
            print(f"   ❌ Error al inicializar mapa: {result.get('error')}")
            return False
        
        # Probar rotación
        result = controller.handle_rotation(
            azimuth_angle=90.0,
            elevation_angle=45.0
        )
        if result['ok']:
            print("   ✅ handle_rotation funciona con azimuth_angle/elevation_angle")
        else:
            print(f"   ❌ Error en handle_rotation: {result.get('error')}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 5: Reset rotation
    print("\n5. Probando reset_rotation...")
    try:
        result = controller.handle_reset_rotation()
        if result['ok']:
            print("   ✅ reset_rotation funciona correctamente")
        else:
            print(f"   ❌ Error en reset_rotation: {result.get('error')}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 6: Verificar valores finales
    print("\n6. Verificando valores finales en el modelo...")
    params = model.get_all_params()
    
    if 'height_variation' in params['terrain']:
        print(f"   ✅ terrain.height_variation = {params['terrain']['height_variation']}")
    else:
        print("   ❌ height_variation no encontrado")
        return False
    
    if 'terrain_roughness' in params['terrain']:
        print(f"   ✅ terrain.terrain_roughness = {params['terrain']['terrain_roughness']}")
    else:
        print("   ❌ terrain_roughness no encontrado")
        return False
    
    if 'azimuth_angle' in params['visual']:
        print(f"   ✅ visual.azimuth_angle = {params['visual']['azimuth_angle']}")
    else:
        print("   ❌ azimuth_angle no encontrado")
        return False
    
    if 'elevation_angle' in params['visual']:
        print(f"   ✅ visual.elevation_angle = {params['visual']['elevation_angle']}")
    else:
        print("   ❌ elevation_angle no encontrado")
        return False
    
    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS PASARON - Normalización correcta")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_parameter_normalization()
    sys.exit(0 if success else 1)
