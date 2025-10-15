"""
Módulo de interfaz de usuario (controles y widgets)
"""
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox
import random
import numpy as np


class UIController:
    """Controlador de la interfaz de usuario"""
    
    def __init__(self, fig, generator, terrain_params, visual_params, draw_callback):
        self.fig = fig
        self.generator = generator
        self.terrain_params = terrain_params
        self.visual_params = visual_params
        self.draw_callback = draw_callback
        self.show_axis_labels = True
        self.ax_sliders = {}
        self.crater_sliders = {}
        self.widgets = {}
        self.readouts = {}
        self.line_color = self.visual_params.get('line_color', '#ff7825')
        # Valores por defecto de rotación
        self._default_az = self.visual_params.get('azimuth_angle', 340)
        self._default_el = self.visual_params.get('elevation_angle', 20)
        # Estado del gizmo (azimuth/elevation)
        self._gizmo_dragging = False

    def create_main_sliders(self):
        """Crea los sliders principales en el panel derecho"""
        base_x = 0.74
        width = 0.22
        y = 0.82
        gap = 0.08

        main_sliders = [
            ('height_variation', 'Variación de altura', 0.0, 20.0, self.terrain_params['height_variation'], False, '%1.1f'),
            ('terrain_roughness', 'Rugosidad', 0, 100, self.terrain_params['terrain_roughness'], True, '%d%%'),
            ('num_contour_levels', 'Densidad de líneas', 10, 40, self.visual_params['num_contour_levels'], True, '%d'),
        ]

        for i, params in enumerate(main_sliders):
            name, label, min_val, max_val, init_val, is_int, fmt = params

            # Etiqueta con título y valor a la derecha
            lbl = self.fig.text(base_x, y + 0.025, label, color='white', fontsize=10, va='bottom')
            val_text = self.fig.text(base_x + width - 0.04, y + 0.025,
                                     (fmt % init_val) if not is_int else (fmt % int(init_val)),
                                     color='white', fontsize=10, va='bottom', ha='right')
            self.readouts[f'{name}_label'] = lbl
            self.readouts[f'{name}_value'] = val_text

            ax_pos = [base_x, y, width, 0.025]
            ax = self.fig.add_axes(ax_pos, facecolor='#2a2a2a')
            slider = Slider(
                ax=ax,
                label='',
                valmin=min_val,
                valmax=max_val,
                valinit=init_val,
                valstep=1 if is_int else None,
                valfmt='%d' if is_int else '%1.1f',
                color='orange',
                track_color='#404040'
            )
            slider.valtext.set_color('white')

            def _mk_update(n=name, f=fmt, integer=is_int, vt=val_text):
                def update(val):
                    if n in self.terrain_params:
                        self.terrain_params[n] = val
                        self.generator.generate_terrain(**self.terrain_params)
                    else:
                        self.visual_params[n] = val
                    # Actualiza el texto de valor
                    if integer:
                        vt.set_text(f % int(val))
                    else:
                        vt.set_text(f % float(val))
                    self.draw_callback()
                return update

            slider.on_changed(_mk_update())
            self.ax_sliders[name] = ax
            self.ax_sliders[name].slider = slider
            y -= gap
    
    # Método auxiliar obsoleto eliminado (no utilizado)
    
    def create_seed_input(self):
        """Crea el campo de entrada para la semilla en la barra superior"""
        # Etiqueta
        self.fig.text(0.23, 0.94, 'Semilla:', color='white', fontsize=10, va='center')
        ax_seed = self.fig.add_axes([0.26, 0.90, 0.10, 0.04], facecolor='#2a2a2a')
        seed_text = TextBox(ax_seed, '', initial=str(self.terrain_params['seed']), 
                            color='white', hovercolor='#404040')
        seed_text.label.set_color('white')
        
        def submit_seed(text):
            try:
                # Normalizar semillas muy grandes para evitar bloqueos: clamp 1..10_000_000 y hash a int32
                new_seed = int(text)
                if new_seed < 1:
                    new_seed = 1
                # Reducir magnitud manteniendo variabilidad
                new_seed = int(abs(new_seed)) % 10_000_000
                if new_seed == 0:
                    new_seed = 1
                self.terrain_params['seed'] = new_seed
                self.generator.generate_terrain(**self.terrain_params)
                self.draw_callback()
            except ValueError:
                print("Semilla invalida")
                seed_text.set_val(str(self.terrain_params['seed']))
        
        seed_text.on_submit(submit_seed)
        self.widgets['seed_text'] = seed_text
        
        # Botón de refresco al lado
        ax_refresh = self.fig.add_axes([0.37, 0.90, 0.04, 0.04])
        btn_refresh = Button(ax_refresh, '↻', color='#2a2a2a', hovercolor='#404040')
        btn_refresh.label.set_color('white')
        _refresh_lock = {'busy': False}  # Initialize the reentrancy lock
        def do_refresh(event):
            if _refresh_lock['busy']:
                return
            _refresh_lock['busy'] = True
            try:
                new_seed = random.randint(1, 10_000_000)
                seed_text.set_val(str(new_seed))
                submit_seed(str(new_seed))
            finally:
                _refresh_lock['busy'] = False
        btn_refresh.on_clicked(do_refresh)
        self.widgets['btn_refresh'] = btn_refresh

        return seed_text
    
    def create_crater_sliders(self):
        """Crea los sliders de control de cráteres en el panel derecho"""
        base_x = 0.74
        width = 0.22
        # Comienza más abajo del panel
        # Título de sección
        self.readouts['craters_title'] = self.fig.text(0.74, 0.40, 'Cráteres:', color='white', fontsize=11, va='center')
        y_start = 0.36
        gap = 0.08
        crater_slider_params = [
            ('num_craters', 'Densidad', 0, 10, self.terrain_params['num_craters'], True, '%d'),
            ('crater_size', 'Tamaño', 0.1, 1.0, self.terrain_params['crater_size'], False, '%1.1f'),
            ('crater_depth', 'Profundidad', 0.1, 1.0, self.terrain_params['crater_depth'], False, '%1.1f'),
        ]

        y = y_start
        for i, params in enumerate(crater_slider_params):
            name, label, min_val, max_val, init_val, is_int, fmt = params
            ax_pos = [base_x, y, width, 0.025]

            # Crear o reemplazar slider
            if name in self.crater_sliders and 'ax' in self.crater_sliders[name]:
                try:
                    self.crater_sliders[name]['ax'].remove()
                except Exception:
                    pass
            ax = self.fig.add_axes(ax_pos, facecolor='#2a2a2a')
            slider = Slider(
                ax=ax,
                label='',
                valmin=min_val,
                valmax=max_val,
                valinit=init_val,
                valstep=1 if is_int else None,
                valfmt='%d' if is_int else '%1.1f',
                color='orange',
                track_color='#404040'
            )
            slider.valtext.set_color('white')
            # Etiqueta y valor
            lbl = self.fig.text(base_x, y + 0.025, label, color='white', fontsize=10, va='bottom')
            val_text = self.fig.text(base_x + width - 0.04, y + 0.025,
                                     (fmt % init_val) if not is_int else (fmt % int(init_val)),
                                     color='white', fontsize=10, va='bottom', ha='right')

            def _mk_update(n=name, f=fmt, integer=is_int, vt=val_text):
                def update(val):
                    self.terrain_params[n] = val
                    # Actualizar valor y regenerar
                    if integer:
                        vt.set_text(f % int(val))
                    else:
                        vt.set_text(f % float(val))
                    self.generator.generate_terrain(**self.terrain_params)
                    self.draw_callback()
                return update

            slider.on_changed(_mk_update())
            self.crater_sliders[name] = {'ax': ax, 'slider': slider, 'label': lbl, 'value_text': val_text}
            y -= gap
    
    # Método auxiliar obsoleto eliminado (no utilizado)
    
    def toggle_crater_sliders(self, visible):
        """Muestra u oculta los sliders de cráteres"""
        for data in self.crater_sliders.values():
            if 'ax' in data:
                data['ax'].set_visible(visible)
            if 'label' in data:
                data['label'].set_visible(visible)
            if 'value_text' in data:
                data['value_text'].set_visible(visible)
        if 'craters_title' in self.readouts:
            self.readouts['craters_title'].set_visible(visible)
    
    def create_buttons(self, export_callback):
        """Crea todos los botones de la interfaz (barra superior + panel derecho)"""
        # ------ Barra superior ------
        # Guardar como
        self.fig.text(0.06, 0.94, 'Guardar como:', color='white', fontsize=10, va='center')
        ax_png = self.fig.add_axes([0.13, 0.90, 0.06, 0.04])
        btn_png = Button(ax_png, 'PNG', color='#2a2a2a', hovercolor='#404040')
        btn_png.label.set_color('white')
        btn_png.on_clicked(lambda e: export_callback('png'))
        self.widgets['btn_png'] = btn_png
        ax_svg = self.fig.add_axes([0.20, 0.90, 0.06, 0.04])
        btn_svg = Button(ax_svg, 'SVG', color='#2a2a2a', hovercolor='#404040')
        btn_svg.label.set_color('white')
        btn_svg.on_clicked(lambda e: export_callback('svg'))
        self.widgets['btn_svg'] = btn_svg

        # Campo de texto para color hex
        self.fig.text(0.41, 0.94, 'Color de líneas:', color='white', fontsize=10, va='center')
        ax_color = self.fig.add_axes([0.50, 0.90, 0.10, 0.04], facecolor='#2a2a2a')
        color_text = TextBox(ax_color, '', initial=self.line_color, color='white', hovercolor='#404040')
        color_text.label.set_color('white')
        def submit_color(text):
            if text.startswith('#') and (len(text) == 7 or len(text) == 4):
                self.line_color = text
                self.visual_params['line_color'] = text
                # Actualizar swatch y gizmo si existe
                if 'color_swatch_ax' in self.widgets:
                    self.widgets['color_swatch_ax'].set_facecolor(text)
                if 'gizmo_circle' in self.widgets:
                    self.widgets['gizmo_circle'].set_color(text)
                if 'gizmo_marker' in self.widgets:
                    self.widgets['gizmo_marker'].set_color(text)
                self.draw_callback()
            else:
                print('Código HEX inválido')
                color_text.set_val(self.line_color)
        color_text.on_submit(submit_color)
        self.widgets['color_text'] = color_text
        # Swatch del color
        ax_swatch = self.fig.add_axes([0.61, 0.90, 0.03, 0.04])
        ax_swatch.set_xticks([]); ax_swatch.set_yticks([])
        ax_swatch.set_facecolor(self.line_color)
        for spine in ax_swatch.spines.values():
            spine.set_visible(False)
        self.widgets['color_swatch_ax'] = ax_swatch

        # Botón para mostrar/ocultar labels de ejes
        def toggle_axis_labels(event):
            self.show_axis_labels = not self.show_axis_labels
            status = "ON" if self.show_axis_labels else "OFF"
            btn_axis_labels.label.set_text(f'Ejes: {status}')
            self.visual_params['show_axis_labels'] = self.show_axis_labels
            self.draw_callback()

        self.fig.text(0.66, 0.94, 'Ejes:', color='white', fontsize=10, va='center')
        ax_axis_btn = self.fig.add_axes([0.69, 0.90, 0.06, 0.04])
        btn_axis_labels = Button(ax_axis_btn, f"{'ON' if self.show_axis_labels else 'OFF'}",
                                 color='#2a2a2a', hovercolor='#404040')
        btn_axis_labels.label.set_color('white')
        btn_axis_labels.on_clicked(toggle_axis_labels)
        self.widgets['btn_axis_labels'] = btn_axis_labels

        # Botón toggle de cráteres
        def toggle_craters(event):
            self.terrain_params['crater_enabled'] = not self.terrain_params['crater_enabled']
            status = "ON" if self.terrain_params['crater_enabled'] else "OFF"
            btn_craters.label.set_text(f'{status}')
            
            if self.terrain_params['crater_enabled']:
                self.create_crater_sliders()
                self.toggle_crater_sliders(True)
            else:
                self.toggle_crater_sliders(False)
            
            self.generator.generate_terrain(**self.terrain_params)
            self.draw_callback()
            self.fig.canvas.draw()

        self.fig.text(0.77, 0.94, 'Cráteres:', color='white', fontsize=10, va='center')
        ax_crater_btn = self.fig.add_axes([0.81, 0.90, 0.06, 0.04])
        btn_craters = Button(ax_crater_btn, f"{'ON' if self.terrain_params['crater_enabled'] else 'OFF'}",
                             color='#2a2a2a', hovercolor='#404040')
        btn_craters.label.set_color('white')
        btn_craters.on_clicked(toggle_craters)
        self.widgets['btn_craters'] = btn_craters

        # ------ Panel derecho: sección Rotación ------
        self.fig.text(0.74, 0.58, 'Rotación:', color='white', fontsize=11, va='center')
        # Botón reset
        ax_reset = self.fig.add_axes([0.90, 0.575, 0.035, 0.035])
        btn_reset = Button(ax_reset, '⟲', color='#2a2a2a', hovercolor='#404040')
        btn_reset.label.set_color('white')
        def do_reset(event):
            self.visual_params['azimuth_angle'] = self._default_az
            self.visual_params['elevation_angle'] = self._default_el
            # Si hay gizmo, actualiza su marcador
            if 'gizmo_marker' in self.widgets:
                r = 0.8
                azr = np.deg2rad(self._default_az)
                self.widgets['gizmo_marker'].set_data([r*np.cos(azr)], [r*np.sin(azr)])
            self._update_rotation_readouts()
            self.draw_callback()
            self.fig.canvas.draw_idle()
        btn_reset.on_clicked(do_reset)
        self.widgets['btn_reset_rot'] = btn_reset

        # Lecturas de ángulos
        self.readouts['rot_az'] = self.fig.text(0.74, 0.52, f"Eje Z: {int(self.visual_params.get('azimuth_angle', 340))}°",
                                                color='white', fontsize=10, va='center')
        self.readouts['rot_el'] = self.fig.text(0.74, 0.48, f"Elevación: {int(self.visual_params.get('elevation_angle', 20))}°",
                                                color='white', fontsize=10, va='center')

        # Gizmo de orientación (inset): panel tipo brújula para rotar (abajo-derecha)
        self._create_orientation_gizmo(pos=[0.66, 0.12, 0.16, 0.16])

    def _create_orientation_gizmo(self, pos=None):
        # Área para el gizmo (por defecto abajo derecha)
        if pos is None:
            pos = [0.66, 0.12, 0.16, 0.16]
        ax_gizmo = self.fig.add_axes(pos, facecolor='#111111')
        ax_gizmo.set_xticks([])
        ax_gizmo.set_yticks([])
        ax_gizmo.set_xlim(-1, 1)
        ax_gizmo.set_ylim(-1, 1)
        # Dibujar círculo y ejes
        circle = plt.Circle((0, 0), 0.95, color=self.line_color, fill=False, alpha=0.6, linewidth=1.0)
        ax_gizmo.add_patch(circle)
        ax_gizmo.plot([0, 0], [-1, 1], color=self.line_color, alpha=0.4, linewidth=0.8)
        ax_gizmo.plot([-1, 1], [0, 0], color=self.line_color, alpha=0.4, linewidth=0.8)
        # Marcador de dirección actual
        az = np.deg2rad(self.visual_params.get('azimuth_angle', 340))
        r = 0.8
        marker, = ax_gizmo.plot([r*np.cos(az)], [r*np.sin(az)], marker='o', color=self.line_color)
        self.widgets['gizmo_circle'] = circle
        self.widgets['gizmo_marker'] = marker

        def on_press(event):
            if event.inaxes == ax_gizmo:
                self._gizmo_dragging = True

        def on_release(event):
            self._gizmo_dragging = False

        def on_move(event):
            if not self._gizmo_dragging or event.inaxes != ax_gizmo or event.xdata is None:
                return
            # Mapear coordenadas a ángulo azimutal
            azimuth = (np.degrees(np.arctan2(event.ydata, event.xdata)) + 360.0) % 360.0
            # Mapear distancia al centro a elevación (0..1 -> 0..90)
            dist = min(1.0, np.sqrt(event.xdata**2 + event.ydata**2))
            elevation = np.clip(dist * 90.0, 0, 90)
            # Actualizar parámetros y UI
            self.visual_params['azimuth_angle'] = azimuth
            self.visual_params['elevation_angle'] = elevation
            marker.set_data([r*np.cos(np.deg2rad(azimuth))], [r*np.sin(np.deg2rad(azimuth))])
            # Redibujar escena
            self.draw_callback()
            self._update_rotation_readouts()
            self.fig.canvas.draw_idle()

        cid_press = self.fig.canvas.mpl_connect('button_press_event', on_press)
        cid_release = self.fig.canvas.mpl_connect('button_release_event', on_release)
        cid_move = self.fig.canvas.mpl_connect('motion_notify_event', on_move)
        # Guardar referencias
        self.widgets['gizmo_ax'] = ax_gizmo

    def _update_rotation_readouts(self):
        """Actualiza los textos de lectura de azimuth y elevación"""
        if 'rot_az' in self.readouts:
            self.readouts['rot_az'].set_text(f"Eje Z: {int(self.visual_params.get('azimuth_angle', 0))}°")
        if 'rot_el' in self.readouts:
            self.readouts['rot_el'].set_text(f"Elevación: {int(self.visual_params.get('elevation_angle', 0))}°")
