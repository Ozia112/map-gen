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
        # Intentar preparar vendor de Three.js para modo offline al iniciar
        try:
            self._ensure_vendor_three()
        except Exception as e:
            print(f"Aviso: no se pudo preparar vendor de Three.js al iniciar: {e}")
    
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
                    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')),
                    'generados'
                )
            
            try:
                os.makedirs(base_dir, exist_ok=True)
            except Exception:
                pass
            
            return base_dir
        
        @eel.expose
        def api_select_save_path():
            """Abre un diálogo para seleccionar carpeta de guardado"""
            try:
                import tkinter as tk
                from tkinter import filedialog
                
                # Crear ventana raíz oculta
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                
                # Obtener ruta inicial sugerida
                initial_dir = api_suggest_download_path()
                
                # Abrir diálogo de selección de carpeta
                folder_path = filedialog.askdirectory(
                    title='Seleccionar carpeta para guardar',
                    initialdir=initial_dir
                )
                
                root.destroy()
                
                # Retornar la ruta seleccionada o None si se canceló
                return folder_path if folder_path else None
                
            except Exception as e:
                print(f"Error al abrir diálogo: {e}")
                return None
        
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

        @eel.expose
        def api_prepare_offline_three():
            """Descarga archivos de Three.js en vendor/ para modo offline (una sola vez)."""
            try:
                import urllib.request
                base = os.path.join(self.web_dir, 'vendor', 'three', '0.157.0')
                paths = {
                    os.path.join(base, 'build', 'three.module.js'): 'https://unpkg.com/three@0.157.0/build/three.module.js',
                    os.path.join(base, 'examples', 'jsm', 'controls', 'OrbitControls.js'): 'https://unpkg.com/three@0.157.0/examples/jsm/controls/OrbitControls.js',
                    os.path.join(base, 'examples', 'jsm', 'renderers', 'SVGRenderer.js'): 'https://unpkg.com/three@0.157.0/examples/jsm/renderers/SVGRenderer.js',
                    os.path.join(base, 'examples', 'jsm', 'exporters', 'OBJExporter.js'): 'https://unpkg.com/three@0.157.0/examples/jsm/exporters/OBJExporter.js',
                }
                for p in paths.keys():
                    os.makedirs(os.path.dirname(p), exist_ok=True)
                downloaded = []
                for out_path, url in paths.items():
                    try:
                        with urllib.request.urlopen(url, timeout=30) as r:
                            content = r.read()
                        with open(out_path, 'wb') as f:
                            f.write(content)
                        downloaded.append(os.path.relpath(out_path, self.web_dir))
                    except Exception as e:
                        return {'ok': False, 'error': f'No se pudo descargar {url}: {e}'}
                return {'ok': True, 'files': downloaded}
            except Exception as e:
                return {'ok': False, 'error': str(e)}
    
    def setup_http_routes(self):
        """Configura rutas HTTP para descarga de archivos"""
        # Basic pages routing
        @bottle.route('/')
        @bottle.route('/home')
        def http_home():
            return bottle.static_file('index.html', root=self.web_dir)

        @bottle.route('/laboratorio-3d')
        def http_laboratorio():
            return bottle.static_file('laboratorio-3d.html', root=self.web_dir)

        @bottle.route('/lab3d')
        def http_legacy_lab3d():
            bottle.response.status = 301
            bottle.response.set_header('Location', '/laboratorio-3d')
            return ''

        # Serve local vendor libs for offline usage
        @bottle.route('/vendor/<path:path>')
        def http_vendor(path):
            vendor_root = os.path.join(self.web_dir, 'vendor')
            return bottle.static_file(path, root=vendor_root)
        
        # Serve home directory for JavaScript modules
        @bottle.route('/home/<filename>')
        def http_home_files(filename):
            home_root = os.path.join(self.web_dir, 'home')
            return bottle.static_file(filename, root=home_root)
        
        # Serve lab3d directory for JavaScript modules
        @bottle.route('/lab3d/<filename>')
        def http_lab3d_files(filename):
            lab3d_root = os.path.join(self.web_dir, 'lab3d')
            return bottle.static_file(filename, root=lab3d_root)
        
        # Serve laboratorio-3d directory for JavaScript modules
        @bottle.route('/laboratorio-3d/<filename>')
        def http_laboratorio_3d_files(filename):
            laboratorio_root = os.path.join(self.web_dir, 'laboratorio-3d')
            return bottle.static_file(filename, root=laboratorio_root)
        
        # Serve tmp directory for preview images
        @bottle.route('/tmp/<filename>')
        def http_tmp(filename):
            tmp_root = os.path.join(self.web_dir, 'tmp')
            return bottle.static_file(filename, root=tmp_root)
        
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
        
        # Catch-all route for other static files (CSS, JS, etc.) in web root
        @bottle.route('/<filename:re:.*\\.(js|css|png|jpg|jpeg|gif|svg|ico)$>')
        def http_static_files(filename):
            return bottle.static_file(filename, root=self.web_dir)
    
    def _generate_preview(self):
        """Genera la imagen de preview usando el modelo actual"""
        from view.visualization import export_preview_image
        
        generator = self.map_controller.model.generator
        visual_params = self.map_controller.model.visual_params
        
        export_preview_image(generator, visual_params, self.preview_path)
    
    def initialize_preview(self):
        """Genera el preview inicial al arrancar la aplicación"""
        self._generate_preview()

    def _ensure_vendor_three(self):
        """Verifica y descarga (si faltan) los archivos de Three.js a vendor/."""
        base = os.path.join(self.web_dir, 'vendor', 'three', '0.157.0')
        targets = [
            (os.path.join(base, 'build', 'three.module.js'), [
                'https://unpkg.com/three@0.157.0/build/three.module.js',
                'https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.module.js'
            ]),
            (os.path.join(base, 'examples', 'jsm', 'controls', 'OrbitControls.js'), [
                'https://unpkg.com/three@0.157.0/examples/jsm/controls/OrbitControls.js',
                'https://cdn.jsdelivr.net/npm/three@0.157.0/examples/jsm/controls/OrbitControls.js'
            ]),
            (os.path.join(base, 'examples', 'jsm', 'renderers', 'SVGRenderer.js'), [
                'https://unpkg.com/three@0.157.0/examples/jsm/renderers/SVGRenderer.js',
                'https://cdn.jsdelivr.net/npm/three@0.157.0/examples/jsm/renderers/SVGRenderer.js'
            ]),
            (os.path.join(base, 'examples', 'jsm', 'exporters', 'OBJExporter.js'), [
                'https://unpkg.com/three@0.157.0/examples/jsm/exporters/OBJExporter.js',
                'https://cdn.jsdelivr.net/npm/three@0.157.0/examples/jsm/exporters/OBJExporter.js'
            ]),
        ]
        import urllib.request
        for out_path, urls in targets:
            if os.path.isfile(out_path) and os.path.getsize(out_path) > 1024:
                continue
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            last_err = None
            for url in urls:
                try:
                    with urllib.request.urlopen(url, timeout=30) as r:
                        content = r.read()
                    with open(out_path, 'wb') as f:
                        f.write(content)
                    last_err = None
                    print(f"Descargado vendor: {url} -> {out_path}")
                    break
                except Exception as e:
                    last_err = e
            if last_err:
                raise last_err
