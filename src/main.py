"""
Generador de Mapas Topográficos 3D - Aplicación Principal
Genera mapas topográficos holográficos con efecto de líneas flotantes
"""
import matplotlib.pyplot as plt
import os
import os
import socket
import argparse
import eel
import bottle

# Importar módulos locales
from terrain_generator import TopographicMapGenerator
from visualization import draw_map_3d, export_map_clean, export_preview_image, export_with_dialog, ensure_unique_path
from ui_controller import UIController
from config import TERRAIN_PARAMS, VISUAL_PARAMS, WINDOW_CONFIG, TERRAIN_SIZE


def _find_free_port(start_port: int = 8080, max_tries: int = 20) -> int:
    """Encuentra un puerto libre empezando desde start_port."""
    port = int(start_port)
    for _ in range(max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1
    return int(start_port)


def _prompt_host_port(default_port: int) -> tuple[str, int]:
    """Dialogo para elegir host/puerto. Devuelve (host, port).
    Si no se puede abrir una UI, hace fallback a entrada por consola.
    """
    host = '127.0.0.1'  # seguro por defecto
    port = int(default_port)
    try:
        import tkinter as tk
        from tkinter import simpledialog, messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            title='Configuración de servidor local',
            message='Por seguridad se usará 127.0.0.1 (solo tu equipo).\nPuedes cambiar el puerto si lo deseas.'
        )
        p = simpledialog.askinteger('Puerto', f'Introduce el puerto (libre):', initialvalue=port, minvalue=1024, maxvalue=65535)
        if p:
            port = int(p)
        # Preguntar si desea exponer en red local
        answer = messagebox.askyesno('Exposición en red local', '¿Deseas exponer el servidor en tu red local (0.0.0.0)?\nNo recomendado salvo que sepas lo que haces.')
        if answer:
            host = '0.0.0.0'
        root.destroy()
    except Exception:
        # Fallback por consola
        try:
            txt = input(f"Puerto [{port}]: ").strip()
            if txt:
                p = int(txt)
                if 1024 <= p <= 65535:
                    port = p
        except Exception:
            pass
        # Host por defecto 127.0.0.1
    return host, port


def _parse_args():
    parser = argparse.ArgumentParser(description='Generador de Mapas Topográficos 3D')
    parser.add_argument('--host', type=str, default=None, help='Host de escucha (127.0.0.1 por defecto)')
    parser.add_argument('--port', type=int, default=None, help='Puerto de escucha (8080 por defecto)')
    parser.add_argument('--no-browser', action='store_true', help='No abrir el navegador automáticamente')
    return parser.parse_args()


