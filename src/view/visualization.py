"""
Módulo de visualización 3D del terreno
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import os
def ensure_unique_path(path: str) -> str:
    """Devuelve una ruta única añadiendo ' (n)' si el archivo ya existe."""
    base, ext = os.path.splitext(path)
    if not os.path.exists(path):
        return path
    n = 1
    while True:
        candidate = f"{base} ({n}){ext}"
        if not os.path.exists(candidate):
            return candidate
        n += 1


# ---- Utilidades compartidas y caché de meshgrid ----
def _get_meshgrid(generator):
    """Devuelve X_mesh, Y_mesh cacheados según dimensiones actuales."""
    W, H = generator.width, generator.height
    cache = getattr(generator, '_cached_grid', None)
    if not cache or cache.get('shape') != (W, H):
        X = np.linspace(0, W - 1, W)
        Y = np.linspace(0, H - 1, H)
        X_mesh, Y_mesh = np.meshgrid(X, Y)
        generator._cached_grid = {'shape': (W, H), 'X': X_mesh, 'Y': Y_mesh}
    return generator._cached_grid['X'], generator._cached_grid['Y']

def _compute_z_base(min_h: float, max_h: float) -> float:
    """
    Calcula la base del mapa 3D.
    Como ahora todos los terrenos tienen BASE_HEIGHT=2.0 mínimo,
    ponemos la base en 0 para mostrar toda la altura del "pastel"
    """
    return 0.0

def _compute_adaptive_ticks(z_min: float, z_max: float):
    """
    Calcula ticks adaptativos para el eje Z basándose en el rango de altura.
    Evita tener muchos ticks en espacios pequeños ajustando el intervalo.
    
    Args:
        z_min: Altura mínima
        z_max: Altura máxima
        
    Returns:
        array de posiciones de ticks
    """
    z_range = z_max - z_min
    
    # Determinar intervalo óptimo basado en el rango
    if z_range <= 5:
        interval = 1
    elif z_range <= 10:
        interval = 2
    elif z_range <= 20:
        interval = 5
    elif z_range <= 50:
        interval = 10
    elif z_range <= 100:
        interval = 20
    else:
        interval = 50
    
    # Generar ticks alineados al intervalo
    start = np.ceil(z_min / interval) * interval
    end = np.floor(z_max / interval) * interval
    
    if start > end:
        # Si el rango es muy pequeño, usar al menos 2 ticks
        return np.array([z_min, z_max])
    
    return np.arange(start, end + interval, interval)

def _compute_levels(min_h: float, max_h: float, nlevels: int):
    """
    Calcula niveles de contorno. 
    Si el terreno es plano (min_h == max_h), genera niveles igualmente espaciados
    alrededor de la altura para visualización.
    """
    n = max(1, int(nlevels))
    
    if max_h <= min_h:
        # Terreno plano: crear niveles artificiales para visualización
        # Distribuir niveles alrededor de la altura actual
        base_height = min_h if min_h > 0 else 2.0
        step = base_height / (n + 1)
        return np.arange(step, base_height, step)
    
    # Terreno con variación: niveles normales
    step = (max_h - min_h) / n
    return np.arange(min_h + step, max_h, step)


def draw_map_3d(generator, num_contour_levels, elevation_angle, azimuth_angle, show_axis_labels=True, line_color='#ff7825', sea_level=0.0, grid_color='#00ffff', grid_width=0.6, grid_opacity=0.35):
    """Dibuja el mapa topográfico 3D con líneas flotantes y caja en las esquinas"""
    # Verificar que el terreno esté generado
    if generator.terrain is None:
        raise ValueError("No hay terreno generado. Llama a generate_terrain() primero.")
    
    if generator.ax is not None:
        generator.ax.clear()
    # Meshgrid cacheado
    X_mesh, Y_mesh = _get_meshgrid(generator)
    Z_mesh = generator.terrain.T
    
    min_h = float(Z_mesh.min())
    max_h = float(Z_mesh.max())
    z_base = _compute_z_base(min_h, max_h)
    
    # Calcular niveles de contorno - siempre genera niveles, incluso para terreno plano
    levels = _compute_levels(min_h, max_h, num_contour_levels)
    
    # DEBUG: Ver valores de sea_level
    print(f"DEBUG draw_map_3d: sea_level={sea_level}, min_h={min_h:.2f}, max_h={max_h:.2f}")
    print(f"DEBUG levels: {[f'{l:.2f}' for l in levels[:5]]}{'...' if len(levels) > 5 else ''}")
    
    # Dibujar líneas de contorno en su altura real (efecto holograma)
    if len(levels) > 0:
        for level in levels:
            # Líneas punteadas bajo el nivel del mar, sólidas arriba
            linestyle = 'dashed' if level < sea_level else 'solid'
            print(f"DEBUG nivel {level:.2f}: {'PUNTEADA' if level < sea_level else 'SÓLIDA'} (sea_level={sea_level})")
            generator.ax.contour(
                X_mesh, Y_mesh, Z_mesh,
                levels=[level],
                colors=line_color,
                linewidths=1.2,
                linestyles=[linestyle],  # Pasar como lista
                alpha=0.8,
                zorder=5,
                zdir='z',
                offset=level
            )
        
        # Soportes y caja - siempre se dibujan
        corners = [
            (0, 0),
            (generator.width - 1, 0),
            (generator.width - 1, generator.height - 1),
            (0, generator.height - 1)
        ]
        # Verticales (soportes)
        for i, j in corners:
            z_val = generator.terrain[i, j]
            generator.ax.plot([i, i], [j, j], [z_base, z_val], color=line_color, alpha=0.6, linewidth=1.5, zorder=6)
        # Conectar las esquinas en la base (z_base)
        for idx in range(4):
            i1, j1 = corners[idx]
            i2, j2 = corners[(idx + 1) % 4]
            generator.ax.plot([i1, i2], [j1, j2], [z_base, z_base], color=line_color, alpha=0.6, linewidth=1.2, zorder=6)
    # Perímetro superior usa parámetros de las líneas topográficas
    rgba = mcolors.to_rgba(line_color, alpha=0.8)
    _draw_terrain_perimeter(generator, generator.ax, rgba, 1.2)
    
    # Configurar vista isométrica
    generator.ax.view_init(elev=elevation_angle, azim=azimuth_angle)
    
    # Configurar límites (usar z_base como mínimo)
    generator.ax.set_xlim(0, generator.width - 1)
    generator.ax.set_ylim(0, generator.height - 1)
    generator.ax.set_zlim(z_base, max_h + 1)
    
    # Configurar ticks adaptativos para el eje Z
    z_ticks = _compute_adaptive_ticks(z_base, max_h + 1)
    generator.ax.set_zticks(z_ticks)
    
    # Mantener proporciones de unidades para que los círculos no se deformen
    z_range = (max_h - z_base) + 1
    generator.ax.set_box_aspect((generator.width, generator.height, max(z_range, 1)))
    generator.ax.set_facecolor('black')
    _apply_axes_style(generator.ax, show_axis_labels, grid_color, grid_width, grid_opacity)
    try:
        generator.ax.set_axisbelow(True)
    except Exception:
        pass
    
    generator.fig.canvas.draw_idle()


def export_map_clean(generator, visual_params, fmt='png', save_path=None, include_grid=None, scale=1):
    """Exporta el mapa sin UI, solo las líneas topográficas y la caja de soporte.
    Puede configurar:
    - fmt: 'png' o 'svg'
    - save_path: ruta de salida. Si es None, guarda en 'generados' con timestamp
    - include_grid: True/False para incluir grilla y ejes. Si None, usa visual_params
    - scale: 1, 2 o 4 (escala del lienzo/figura)
    """
    # Verificar que el terreno esté generado
    if generator.terrain is None:
        raise ValueError("No hay terreno generado. Llama a generate_terrain() primero.")
    
    line_color = visual_params.get('line_color', '#ff7825')
    scale = int(scale) if str(scale).isdigit() else 1
    if scale not in (1, 2, 4):
        scale = 1
    base_size = (16, 9)
    figsize = (base_size[0] * scale, base_size[1] * scale)
    temp_fig = plt.figure(figsize=figsize, facecolor='black')
    temp_ax = temp_fig.add_subplot(111, projection='3d')
    X_mesh, Y_mesh = _get_meshgrid(generator)
    Z_mesh = generator.terrain.T
    min_h = float(Z_mesh.min())
    max_h = float(Z_mesh.max())
    z_base = _compute_z_base(min_h, max_h)
    
    # Calcular y dibujar niveles - siempre genera niveles, incluso para terreno plano
    levels = _compute_levels(min_h, max_h, visual_params['num_contour_levels'])
    sea_level = visual_params.get('sea_level', 0.0)
    if len(levels) > 0:
        for level in levels:
            # Líneas punteadas bajo el nivel del mar, sólidas arriba
            linestyle = 'dashed' if level < sea_level else 'solid'
            temp_ax.contour(
                X_mesh, Y_mesh, Z_mesh,
                levels=[level],
                colors=line_color,
                linewidths=1.2,
                linestyles=[linestyle],  # Pasar como lista
                alpha=0.8,
                zorder=5,
                zdir='z',
                offset=level
            )
        
    # Soportes y caja con margen inferior - siempre se dibujan
    corners = [
        (0, 0),
        (generator.width - 1, 0),
        (generator.width - 1, generator.height - 1),
        (0, generator.height - 1)
    ]
    # Verticales
    for i, j in corners:
        z_val = generator.terrain[i, j]
        temp_ax.plot([i, i], [j, j], [z_base, z_val], color=line_color, alpha=0.6, linewidth=1.5, zorder=6)
    # Conectar las esquinas en la base (z_base)
    for idx in range(4):
        i1, j1 = corners[idx]
        i2, j2 = corners[(idx + 1) % 4]
        temp_ax.plot([i1, i2], [j1, j2], [z_base, z_base], color=line_color, alpha=0.6, linewidth=1.2, zorder=6)
    rgba = mcolors.to_rgba(line_color, alpha=0.8)
    _draw_terrain_perimeter(generator, temp_ax, rgba, 1.2)
    
    temp_ax.view_init(elev=visual_params['elevation_angle'], azim=visual_params['azimuth_angle'])
    temp_ax.set_xlim(0, generator.width - 1)
    temp_ax.set_ylim(0, generator.height - 1)
    temp_ax.set_zlim(z_base, max_h + 1)
    
    # Configurar ticks adaptativos para el eje Z
    z_ticks = _compute_adaptive_ticks(z_base, max_h + 1)
    temp_ax.set_zticks(z_ticks)
    
    z_range = (max_h - z_base) + 1
    temp_ax.set_box_aspect((generator.width, generator.height, max(z_range, 1)))
    temp_ax.set_facecolor('black')
    show_axis_labels = bool(visual_params.get('show_axis_labels', True)) if include_grid is None else bool(include_grid)
    grid_color = visual_params.get('grid_color', '#00ffff')
    grid_width = float(visual_params.get('grid_width', 0.6))
    grid_opacity = float(visual_params.get('grid_opacity', 0.35))
    _apply_axes_style(temp_ax, show_axis_labels, grid_color, grid_width, grid_opacity)
    try:
        temp_ax.set_axisbelow(True)
    except Exception:
        pass
    
    from datetime import datetime
    # Resolver ruta de salida
    if save_path is None:
        # Asegurar carpeta de salida (fuera de src)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        out_dir = os.path.join(project_root, 'generados')
        os.makedirs(out_dir, exist_ok=True)
        # Nombre con timestamp para evitar sobrescrituras
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(out_dir, f'mapa_topografico_3d_{ts}.{fmt}')
        filename = ensure_unique_path(filename)
    else:
        # Respetar extensión elegida
        filename = save_path
        # Ajustar extensión si no coincide con fmt
        root, ext = os.path.splitext(filename)
        if fmt.lower() not in (ext.lower().strip('.')):
            filename = root + f'.{fmt}'
        # Asegurar unicidad
        filename = ensure_unique_path(filename)

    dpi = 300
    # Para PNG, escalar DPI adicionalmente para mejorar nitidez
    if str(fmt).lower() == 'png':
        temp_fig.savefig(filename, dpi=dpi, bbox_inches='tight', facecolor='black', pad_inches=0)
    else:
        # SVG es vectorial; guardar tal cual
        temp_fig.savefig(filename, bbox_inches='tight', facecolor='black', pad_inches=0)
    plt.close(temp_fig)
    
    print(f"Exportado: {filename}")
    return True


def export_with_dialog(generator, visual_params):
    """Abre un diálogo para elegir formato (PNG/SVG), escala (x1/x2/x4), incluir grid y ruta de guardado.
    Por defecto sugiere la carpeta Descargas del usuario.
    """
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
        from datetime import datetime

        # Descargas por defecto
        home = os.path.expanduser('~')
        default_downloads = os.path.join(home, 'Downloads')
        if not os.path.isdir(default_downloads):
            # Fallback común en sistemas en español
            alt = os.path.join(home, 'Descargas')
            default_downloads = alt if os.path.isdir(alt) else os.path.dirname(home)

        # Ventana raíz oculta
        root = tk.Tk()
        root.withdraw()

        # Variables de opciones
        fmt_var = tk.StringVar(value='png')
        scale_var = tk.IntVar(value=1)
        grid_var = tk.BooleanVar(value=bool(visual_params.get('show_axis_labels', True)))
        path_var = tk.StringVar()

        # Definir nombre sugerido
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        suggested = os.path.join(default_downloads, f'mapa_topografico_3d_{ts}.png')
        path_var.set(suggested)

        # Construir cuadro de diálogo simple
        dialog = tk.Toplevel(root)
        dialog.title('Exportar mapa')
        dialog.resizable(False, False)

        pad = {'padx': 10, 'pady': 6}
        row = 0

        ttk.Label(dialog, text='Formato:').grid(row=row, column=0, sticky='w', **pad)
        fmt_frame = ttk.Frame(dialog)
        fmt_frame.grid(row=row, column=1, sticky='w', **pad)
        ttk.Radiobutton(fmt_frame, text='PNG', variable=fmt_var, value='png').pack(side='left')
        ttk.Radiobutton(fmt_frame, text='SVG', variable=fmt_var, value='svg').pack(side='left')
        row += 1

        ttk.Label(dialog, text='Escala:').grid(row=row, column=0, sticky='w', **pad)
        scale_frame = ttk.Frame(dialog)
        scale_frame.grid(row=row, column=1, sticky='w', **pad)
        for s in (1, 2, 4):
            ttk.Radiobutton(scale_frame, text=f'x{s}', variable=scale_var, value=s).pack(side='left')
        row += 1

        ttk.Checkbutton(dialog, text='Incluir grilla y ejes', variable=grid_var).grid(row=row, column=0, columnspan=2, sticky='w', **pad)
        row += 1

        # Selección de ruta
        ttk.Label(dialog, text='Ruta de guardado:').grid(row=row, column=0, sticky='w', **pad)
        path_entry = ttk.Entry(dialog, textvariable=path_var, width=48)
        path_entry.grid(row=row, column=1, sticky='w', **pad)
        row += 1

        def choose_path():
            fmt = fmt_var.get()
            filetypes = [('PNG Image', '*.png')] if fmt == 'png' else [('SVG Vector', '*.svg')]
            initialfile = os.path.basename(path_var.get())
            initialdir = os.path.dirname(path_var.get()) or default_downloads
            filename = filedialog.asksaveasfilename(
                title='Guardar como', defaultextension=f'.{fmt}', filetypes=filetypes,
                initialdir=initialdir, initialfile=initialfile
            )
            if filename:
                path_var.set(filename)

        ttk.Button(dialog, text='Elegir...', command=choose_path).grid(row=row-1, column=2, sticky='w', **pad)

        # Botones
        btns = ttk.Frame(dialog)
        btns.grid(row=row, column=0, columnspan=3, sticky='e', **pad)
        result = {'ok': False}

        def do_cancel():
            dialog.destroy()
            root.destroy()

        def do_save():
            path = path_var.get().strip()
            if not path:
                messagebox.showerror('Error', 'Debes elegir una ruta de guardado.')
                return
            fmt = fmt_var.get()
            scl = int(scale_var.get())
            inc_grid = bool(grid_var.get())
            # Ejecutar exportación
            export_map_clean(generator, visual_params, fmt=fmt, save_path=path, include_grid=inc_grid, scale=scl)
            result['ok'] = True
            dialog.destroy()
            root.destroy()

        ttk.Button(btns, text='Cancelar', command=do_cancel).pack(side='right', padx=6)
        ttk.Button(btns, text='Guardar', command=do_save).pack(side='right')

        # Centrar
        dialog.update_idletasks()
        w = dialog.winfo_width(); h = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (w // 2)
        y = (dialog.winfo_screenheight() // 2) - (h // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")

        dialog.transient(root)
        dialog.grab_set()
        root.wait_window(dialog)
        return result.get('ok', False)
    except Exception as e:
        print('No se pudo mostrar el diálogo de exportación, usando ajustes por defecto.', e)
        # Fallback: exportar a generados (png, escala 1)
        return export_map_clean(generator, visual_params, fmt='png', save_path=None, include_grid=visual_params.get('show_axis_labels', True), scale=1)


def export_preview_image(generator, visual_params, out_path):
    """Renderiza una imagen de previsualización (PNG) para la UI web.
    out_path: ruta absoluta al archivo PNG de salida.
    """
    # Verificar que el terreno esté generado
    if generator.terrain is None:
        raise ValueError("No hay terreno generado. Llama a generate_terrain() primero.")
    
    line_color = visual_params.get('line_color', '#ff7825')
    temp_fig = plt.figure(figsize=(12, 8), facecolor='black')
    temp_ax = temp_fig.add_subplot(111, projection='3d')
    X_mesh, Y_mesh = _get_meshgrid(generator)
    Z_mesh = generator.terrain.T
    min_h = float(Z_mesh.min())
    max_h = float(Z_mesh.max())
    z_base = _compute_z_base(min_h, max_h)

    # Calcular y dibujar niveles - siempre genera niveles, incluso para terreno plano
    levels = _compute_levels(min_h, max_h, visual_params['num_contour_levels'])
    sea_level = visual_params.get('sea_level', 0.0)
    
    if len(levels) > 0:
        for level in levels:
            # Líneas punteadas bajo el nivel del mar, sólidas arriba
            linestyle = 'dashed' if level < sea_level else 'solid'
            temp_ax.contour(
                X_mesh, Y_mesh, Z_mesh,
                levels=[level], colors=line_color, linewidths=1.0,
                linestyles=[linestyle], alpha=0.85, zdir='z', offset=level, zorder=5
            )
    
    # Caja con margen inferior - siempre se dibuja
    corners = [(0,0),(generator.width-1,0),(generator.width-1,generator.height-1),(0,generator.height-1)]
    for i,j in corners:
        z_val = generator.terrain[i,j]
        temp_ax.plot([i,i],[j,j],[z_base,z_val], color=line_color, alpha=0.6, linewidth=1.0, zorder=6)
    for idx in range(4):
        i1,j1 = corners[idx]; i2,j2 = corners[(idx+1)%4]
        temp_ax.plot([i1,i2],[j1,j2],[z_base,z_base], color=line_color, alpha=0.6, linewidth=0.9, zorder=6)
    rgba = mcolors.to_rgba(line_color, alpha=0.85)
    _draw_terrain_perimeter(generator, temp_ax, rgba, 1.0)
    temp_ax.view_init(elev=visual_params['elevation_angle'], azim=visual_params['azimuth_angle'])
    temp_ax.set_xlim(0, generator.width-1)
    temp_ax.set_ylim(0, generator.height-1)
    temp_ax.set_zlim(z_base, max_h+1)
    # Configurar ticks adaptativos para el eje Z
    z_ticks = _compute_adaptive_ticks(z_base, max_h + 1)
    temp_ax.set_zticks(z_ticks)
    z_range = (max_h - z_base) + 1
    temp_ax.set_box_aspect((generator.width, generator.height, max(z_range,1)))
    temp_ax.set_facecolor('black')
    show_axis_labels = bool(visual_params.get('show_axis_labels', True))
    grid_color = visual_params.get('grid_color', '#00ffff')
    grid_width = float(visual_params.get('grid_width', 0.6))
    grid_opacity = float(visual_params.get('grid_opacity', 0.35))
    _apply_axes_style(temp_ax, show_axis_labels, grid_color, grid_width, grid_opacity)
    try:
        temp_ax.set_axisbelow(True)
    except Exception:
        pass
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    temp_fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='black', pad_inches=0)
    plt.close(temp_fig)
    return out_path


def _apply_axes_style(ax, show_axis_labels, grid_color, grid_width, grid_opacity):
    """Aplica estilo de ejes y grilla según parámetros de UI.
    - show_axis_labels: activa/desactiva ejes completos
    - grid_color, grid_width, grid_opacity: estilo de grilla
    """
    if show_axis_labels:
        # Aplica estilo de grilla y ejes 3D mediante _axinfo y tick_params
        try:
            rgba = mcolors.to_rgba(grid_color, alpha=float(grid_opacity))
        except Exception:
            rgba = (0.0, 1.0, 1.0, float(grid_opacity))  # fallback cian
        lw = float(grid_width)
        # Grid style
        try:
            for a in (ax.xaxis, ax.yaxis, ax.zaxis):
                a._axinfo['grid']['color'] = rgba
                a._axinfo['grid']['linewidth'] = lw
                a._axinfo['grid']['linestyle'] = '-'
                # Oculta las líneas de eje por defecto para evitar conflicto de color
                if 'axisline' in a._axinfo:
                    a._axinfo['axisline']['color'] = (0, 0, 0, 0)
                    a._axinfo['axisline']['linewidth'] = 0.0
                if 'tick' in a._axinfo:
                    a._axinfo['tick']['color'] = rgba
        except Exception:
            pass
        ax.grid(True)
        # Axis labels (titles) remain outside parametrization (keep white)
        ax.set_xlabel('X', fontsize=9, color='white')
        ax.set_ylabel('Y', fontsize=9, color='white')
        ax.set_zlabel('Altura', fontsize=9, color='white')
        # Tick marks width/color and tick labels color
        try:
            ax.tick_params(colors=rgba, width=lw, labelsize=8,
                           left=True, right=True, bottom=True, top=True,
                           labelleft=True, labelbottom=True)
            for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
                for t in axis.get_ticklines():
                    t.set_linewidth(lw)
                    t.set_color(rgba)
                for lbl in axis.get_ticklabels():
                    lbl.set_color(rgba)
                    try:
                        lbl.set_alpha(rgba[3])
                    except Exception:
                        pass
        except Exception:
            pass
        # Oculta los bordes de los panes para que no opaquen la bounding box personalizada
        try:
            transparent = (0, 0, 0, 0)
            ax.xaxis.pane.set_edgecolor(transparent)
            ax.yaxis.pane.set_edgecolor(transparent)
            ax.zaxis.pane.set_edgecolor(transparent)
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
        except Exception:
            pass
        # Dibuja una bounding box personalizada con los parámetros del grid
        _draw_bounding_box(ax, rgba, lw)
    else:
        ax.grid(False)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_zlabel('')
        ax.tick_params(left=False, right=False, labelleft=False,
                        bottom=False, top=False, labelbottom=False,
                        labelsize=0, colors='black')
        try:
            ax.xaxis.pane.set_edgecolor('black')
            ax.yaxis.pane.set_edgecolor('black')
            ax.zaxis.pane.set_edgecolor('black')
        except Exception:
            pass
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False

def _draw_bounding_box(ax, rgba, lw):
    """Dibuja una caja de contorno personalizada alrededor del volumen visible.
    Usa los límites actuales y dibuja 4 aristas en la base (zmin) y 4 en la parte superior (zmax).
    """
    try:
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        zmin, zmax = ax.get_zlim()
        # Esquinas
        corners_bottom = [
            (xmin, ymin, zmin), (xmax, ymin, zmin),
            (xmax, ymax, zmin), (xmin, ymax, zmin)
        ]
        corners_top = [
            (xmin, ymin, zmax), (xmax, ymin, zmax),
            (xmax, ymax, zmax), (xmin, ymax, zmax)
        ]
        # Base
        for i in range(4):
            x1, y1, z1 = corners_bottom[i]
            x2, y2, z2 = corners_bottom[(i+1) % 4]
            ln = ax.plot([x1, x2], [y1, y2], [z1, z2], color=rgba, linewidth=lw, zorder=6)[0]
            ln.set_alpha(rgba[3])
        # Arriba
        for i in range(4):
            x1, y1, z1 = corners_top[i]
            x2, y2, z2 = corners_top[(i+1) % 4]
            ln = ax.plot([x1, x2], [y1, y2], [z1, z2], color=rgba, linewidth=lw, zorder=6)[0]
            ln.set_alpha(rgba[3])
        # Columnas
        for i in range(4):
            xb, yb, zb = corners_bottom[i]
            xt, yt, zt = corners_top[i]
            ln = ax.plot([xb, xt], [yb, yt], [zb, zt], color=rgba, linewidth=lw, zorder=6)[0]
            ln.set_alpha(rgba[3])
    except Exception:
        pass

def _draw_terrain_perimeter(generator, ax, rgba, lw):
    """Optimizado: traza 4 líneas (una por lado) usando arrays completos."""
    try:
        W, H = generator.width, generator.height
        Z = generator.terrain
        # Superior (y=0)
        xs = np.arange(W); ys = np.zeros(W); zs = Z[:, 0]
        ln = ax.plot(xs, ys, zs, color=rgba, linewidth=lw, zorder=6)[0]; ln.set_alpha(rgba[3])
        # Derecho (x=W-1)
        xs = np.full(H, W - 1); ys = np.arange(H); zs = Z[W - 1, :]
        ln = ax.plot(xs, ys, zs, color=rgba, linewidth=lw, zorder=6)[0]; ln.set_alpha(rgba[3])
        # Inferior (y=H-1)
        xs = np.arange(W - 1, -1, -1); ys = np.full(W, H - 1); zs = Z[::-1, H - 1]
        ln = ax.plot(xs, ys, zs, color=rgba, linewidth=lw, zorder=6)[0]; ln.set_alpha(rgba[3])
        # Izquierdo (x=0)
        xs = np.zeros(H); ys = np.arange(H - 1, -1, -1); zs = Z[0, ::-1]
        ln = ax.plot(xs, ys, zs, color=rgba, linewidth=lw, zorder=6)[0]; ln.set_alpha(rgba[3])
    except Exception:
        pass
