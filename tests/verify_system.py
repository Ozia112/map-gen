"""
Script de verificación del sistema
Comprueba que todas las importaciones y componentes MVC funcionen correctamente
"""
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Verifica que todos los imports funcionen"""
    print("🔍 Verificando importaciones...")
    
    try:
        from model.map_model import MapModel
        print("  ✅ MapModel importado correctamente")
    except Exception as e:
        print(f"  ❌ Error importando MapModel: {e}")
        return False
    
    try:
        from controller.map_controller import MapController
        print("  ✅ MapController importado correctamente")
    except Exception as e:
        print(f"  ❌ Error importando MapController: {e}")
        return False
    
    try:
        from controller.render_controller import RenderController
        print("  ✅ RenderController importado correctamente")
    except Exception as e:
        print(f"  ❌ Error importando RenderController: {e}")
        return False
    
    try:
        from view.web_view_controller import WebViewController
        print("  ✅ WebViewController importado correctamente")
    except Exception as e:
        print(f"  ❌ Error importando WebViewController: {e}")
        return False
    
    return True


def test_model():
    """Verifica funcionalidad básica del modelo"""
    print("\n🧪 Probando MapModel...")
    
    try:
        from model.map_model import MapModel
        
        model = MapModel()
        print("  ✅ MapModel instanciado")
        
        model.update_terrain_params(seed=999, vh=10.0)
        print("  ✅ Parámetros de terreno actualizados")
        
        model.update_visual_params(azimuth=200.0)
        print("  ✅ Parámetros visuales actualizados")
        
        heightmap = model.generate()
        print("  ✅ Heightmap generado")
        
        assert heightmap is not None
        print("  ✅ Heightmap válido")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error en MapModel: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_controller():
    """Verifica funcionalidad básica del controlador"""
    print("\n🎮 Probando MapController...")
    
    try:
        from model.map_model import MapModel
        from controller.map_controller import MapController
        
        model = MapModel()
        controller = MapController(model)
        print("  ✅ MapController instanciado")
        
        result = controller.handle_update({
            'terrain': {'seed': 777}
        })
        print(f"  ✅ handle_update ejecutado: ok={result['ok']}")
        
        assert result['ok'] is True
        print("  ✅ Actualización exitosa")
        
        state = controller.get_current_state()
        print("  ✅ Estado actual obtenido")
        
        assert 'params' in state
        print("  ✅ Estado contiene parámetros")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error en MapController: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Verifica que la configuración sea válida"""
    print("\n⚙️  Verificando configuración...")
    
    try:
        from config import (
            SERVER_CONFIG,
            TERRAIN_PARAMS,
            VISUAL_PARAMS,
            CRATER_PARAMS,
            DEFAULT_WIDTH,
            DEFAULT_HEIGHT
        )
        
        print("  ✅ SERVER_CONFIG cargado")
        print("  ✅ TERRAIN_PARAMS cargado")
        print("  ✅ VISUAL_PARAMS cargado")
        print("  ✅ CRATER_PARAMS cargado")
        print("  ✅ DEFAULT_WIDTH y DEFAULT_HEIGHT cargados")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error en configuración: {e}")
        return False


def check_dependencies():
    """Verifica dependencias instaladas"""
    print("\n📦 Verificando dependencias...")
    
    dependencies = {
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'noise': 'noise',
    }
    
    all_ok = True
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"  ✅ {name} instalado")
        except ImportError:
            print(f"  ❌ {name} no encontrado")
            all_ok = False
    
    # Eel es opcional para tests
    try:
        import eel
        print("  ✅ eel instalado (opcional)")
    except ImportError:
        print("  ⚠️  eel no instalado (necesario para UI web)")
    
    return all_ok


def main():
    """Ejecuta todas las verificaciones"""
    print("=" * 50)
    print("🔬 VISTAR - Verificación del Sistema MVC")
    print("=" * 50)
    
    results = []
    
    # Verificar dependencias
    results.append(("Dependencias", check_dependencies()))
    
    # Verificar configuración
    results.append(("Configuración", test_config()))
    
    # Verificar imports
    results.append(("Importaciones", test_imports()))
    
    # Verificar modelo
    results.append(("Modelo", test_model()))
    
    # Verificar controlador
    results.append(("Controlador", test_controller()))
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 Resumen de Verificación")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("\n✨ ¡Todas las verificaciones pasaron exitosamente!")
        print("🚀 El sistema está listo para ejecutarse.")
        print("\n💡 Para iniciar la aplicación, ejecuta:")
        print("   python run.py")
        return 0
    else:
        print("\n⚠️  Algunas verificaciones fallaron.")
        print("Por favor revisa los errores arriba.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
