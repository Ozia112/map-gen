"""
View Controller - Maneja la interacción con la interfaz web mediante Eel
Actúa como adaptador entre el controlador y la vista (HTML/JS)
"""
import os
import sys
import eel
import bottle
from typing import Dict, Any, Callable
from datetime import datetime

# Asegurar que el directorio src esté en el path
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class WebViewController:
    """
    Controlador de vista web que expone APIs para la interfaz HTML/JS.
    Responsable de:
    - Exponer endpoints Eel para la comunicación JS ↔ Python
    - Manejar rutas HTTP para exportación
    - Gestionar archivos temporales de preview
    - Delegar lógica de negocio al MapController
    """
    
    def __init__(self, map_controller, web_dir: str, preview_dir: str = "tmp"):
        """
        Inicializa el controlador de vista web.
        
        Args:
            map_controller: Instancia de MapController para delegar operaciones
            web_dir: Directorio con archivos estáticos (HTML/CSS/JS)
            preview_dir: Subdirectorio para imágenes de preview
        """
        self.map_controller = map_controller
        self.web_dir = web_dir
        self.preview_dir = os.path.join(web_dir, preview_dir)
        
        # Asegurar que existe el directorio de previews
        os.makedirs(self.preview_dir, exist_ok=True)
        
        # Ruta del preview actual
        self.preview_path = os.path.join(self.preview_dir, 'preview.png')
        
        # Limpiar archivos antiguos al iniciar
        self._cleanup_old_files()
    
    def _cleanup_old_files(self, keep_files=None):
        """
        Limpia archivos antiguos del directorio tmp.
        
        Args:
            keep_files: Lista de nombres de archivos a conservar (opcional)
        """
        if keep_files is None:
            keep_files = ['preview.png']
        
        try:
            for filename in os.listdir(self.preview_dir):
                if filename not in keep_files:
                    file_path = os.path.join(self.preview_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            print(f"Archivo temporal eliminado: {filename}")
                    except Exception as e:
                        print(f"No se pudo eliminar {filename}: {e}")
        except Exception as e:
            print(f"Error al limpiar archivos temporales: {e}")
        
    def setup_eel_routes(self):
        """Registra todas las rutas Eel para comunicación con JS"""
        
        @eel.expose
        def api_get_state():
            """Obtiene el estado actual del modelo"""
            state = self.map_controller.get_current_state()
            result = {
                'terrain': state['params']['terrain'],
                'visual': state['params']['visual'],
                'craters': state['params'].get('crater', {}),
                'preview': 'tmp/preview.png'
            }
            # Agregar estadísticas del terreno si existen
            if 'terrain_stats' in state['params']:
                result['terrain_stats'] = state['params']['terrain_stats']
            return result
        
        @eel.expose
        def api_update(params: dict):
            """Actualiza parámetros y regenera el mapa"""
            result = self.map_controller.handle_update(params)
            if result['ok']:
                # Generar preview
                self._generate_preview()
                result['preview'] = 'tmp/preview.png'
                # Agregar estadísticas del terreno si existen
                if 'params' in result and 'terrain_stats' in result['params']:
                    result['terrain_stats'] = result['params']['terrain_stats']
            return result
        
        @eel.expose
        def api_random_seed():
            """Genera una semilla aleatoria"""
            import random
            seed = random.randint(1, 10_000_000)
            result = self.map_controller.handle_terrain_update(seed=seed)
            if result['ok']:
                self._generate_preview()
                result['preview'] = 'tmp/preview.png'
                # Agregar estadísticas del terreno si existen
                if 'params' in result and 'terrain_stats' in result['params']:
                    result['terrain_stats'] = result['params']['terrain_stats']
            return result
        
        @eel.expose
        def api_export_options(opts: dict):
            """
            Exporta el mapa con opciones específicas.
            opts: { fmt: 'png'|'svg', includeGrid: bool, scale: 1|2|4, path: string }
            """
            export_params = {
                'format': opts.get('fmt', 'png'),
                'path': opts.get('path'),
                'scale': opts.get('scale', 1),
                'include_grid': opts.get('includeGrid', True)
            }
            return self.map_controller.handle_export(export_params)
        
        @eel.expose
        def api_suggest_download_path():
            """Devuelve una ruta sugerida para descargas"""
            home = os.path.expanduser('~')
            candidates = [
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Descargas'),
            ]
            base_dir = None
            for c in candidates:
                if os.path.isdir(c):
                    base_dir = c
                    break
            
            if base_dir is None:
                base_dir = os.path.join(
                    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                    'generados'
                )
            
            try:
                os.makedirs(base_dir, exist_ok=True)
            except Exception:
                pass
            
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            return os.path.join(base_dir, f'mapa_topografico_3d_{ts}.png')
        
        @eel.expose
        def api_browse_save_path(opts: dict):
            """Abre un diálogo nativo de guardar (si está disponible)"""
            fmt = str(opts.get('fmt', 'png')).lower()
            if fmt not in ('png', 'svg'):
                fmt = 'png'
            
            try:
                import tkinter as tk
                from tkinter import filedialog
                
                root = tk.Tk()
                root.withdraw()
                
                filetypes = [('PNG Image', '*.png')] if fmt == 'png' else [('SVG Vector', '*.svg')]
                initial = api_suggest_download_path()
                
                try:
                    chosen = filedialog.asksaveasfilename(
                        title='Guardar como',
                        defaultextension=f'.{fmt}',
                        filetypes=filetypes,
                        initialfile=os.path.basename(initial),
                        initialdir=os.path.dirname(initial)
                    )
                finally:
                    try:
                        root.update_idletasks()
                        root.destroy()
                    except Exception:
                        pass
                
                return chosen or ''
            except Exception:
                return ''
        
        @eel.expose
        def api_reset_view():
            """Resetea la vista a ángulos por defecto"""
            result = self.map_controller.handle_reset_rotation()
            if result['ok']:
                self._generate_preview()
                result['preview'] = 'tmp/preview.png'
            return result
        
        @eel.expose
        def api_get_heightmap():
            """Devuelve el mapa de alturas como JSON para WebGL"""
            generator = self.map_controller.model.generator
            return generator.get_heightmap_payload()
        
        @eel.expose
        def api_set_heightmap(payload: dict):
            """Inyecta un mapa de alturas externo desde JSON"""
            try:
                z = payload.get('z')
                if not z:
                    return {'ok': False, 'error': 'z vacío'}
                
                generator = self.map_controller.model.generator
                generator.set_heightmap(z, normalize=True)
                self._generate_preview()
                
                return {'ok': True, 'preview': 'tmp/preview.png'}
            except Exception as e:
                return {'ok': False, 'error': str(e)}
    
    def setup_http_routes(self):
        """Configura rutas HTTP para descarga de archivos"""
        
        @bottle.route('/export')
        def http_export():
            """Endpoint HTTP para exportación con descarga directa"""
            from view.visualization import export_map_clean, ensure_unique_path
            
            q = bottle.request.query
            fmt = str(q.get('fmt', 'png')).lower()
            include_grid = str(q.get('includeGrid', '1')).lower() in ('1', 'true', 'yes')
            
            try:
                scale = int(q.get('scale', '1'))
            except Exception:
                scale = 1
            
            if fmt not in ('png', 'svg'):
                fmt = 'png'
            if scale not in (1, 2, 4):
                scale = 1
            
            tmp_dir = os.path.join(self.web_dir, 'tmp')
            os.makedirs(tmp_dir, exist_ok=True)
            
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            desired = os.path.join(tmp_dir, f'mapa_topografico_3d_{ts}.{fmt}')
            final_path = ensure_unique_path(desired)
            
            # Usar el generador del modelo
            generator = self.map_controller.model.generator
            visual_params = self.map_controller.model.visual_params
            
            export_map_clean(
                generator, visual_params,
                fmt=fmt, save_path=final_path,
                include_grid=include_grid, scale=scale
            )
            
            if not os.path.isfile(final_path):
                bottle.response.status = 500
                return 'Export failed'
            
            # Limpiar archivos antiguos, manteniendo solo el preview y el recién exportado
            self._cleanup_old_files(keep_files=['preview.png', os.path.basename(final_path)])
            
            return bottle.static_file(
                os.path.basename(final_path),
                root=os.path.dirname(final_path),
                download=os.path.basename(final_path)
            )
    
    def _generate_preview(self):
        """Genera la imagen de preview usando el modelo actual"""
        from view.visualization import export_preview_image
        
        generator = self.map_controller.model.generator
        visual_params = self.map_controller.model.visual_params
        
        export_preview_image(generator, visual_params, self.preview_path)
    
    def initialize_preview(self):
        """Genera el preview inicial al arrancar la aplicación"""
        self._generate_preview()
