import { getEls } from './ui.js';

export const state = { terrain: {}, visual: {}, craters: {} };

export function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

export function applyState(s, updateSliders = true) {
  const els = getEls();
  Object.assign(state.terrain, s.terrain);
  Object.assign(state.visual, s.visual);
  const craters = s.craters || s.crater || {};
  Object.assign(state.craters, craters);

  if (s.terrain_stats && s.terrain_stats.max_height) {
    const newMax = Math.ceil(s.terrain_stats.max_height);
    els.seaLevel.max = newMax;
    if (parseFloat(els.seaLevel.value) > newMax) {
      els.seaLevel.value = newMax;
      state.visual.sea_level = newMax;
      els.seaLevelVal.textContent = newMax.toFixed(1);
    }
  }

  if (!updateSliders) return;

  els.preview.src = s.preview + '?t=' + Date.now();
  els.seedInput.value = state.terrain.seed;
  els.colorInput.value = state.visual.line_color;
  els.colorSwatch.style.background = state.visual.line_color;
  els.chkAxes.checked = !!state.visual.show_axis_labels;
  if (els.gridOptions) {
    els.gridOptions.hidden = !els.chkAxes.checked;
    els.gridColor.value = state.visual.grid_color || '#00ffff';
    if (els.gridSwatch) els.gridSwatch.style.background = els.gridColor.value;
    const gw = state.visual.grid_width ?? 0.6;
    els.gridWidth.value = gw;
    if (els.gridWidthNum) els.gridWidthNum.value = gw.toFixed(1);
    const go01 = state.visual.grid_opacity ?? 0.35;
    const go255 = Math.round(Math.min(1, Math.max(0.01, go01)) * 255);
    els.gridOpacity.value = go255;
    if (els.gridOpacityNum) els.gridOpacityNum.value = go255;
  }
  const cratersEnabled = state.craters.enabled ?? false;
  els.chkCraters.checked = cratersEnabled;
  els.vh.value = state.terrain.height_variation ?? 8.0;
  els.vhVal.textContent = (state.terrain.height_variation ?? 8.0).toFixed(1);
  els.rough.value = state.terrain.terrain_roughness ?? 50;
  els.roughVal.textContent = `${state.terrain.terrain_roughness ?? 50}%`;
  els.baseHeight.value = state.terrain.base_height ?? 20.0;
  els.baseHeightVal.textContent = (state.terrain.base_height ?? 20.0).toFixed(1);
  els.seaLevel.value = state.visual.sea_level ?? 0.0;
  els.seaLevelVal.textContent = (state.visual.sea_level ?? 0.0).toFixed(1);
  els.dens.value = state.visual.num_contour_levels;
  els.densVal.textContent = state.visual.num_contour_levels;
  els.azInput.value = Math.round(state.visual.azimuth_angle);
  els.azRange.value = Math.round(state.visual.azimuth_angle);
  els.elInput.value = Math.round(state.visual.elevation_angle);
  els.elRange.value = Math.round(state.visual.elevation_angle);
  els.cratersSection.hidden = !cratersEnabled;
  els.cDen.value = state.craters.density ?? 3;
  els.cDenVal.textContent = state.craters.density ?? 3;
  els.cSize.value = state.craters.size ?? 0.5;
  els.cSizeVal.textContent = (state.craters.size ?? 0.5).toFixed(1);
  els.cDepth.value = state.craters.depth ?? 0.6;
  els.cDepthVal.textContent = (state.craters.depth ?? 0.6).toFixed(1);
}
