import { getEls, showLoader, showToast, placeSideTab } from './ui.js';
import { state, applyState, clamp } from './state.js';
import { getState, updatePreview, randomSeed, resetView, suggestDownloadPath, exportOptions } from './api.js';

function setFormat(els, fmt) {
  const isPng = fmt === 'png';
  els.expFmtPng.classList.toggle('active', isPng);
  els.expFmtSvg.classList.toggle('active', !isPng);
  els.expFmtPng.dataset.fmt = 'png';
  els.expFmtSvg.dataset.fmt = 'svg';
}

function wire() {
  const els = getEls();
  // Debug: report presence of critical elements
  console.debug('[wire] Elements presence', {
    vh: !!els.vh, rough: !!els.rough, baseHeight: !!els.baseHeight,
    seaLevel: !!els.seaLevel, dens: !!els.dens,
    chkCraters: !!els.chkCraters, cDen: !!els.cDen, cSize: !!els.cSize, cDepth: !!els.cDepth,
    preview: !!els.preview
  });

  // Export modal open
  if (els.btnExport) els.btnExport.onclick = async () => {
    try {
      const sug = await suggestDownloadPath();
      if (sug && typeof sug === 'string' && !els.expPath.value) {
        els.expPath.placeholder = sug;
        els.expPath.value = sug;
        els.expPath.title = sug;
      }
    } catch { if (!els.expPath.value) els.expPath.value = '/Descargas/'; }
    els.expChkGrid.checked = !!state.visual.show_axis_labels;
    els.expScale.value = '1';
    setFormat(els, 'png');
    if (els.exportModal) els.exportModal.classList.remove('hidden');
    try {
      const rect = els.btnExport.getBoundingClientRect();
      const panel = els.exportModal;
      if (panel) {
        panel.style.left = (rect.left) + 'px';
        panel.style.top = (rect.top) + 'px';
        panel.style.width = Math.max(rect.width, 360) + 'px';
      }
    } catch {}
  };

  if (els.expFmtPng) els.expFmtPng.onclick = () => { setFormat(els, 'png'); if (els.expScale) { els.expScale.disabled = false; } };
  if (els.expFmtSvg) els.expFmtSvg.onclick = () => { setFormat(els, 'svg'); if (els.expScale) { els.expScale.disabled = true; } };
  if (els.expClose) els.expClose.onclick = () => { if (els.exportModal) els.exportModal.classList.add('hidden'); };

  document.addEventListener('click', (ev) => {
    const panel = els.exportModal;
    if (!panel || panel.classList.contains('hidden')) return;
    const isInside = panel.contains(ev.target) || (els.btnExport && els.btnExport.contains(ev.target));
    if (!isInside) panel.classList.add('hidden');
  });

  if (els.expBrowse) els.expBrowse.onclick = async () => {
    const fmt = els.expFmtSvg.classList.contains('active') ? 'svg' : 'png';
    const includeGrid = !!els.expChkGrid.checked;
    const scale = parseInt(els.expScale.value || '1');
    const url = `/export?fmt=${encodeURIComponent(fmt)}&includeGrid=${includeGrid ? '1' : '0'}&scale=${encodeURIComponent(scale)}`;
    showToast('Generando archivo…', 'info');
    window.open(url, '_blank');
    if (els.exportModal) els.exportModal.classList.add('hidden');
  };

  if (els.expSave) els.expSave.onclick = async () => {
    const fmt = els.expFmtSvg.classList.contains('active') ? 'svg' : 'png';
    const includeGrid = !!els.expChkGrid.checked;
    const scale = parseInt(els.expScale.value || '1');
    const path = (els.expPath.value || '').trim();
    if (!path || path === '/Descargas/') {
      const url = `/export?fmt=${encodeURIComponent(fmt)}&includeGrid=${includeGrid ? '1' : '0'}&scale=${encodeURIComponent(scale)}`;
      showToast('Generando archivo…', 'info');
      window.open(url, '_blank');
      if (els.exportModal) els.exportModal.classList.add('hidden');
      setTimeout(() => showToast('Descarga iniciada.', 'success'), 600);
      return;
    }
    showLoader(true);
    try {
      const res = await exportOptions({ fmt, includeGrid, scale, path });
      if (res && res.ok) {
        if (els.exportModal) els.exportModal.classList.add('hidden');
        showToast('Guardado correctamente.', 'success', 3000);
      } else {
        showToast('No se pudo guardar el archivo.', 'error', 4000);
      }
    } catch { /* ignore */ }
    showLoader(false);
  };

  // Options panel logic
  let _optOutsideHandler = null;
  const openOptions = (anchorEl) => {
    if (!els.optPanel) return;
    els.optPanel.classList.remove('hidden');
    try {
      if (anchorEl && anchorEl.getBoundingClientRect) {
        const rect = anchorEl.getBoundingClientRect();
        const panelRect = els.optPanel.getBoundingClientRect();
        let top = rect.top;
        let left = rect.left - panelRect.width + 34;
        if (top + panelRect.height > window.innerHeight - 16) {
          top = Math.max(16, window.innerHeight - panelRect.height - 16);
        }
        if (left < 16) left = 16;
        els.optPanel.style.top = `${top}px`;
        els.optPanel.style.left = `${left}px`;
        els.optPanel.style.right = 'auto';
      }
    } catch {}
    if (!_optOutsideHandler) {
      _optOutsideHandler = (ev) => {
        const t = ev.target;
        if (!els.optPanel.contains(t) && t !== els.btnOptionsTab) {
          closeOptions();
        }
      };
      document.addEventListener('click', _optOutsideHandler);
    }
  };
  const closeOptions = () => {
    if (!els.optPanel) return;
    els.optPanel.classList.add('hidden');
    if (_optOutsideHandler) {
      document.removeEventListener('click', _optOutsideHandler);
      _optOutsideHandler = null;
    }
  };
  if (els.btnOptionsTab) els.btnOptionsTab.onclick = (e) => { e.stopPropagation(); openOptions(e.currentTarget); };
  if (els.btnCloseOptions) els.btnCloseOptions.onclick = (e) => { e.stopPropagation(); closeOptions(); };

  // Place side tab
  const sidebar = document.querySelector('aside.panel');
  placeSideTab(els.btnOptionsTab, sidebar);
  window.addEventListener('resize', () => placeSideTab(els.btnOptionsTab, sidebar));

  // Events
  els.btnSeedRandom.onclick = async () => {
    showLoader(true);
    try {
      const r = await randomSeed();
      showLoader(false);
      if (r && r.ok) {
        const s = await getState();
        applyState(s);
      } else {
        showToast('Error al generar semilla aleatoria', 'error');
      }
    } catch (err) {
      showLoader(false);
      console.error('Error en random seed:', err);
      showToast('Error al generar semilla aleatoria', 'error');
    }
  };

  function triggerUpdate() {
    const els2 = getEls();
    showLoader(true);
    const params = { terrain: state.terrain, visual: state.visual, craters: state.craters };
    console.debug('[triggerUpdate] sending params', JSON.stringify(params));
    updatePreview(params).then((res) => {
      if (res && res.ok) {
        if (res.params) {
          console.debug('[triggerUpdate] backend ok; crater params now', res.params.crater || res.params.craters);
        }
        if (res.terrain_stats) {
          applyState(res, false);
        }
        els2.preview.onload = () => { showLoader(false); };
        els2.preview.src = res.preview + '?t=' + Date.now();
      } else {
        showLoader(false);
        showToast(res?.error || 'Error al actualizar', 'error');
      }
    }).catch((err) => {
      showLoader(false);
      console.error('Error en previewUpdate:', err);
      showToast('Error de comunicación con el servidor', 'error');
    });
  }

  els.seedInput.onchange = () => { let v = parseInt(els.seedInput.value || '0'); if (isNaN(v) || v < 1) v = 1; v = Math.abs(v) % 10000000 || 1; els.seedInput.value = v; state.terrain.seed = v; triggerUpdate(); };
  els.colorInput.onchange = () => { state.visual.line_color = els.colorInput.value; els.colorSwatch.style.background = state.visual.line_color; triggerUpdate(); };
  els.chkAxes.onchange = () => { state.visual.show_axis_labels = !!els.chkAxes.checked; if (els.gridOptions) els.gridOptions.hidden = !els.chkAxes.checked; triggerUpdate(); };
  if (els.gridColor) els.gridColor.onchange = () => { state.visual.grid_color = els.gridColor.value; if (els.gridSwatch) els.gridSwatch.style.background = els.gridColor.value; triggerUpdate(); };
  if (els.gridWidth) els.gridWidth.oninput = () => { const v = parseFloat(els.gridWidth.value); state.visual.grid_width = v; if (els.gridWidthNum) els.gridWidthNum.value = v.toFixed(1); triggerUpdate(); };
  if (els.gridWidthNum) els.gridWidthNum.onchange = () => { let v = parseFloat(els.gridWidthNum.value); if (isNaN(v)) v = state.visual.grid_width ?? 0.6; v = Math.min(2.0, Math.max(0.2, v)); els.gridWidthNum.value = v.toFixed(1); els.gridWidth.value = v; state.visual.grid_width = v; triggerUpdate(); };
  if (els.gridOpacity) els.gridOpacity.oninput = () => { const v = parseInt(els.gridOpacity.value); if (els.gridOpacityNum) els.gridOpacityNum.value = v; state.visual.grid_opacity = Math.max(1, Math.min(255, v)) / 255; triggerUpdate(); };
  if (els.gridOpacityNum) els.gridOpacityNum.onchange = () => { let v = parseInt(els.gridOpacityNum.value); if (isNaN(v)) v = Math.round((state.visual.grid_opacity ?? 0.35) * 255); v = Math.min(255, Math.max(1, v)); els.gridOpacityNum.value = v; els.gridOpacity.value = v; state.visual.grid_opacity = v / 255; triggerUpdate(); };

  if (!state.craters) state.craters = {};
  els.chkCraters.onchange = () => { state.craters.enabled = !!els.chkCraters.checked; els.cratersSection.hidden = !state.craters.enabled; triggerUpdate(); };

  if (els.vh) {
    const vhHandler = () => { const v = parseFloat(els.vh.value); console.debug('[UI] vh ->', v); state.terrain.height_variation = v; if (els.vhVal) els.vhVal.textContent = v.toFixed(1); triggerUpdate(); };
    els.vh.oninput = vhHandler; els.vh.onchange = vhHandler;
  }
  if (els.rough) {
    const roughHandler = () => { const v = parseInt(els.rough.value); console.debug('[UI] roughness ->', v); state.terrain.terrain_roughness = v; if (els.roughVal) els.roughVal.textContent = `${v}%`; triggerUpdate(); };
    els.rough.oninput = roughHandler; els.rough.onchange = roughHandler;
  }
  if (els.baseHeight) {
    const baseHandler = () => { const v = parseFloat(els.baseHeight.value); console.debug('[UI] base_height ->', v); state.terrain.base_height = v; if (els.baseHeightVal) els.baseHeightVal.textContent = v.toFixed(1); triggerUpdate(); };
    els.baseHeight.oninput = baseHandler; els.baseHeight.onchange = baseHandler;
  }
  if (els.seaLevel) {
    const seaHandler = () => { const v = parseFloat(els.seaLevel.value); console.debug('[UI] sea_level ->', v); state.visual.sea_level = v; if (els.seaLevelVal) els.seaLevelVal.textContent = v.toFixed(1); triggerUpdate(); };
    els.seaLevel.oninput = seaHandler; els.seaLevel.onchange = seaHandler;
  }
  if (els.dens) {
    const densHandler = () => { const v = parseInt(els.dens.value); console.debug('[UI] contour_levels ->', v); state.visual.num_contour_levels = v; if (els.densVal) els.densVal.textContent = v; triggerUpdate(); };
    els.dens.oninput = densHandler; els.dens.onchange = densHandler;
  }

  // Crater sliders
  if (els.cDen) {
    const cDenHandler = () => { const v = parseInt(els.cDen.value); console.debug('[UI] crater density ->', v); state.craters.density = v; if (els.cDenVal) els.cDenVal.textContent = v; triggerUpdate(); };
    els.cDen.oninput = cDenHandler; els.cDen.onchange = cDenHandler;
  }
  if (els.cSize) {
    const cSizeHandler = () => { const v = parseFloat(els.cSize.value); console.debug('[UI] crater size ->', v); state.craters.size = v; if (els.cSizeVal) els.cSizeVal.textContent = v.toFixed(1); triggerUpdate(); };
    els.cSize.oninput = cSizeHandler; els.cSize.onchange = cSizeHandler;
  }
  if (els.cDepth) {
    const cDepthHandler = () => { const v = parseFloat(els.cDepth.value); console.debug('[UI] crater depth ->', v); state.craters.depth = v; if (els.cDepthVal) els.cDepthVal.textContent = v.toFixed(1); triggerUpdate(); };
    els.cDepth.oninput = cDepthHandler; els.cDepth.onchange = cDepthHandler;
  }

  els.azRange.oninput = () => { const v = clamp(parseInt(els.azRange.value), 0, 360); els.azInput.value = v; state.visual.azimuth_angle = v; triggerUpdate(); };
  els.azInput.onchange = () => { let v = parseInt(els.azInput.value); if (isNaN(v)) v = state.visual.azimuth_angle; v = clamp(v, 0, 360); els.azInput.value = v; els.azRange.value = v; state.visual.azimuth_angle = v; triggerUpdate(); };
  els.elRange.oninput = () => { const v = clamp(parseInt(els.elRange.value), 0, 90); els.elInput.value = v; state.visual.elevation_angle = v; triggerUpdate(); };
  els.elInput.onchange = () => { let v = parseInt(els.elInput.value); if (isNaN(v)) v = state.visual.elevation_angle; v = clamp(v, 0, 90); els.elInput.value = v; els.elRange.value = v; state.visual.elevation_angle = v; triggerUpdate(); };

  els.btnReset.onclick = async () => {
    showLoader(true);
    try {
      const r = await resetView();
      showLoader(false);
      if (r && r.ok) {
        const s = await getState();
        applyState(s);
      } else {
        showToast('Error al restablecer rotación', 'error');
      }
    } catch (err) {
      showLoader(false);
      console.error('Error en reset view:', err);
      showToast('Error al restablecer rotación', 'error');
    }
  };
}

async function init() {
  const s = await getState();
  applyState(s);
  wire();
}

init();
