import { getEls } from './ui.js';

export const state = { terrain: {}, visual: {}, craters: {} };

export function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

export function applyState(s, updateAll = true) {
  const els = getEls();
  Object.assign(state.terrain, s.terrain);
  Object.assign(state.visual, s.visual);
  const craters = s.craters || s.crater || {};
  Object.assign(state.craters, craters);

  if (updateAll) {
    // Terrain parameters
    if (els.vh) {
      els.vh.value = state.terrain.height_variation ?? 8.0;
      if (els.vhVal) els.vhVal.value = String((state.terrain.height_variation ?? 8.0).toFixed(1));
    }
    
    if (els.rough) {
      els.rough.value = state.terrain.terrain_roughness ?? 50;
      if (els.roughVal) els.roughVal.value = `${Math.round(state.terrain.terrain_roughness ?? 50)}%`;
    }

    if (els.dens) {
      els.dens.value = state.visual.num_contour_levels ?? 30;
      if (els.densVal) els.densVal.value = String(Math.round(state.visual.num_contour_levels ?? 30));
    }

    // Rotation
    if (els.azRange) {
      els.azRange.value = Math.round(state.visual.azimuth_angle ?? 340);
      if (els.azVal) els.azVal.value = `${Math.round(state.visual.azimuth_angle ?? 340)}°`;
    }

    if (els.elRange) {
      els.elRange.value = Math.round(state.visual.elevation_angle ?? 24);
      if (els.elVal) els.elVal.value = `${Math.round(state.visual.elevation_angle ?? 24)}°`;
    }

    // Craters
    const cratersEnabled = state.craters.enabled ?? false;
    if (els.chkCraters) {
      els.chkCraters.checked = cratersEnabled;
    }
    if (els.cratersSection) {
      els.cratersSection.classList.toggle('hidden', !cratersEnabled);
    }

    if (els.cDen) {
      els.cDen.value = state.craters.density ?? 3;
      if (els.cDenVal) els.cDenVal.value = String(Math.round(state.craters.density ?? 3));
    }

    if (els.cSize) {
      els.cSize.value = state.craters.size ?? 0.5;
      if (els.cSizeVal) els.cSizeVal.value = String((state.craters.size ?? 0.5).toFixed(1));
    }

    if (els.cDepth) {
      els.cDepth.value = state.craters.depth ?? 0.6;
      if (els.cDepthVal) els.cDepthVal.value = String((state.craters.depth ?? 0.6).toFixed(1));
    }

    // Options menu
    if (els.seedInput) {
      const seed = state.terrain.seed ?? 42;
      els.seedInput.value = String(seed).padStart(6, '0');
    }

    const lineColor = state.visual.line_color ?? '#FF7825';
    if (els.lineColorInput) {
      els.lineColorInput.value = lineColor;
    }
    if (els.lineColorHex) {
      els.lineColorHex.value = lineColor.toUpperCase();
    }
    if (els.colorSwatch) {
      els.colorSwatch.style.backgroundColor = lineColor;
    }

    if (els.baseHeightSlider) {
      els.baseHeightSlider.value = String(Math.round(state.terrain.base_height ?? 20));
    }
    if (els.baseHeightValue) {
      els.baseHeightValue.value = String(Math.round(state.terrain.base_height ?? 20));
    }

    if (els.seaLevelSlider) {
      els.seaLevelSlider.value = String(Math.round(state.visual.sea_level ?? 0));
    }
    if (els.seaLevelValue) {
      els.seaLevelValue.value = String(Math.round(state.visual.sea_level ?? 0));
    }

    // Grid options
    const gridEnabled = state.visual.show_axis_labels ?? true;
    if (els.gridToggle) {
      els.gridToggle.checked = gridEnabled;
    }
    if (els.gridOptions) {
      els.gridOptions.classList.toggle('hidden', !gridEnabled);
    }

    const gridColor = state.visual.grid_color ?? '#00FFFF';
    if (els.gridColorInput) {
      els.gridColorInput.value = gridColor;
    }
    if (els.gridColorHex) {
      const hex = gridColor.toUpperCase();
      els.gridColorHex.value = hex.startsWith('#') ? hex : '#' + hex;
    }
    if (els.gridColorSwatch) {
      els.gridColorSwatch.style.backgroundColor = gridColor;
    }

    if (els.gridWidthSlider) {
      // Convertir de formato interno (ej. 0.6) a px (ej. 2px)
      const widthPx = Math.round((state.visual.grid_width ?? 0.6) * 3.33);
      els.gridWidthSlider.value = String(widthPx);
    }
    if (els.gridWidthValue) {
      const widthPx = Math.round((state.visual.grid_width ?? 0.6) * 3.33);
      els.gridWidthValue.value = widthPx + 'px';
    }

    if (els.gridOpacitySlider) {
      // Convertir de 0-1 a 1-255
      const opacity255 = Math.round((state.visual.grid_opacity ?? 0.35) * 255);
      els.gridOpacitySlider.value = String(opacity255);
    }
    if (els.gridOpacityValue) {
      const opacity255 = Math.round((state.visual.grid_opacity ?? 0.35) * 255);
      els.gridOpacityValue.value = String(opacity255);
    }
  }

  // Update preview if it exists
  if (s.preview && els.preview) {
    els.preview.src = s.preview + '?t=' + Date.now();
    els.preview.classList.remove('hidden');
  }
}

