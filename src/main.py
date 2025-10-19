"""
Generador de Mapas Topográficos 3D - Aplicación Principal
Punto de entrada que inicializa el patrón MVC y lanza el servidor web
"""
import os
import socket
import argparse
import eel

# Importar componentes MVC
from model.map_model import MapModel
from controller.map_controller import MapController
from view.web_view_controller import WebViewController


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
    """
    Diálogo para elegir host/puerto. Devuelve (host, port).
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
        
        p = simpledialog.askinteger(
            'Puerto',
            f'Introduce el puerto (libre):',
            initialvalue=port,
            minvalue=1024,
            maxvalue=65535
        )
        if p:
            port = int(p)
        
        # Preguntar si desea exponer en red local
        answer = messagebox.askyesno(
            'Exposición en red local',
            '¿Deseas exponer el servidor en tu red local (0.0.0.0)?\nNo recomendado salvo que sepas lo que haces.'
        )
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
    
    return host, port


def _parse_args():
    """Parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description='Generador de Mapas Topográficos 3D')
    parser.add_argument('--host', type=str, default=None, help='Host de escucha (127.0.0.1 por defecto)')
    parser.add_argument('--port', type=int, default=None, help='Puerto de escucha (8080 por defecto)')
    parser.add_argument('--no-browser', action='store_true', help='No abrir el navegador automáticamente')
    return parser.parse_args()


def main():
    """Función principal de la aplicación"""
    
    # ========== INICIALIZACIÓN MVC ==========
    
    # MODELO: Estado de la aplicación
    model = MapModel()
    
    # CONTROLADOR: Lógica de negocio
    controller = MapController(model)
    
    # VISTA: Interfaz web
    web_dir = os.path.join(os.path.dirname(__file__), 'view', 'web')
    view_controller = WebViewController(controller, web_dir)
    
    # Configurar rutas Eel y HTTP
    eel.init(web_dir)
    view_controller.setup_eel_routes()
    view_controller.setup_http_routes()
    
    # Generar mapa inicial y preview
    result = controller.initialize_map()
    if not result.get('ok', False):
        print(f"Error al inicializar el mapa: {result.get('error', 'Error desconocido')}")
        return
    view_controller.initialize_preview()
    
    # ========== CONFIGURACIÓN DEL SERVIDOR ==========
    
    args = _parse_args()
    env_port = os.environ.get('PORT')
    
    # Determinar puerto inicial
    chosen_port = args.port or (int(env_port) if env_port and env_port.isdigit() else None)
    
    if not chosen_port:
        # Sugerir un puerto libre
        candidate = _find_free_port(8080)
        # Diálogo/entrada interactiva
        host, chosen_port = _prompt_host_port(candidate)
    else:
        host = args.host or '127.0.0.1'
    
    # Si el puerto elegido está ocupado, intentar siguiente libre
    free_check = _find_free_port(chosen_port)
    if free_check != chosen_port and host == '127.0.0.1':
        print(f"Puerto {chosen_port} en uso. Usando {free_check}...")
        chosen_port = free_check
    
    # ========== MENSAJE DE BIENVENIDA ==========
    
    lan_mode = (str(host) == '0.0.0.0')
    
    print("=" * 50)
    print("VISTAR (Visual Terrain Analytics Renderer) V2.0")
    print("=" * 50)
    print("- Mapa Topografico Isometrico de Contornos")
    print("- Parametros ajustables en tiempo real")
    print("- Exportable a PNG y SVG de alta resolucion")
    print(f"- Modo servidor: {'LAN (0.0.0.0)' if lan_mode else 'Local (127.0.0.1)'}")
    print(f"- Puerto: {int(chosen_port)}")
    print(f"- URL: http://{host}:{int(chosen_port)}")
    
    if lan_mode:
        print(f"- URL local: http://127.0.0.1:{int(chosen_port)}")
    
    print("=" * 50)
    
    # ========== INICIO DEL SERVIDOR ==========
    
    start_kwargs = dict(
        host=host,
        port=int(chosen_port),
        size=(1280, 800),
        block=True
    )
    
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