def main():
    """Funcion principal de la aplicación"""
    
    # Mensaje de bienvenida
    print("=" * 50)
    print("VISTAR (Visual Terrain Analytics Renderer) V1.4")
    print("=" * 50)
    print("- Mapa Topografico Isometrico de Contornos")
    print("- Parametros ajustables")
    print("- Exportable a PNG y SVG")
    print("- Deploy en localhost")
    print("=" * 50)
    
    # Inicializar generador de terreno
    generator = TopographicMapGenerator(
        width=TERRAIN_SIZE['width'],
        height=TERRAIN_SIZE['height']
    )
    generator.generate_terrain(**TERRAIN_PARAMS)
    
    # Configurar figura 3D
    fig = plt.figure(
        figsize=WINDOW_CONFIG['figsize'],
        facecolor=WINDOW_CONFIG['facecolor']
    )
    ax = fig.add_subplot(111, projection='3d')
    # Dejar espacio para barra superior y panel derecho
    # área grande izquierda: [left, bottom, width, height]
    ax.set_position([0.04, 0.10, 0.60, 0.82])
    fig.subplots_adjust(**WINDOW_CONFIG['subplots_adjust'])
    
    # Asignar figura y eje al generador
    generator.fig = fig
    generator.ax = ax
    
    # Callback para redibujar el mapa
    def redraw_map():
        show_axis_labels = VISUAL_PARAMS.get('show_axis_labels', True)
        line_color = VISUAL_PARAMS.get('line_color', '#00ffff')
        grid_color = VISUAL_PARAMS.get('grid_color', '#00ffff')
        grid_width = VISUAL_PARAMS.get('grid_width', 0.6)
        grid_opacity = VISUAL_PARAMS.get('grid_opacity', 0.35)
        draw_map_3d(
            generator,
            VISUAL_PARAMS['num_contour_levels'],
            VISUAL_PARAMS['elevation_angle'],
            VISUAL_PARAMS['azimuth_angle'],
            show_axis_labels=show_axis_labels,
            line_color=line_color,
            grid_color=grid_color,
            grid_width=grid_width,
            grid_opacity=grid_opacity
        )
    # Crear controlador de UI con el callback listo
    ui = UIController(fig, generator, TERRAIN_PARAMS, VISUAL_PARAMS, redraw_map)

    # Dibujar mapa inicial
    redraw_map()

    # Callback para exportar
    def export_callback(fmt):
        # Ignorar fmt y abrir diálogo para opciones completas
        export_with_dialog(generator, VISUAL_PARAMS)

    # Crear todos los controles
    ui.create_main_sliders()
    ui.create_seed_input()
    ui.create_buttons(export_callback)
    # Inicializar sliders de cráteres si están habilitados
    if TERRAIN_PARAMS['crater_enabled']:
        ui.create_crater_sliders()
    # --- Modo Eel (UI Web) ---
    # Prepara una imagen de previsualización inicial
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    preview_path = os.path.join(web_dir, 'tmp', 'preview.png')
    export_preview_image(generator, VISUAL_PARAMS, preview_path)

    # Exponer funciones a JS
    @eel.expose
    def api_get_state():
        return {
            'terrain': {
                'terrain_roughness': TERRAIN_PARAMS['terrain_roughness'],
                'height_variation': TERRAIN_PARAMS['height_variation'],
                'seed': TERRAIN_PARAMS['seed'],
                'crater_enabled': TERRAIN_PARAMS['crater_enabled'],
                'num_craters': TERRAIN_PARAMS['num_craters'],
                'crater_size': TERRAIN_PARAMS['crater_size'],
                'crater_depth': TERRAIN_PARAMS['crater_depth'],
            },
            'visual': VISUAL_PARAMS,
            'preview': 'tmp/preview.png'
        }

    @eel.expose
    def api_update(params: dict):
        # Actualiza parámetros y re-render
        TERRAIN_PARAMS.update(params.get('terrain', {}))
        # Clamp/normalizar semilla por seguridad
        try:
            s = int(TERRAIN_PARAMS.get('seed', 1))
        except Exception:
            s = 1
        if s < 1:
            s = 1
        TERRAIN_PARAMS['seed'] = int(abs(s)) % 10_000_000 or 1
        VISUAL_PARAMS.update(params.get('visual', {}))
        generator.generate_terrain(**TERRAIN_PARAMS)
        export_preview_image(generator, VISUAL_PARAMS, preview_path)
        return {'ok': True, 'preview': 'tmp/preview.png'}

    @eel.expose
    def api_random_seed():
        import random
        TERRAIN_PARAMS['seed'] = random.randint(1, 10_000_000)
        generator.generate_terrain(**TERRAIN_PARAMS)
        export_preview_image(generator, VISUAL_PARAMS, preview_path)
        return {'seed': TERRAIN_PARAMS['seed'], 'preview': 'tmp/preview.png'}

    @eel.expose
    def api_export(fmt: str):
        # UI Web: intentar abrir diálogo local si corre en escritorio.
        # Si falla (servidor headless), exportar por defecto a generados.
        ok = False
        try:
            ok = export_with_dialog(generator, VISUAL_PARAMS)
        except Exception:
            ok = export_map_clean(generator, VISUAL_PARAMS, fmt)
        return {'ok': bool(ok)}

    @eel.expose
    def api_export_options(opts: dict):
        """Exporta respetando las opciones enviadas desde el modal web.
        opts: { fmt: 'png'|'svg', includeGrid: bool, scale: 1|2|4, path: string }
        """
        fmt = str(opts.get('fmt', 'png')).lower()
        if fmt not in ('png', 'svg'):
            fmt = 'png'
        include_grid = bool(opts.get('includeGrid', VISUAL_PARAMS.get('show_axis_labels', True)))
        try:
            scale = int(opts.get('scale', 1))
        except Exception:
            scale = 1
        if scale not in (1, 2, 4):
            scale = 1
        path = opts.get('path')
        if path:
            path = str(path)
        else:
            path = None
        ok = export_map_clean(generator, VISUAL_PARAMS, fmt=fmt, save_path=path, include_grid=include_grid, scale=scale)
        return {'ok': bool(ok)}

    @eel.expose
    def api_suggest_download_path():
        """Devuelve una ruta sugerida en Descargas con nombre por defecto y extensión PNG."""
        from datetime import datetime
        home = os.path.expanduser('~')
        candidates = [
            os.path.join(home, 'Downloads'),
            os.path.join(home, 'Descargas'),
        ]
        base_dir = None
        for c in candidates:
            if os.path.isdir(c):
                base_dir = c; break
        if base_dir is None:
            base_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'generados')
        try:
            os.makedirs(base_dir, exist_ok=True)
        except Exception:
            pass
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join(base_dir, f'mapa_topografico_3d_{ts}.png')

    @eel.expose
    def api_browse_save_path(opts: dict):
        """Abre un diálogo nativo de guardar cuando es posible (entorno con Tk)."""
        fmt = str(opts.get('fmt', 'png')).lower()
        if fmt not in ('png', 'svg'):
            fmt = 'png'
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk(); root.withdraw()
            filetypes = [('PNG Image', '*.png')] if fmt == 'png' else [('SVG Vector', '*.svg')]
            initial = api_suggest_download_path()
            # Ejecutar diálogo sin mainloop y destruir inmediatamente
            try:
                chosen = filedialog.asksaveasfilename(title='Guardar como', defaultextension=f'.{fmt}', filetypes=filetypes, initialfile=os.path.basename(initial), initialdir=os.path.dirname(initial))
            finally:
                try:
                    root.update_idletasks(); root.destroy()
                except Exception:
                    pass
            return chosen or ''
        except Exception:
            return ''

    @eel.expose
    def api_reset_view():
        VISUAL_PARAMS['azimuth_angle'] = 340
        VISUAL_PARAMS['elevation_angle'] = 20
        export_preview_image(generator, VISUAL_PARAMS, preview_path)
        return {'ok': True, 'preview': 'tmp/preview.png', 'az': 340, 'el': 20}

    # Lanzar Eel con despliegue "universal" configurable
    eel.init(web_dir)

    # Ruta HTTP para que el navegador gestione la descarga (Edge/Chrome Download Manager)
    @bottle.route('/export')
    def http_export():
        from datetime import datetime
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
        tmp_dir = os.path.join(web_dir, 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        desired = os.path.join(tmp_dir, f'mapa_topografico_3d_{ts}.{fmt}')
        final_path = ensure_unique_path(desired)
        export_map_clean(generator, VISUAL_PARAMS, fmt=fmt, save_path=final_path, include_grid=include_grid, scale=scale)
        if not os.path.isfile(final_path):
            bottle.response.status = 500
            return 'Export failed'
        return bottle.static_file(os.path.basename(final_path), root=os.path.dirname(final_path), download=os.path.basename(final_path))

    args = _parse_args()
    env_port = os.environ.get('PORT')
    # Determinar puerto inicial
    chosen_port = args.port or (int(env_port) if env_port and env_port.isdigit() else None)
    if not chosen_port:
        # Sugerir un puerto libre
        candidate = _find_free_port(8080)
        # Dialogo/entrada interactiva
        host, chosen_port = _prompt_host_port(candidate)
    else:
        host = args.host or '127.0.0.1'

    # Si el puerto elegido está ocupado, intentar siguiente libre
    free_check = _find_free_port(chosen_port)
    if free_check != chosen_port and host == '127.0.0.1':
        print(f"Puerto {chosen_port} en uso. Usando {free_check}...")
        chosen_port = free_check

    start_kwargs = dict(host=host, port=int(chosen_port), size=(1280, 800), block=True)
    index_page = 'index.html'

    if args.no_browser:
        # No abrir navegador, iniciar servidor solamente
        eel.start(index_page, mode=None, **start_kwargs)
    else:
        # Dejar que Eel elija el navegador por defecto
        try:
            eel.start(index_page, **start_kwargs)
        except OSError as e:
            print('No se pudo abrir el navegador por defecto. Iniciando sin navegador...')
            print('Error:', e)
            eel.start(index_page, mode=None, **start_kwargs)


if __name__ == '__main__':
    main()
