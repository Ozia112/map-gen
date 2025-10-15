/* global eel */
const els = {
  preview: document.getElementById('preview'),
  btnExport: document.getElementById('btnExport'),
  btnOpenOptions: document.getElementById('btnOpenOptions'),
  btnCloseOptions: document.getElementById('btnCloseOptions'),
  // Replaced overlay-based open with side-tab floating panel
  optPanel: document.getElementById('optPanel'),
  btnOptionsTab: document.getElementById('btnOptionsTab'),
  seedInput: document.getElementById('seedInput'),
  btnSeedRandom: document.getElementById('btnSeedRandom'),
  colorInput: document.getElementById('colorInput'),
  colorSwatch: document.getElementById('colorSwatch'),
  chkAxes: document.getElementById('chkAxes'),
  gridOptions: document.getElementById('gridOptions'),
  gridColor: document.getElementById('gridColor'),
  gridSwatch: document.getElementById('gridSwatch'),
  gridWidth: document.getElementById('gridWidth'),
  gridWidthNum: document.getElementById('gridWidthNum'),
  gridOpacity: document.getElementById('gridOpacity'),
  gridOpacityNum: document.getElementById('gridOpacityNum'),
  chkCraters: document.getElementById('chkCraters'),
  vh: document.getElementById('vh'), vhVal: document.getElementById('vhVal'),
  rough: document.getElementById('rough'), roughVal: document.getElementById('roughVal'),
  dens: document.getElementById('dens'), densVal: document.getElementById('densVal'),
  btnReset: document.getElementById('btnReset'),
  azInput: document.getElementById('azInput'), azRange: document.getElementById('azRange'),
  elInput: document.getElementById('elInput'), elRange: document.getElementById('elRange'),
  cratersSection: document.getElementById('cratersSection'),
  cDen: document.getElementById('cDen'), cDenVal: document.getElementById('cDenVal'),
  cSize: document.getElementById('cSize'), cSizeVal: document.getElementById('cSizeVal'),
  cDepth: document.getElementById('cDepth'), cDepthVal: document.getElementById('cDepthVal'),
  // Export modal
  exportModal: document.getElementById('exportModal'),
  expPath: document.getElementById('expPath'),
  expBrowse: document.getElementById('expBrowse'),
  expFmtPng: document.getElementById('expFmtPng'),
  expFmtSvg: document.getElementById('expFmtSvg'),
  expChkGrid: document.getElementById('expChkGrid'),
  expScale: document.getElementById('expScale'),
  expSave: document.getElementById('expSave'),
  expClose: document.getElementById('expClose')
};

const state = { terrain: {}, visual: {} };

function applyState(s) {
  Object.assign(state.terrain, s.terrain);
  Object.assign(state.visual, s.visual);
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
    // Opacidad llega 0..1; UI muestra 1..255
    const go01 = state.visual.grid_opacity ?? 0.35;
    const go255 = Math.round(Math.min(1, Math.max(0.01, go01)) * 255);
    els.gridOpacity.value = go255;
    if (els.gridOpacityNum) els.gridOpacityNum.value = go255;
  }
  els.chkCraters.checked = !!state.terrain.crater_enabled;
  // Sliders
  els.vh.value = state.terrain.height_variation; els.vhVal.textContent = state.terrain.height_variation.toFixed(1);
  els.rough.value = state.terrain.terrain_roughness; els.roughVal.textContent = `${state.terrain.terrain_roughness}%`;
  els.dens.value = state.visual.num_contour_levels; els.densVal.textContent = state.visual.num_contour_levels;
  // Rotación (inputs + sliders)
  els.azInput.value = Math.round(state.visual.azimuth_angle);
  els.azRange.value = Math.round(state.visual.azimuth_angle);
  els.elInput.value = Math.round(state.visual.elevation_angle);
  els.elRange.value = Math.round(state.visual.elevation_angle);
  // Cráteres
  els.cratersSection.hidden = !state.terrain.crater_enabled;
  els.cDen.value = state.terrain.num_craters; els.cDenVal.textContent = state.terrain.num_craters;
  els.cSize.value = state.terrain.crater_size; els.cSizeVal.textContent = state.terrain.crater_size.toFixed(1);
  els.cDepth.value = state.terrain.crater_depth; els.cDepthVal.textContent = state.terrain.crater_depth.toFixed(1);
  // Sin gizmo: no dibujo adicional
}

function previewUpdate() {
  showLoader(true);
  eel.api_update(state)().then((res) => {
    els.preview.onload = ()=> { showLoader(false); };
    els.preview.src = res.preview + '?t=' + Date.now();
  }).catch(()=> showLoader(false));
}

function showLoader(show){
  const el = document.getElementById('loading');
  if(!el) return; el.classList.toggle('hidden', !show);
}

function showToast(message, kind='info', timeout=3000){
  try{
    const t = document.createElement('div');
    t.className = 'toast' + (kind==='error'?' error':(kind==='success'?' success':''));
    t.textContent = message;
    document.body.appendChild(t);
    setTimeout(()=>{ t.remove(); }, timeout);
  }catch{}
}

// Eliminado gizmo: rotación solo con inputs/sliders

// Event wiring
function wire() {
  // Export modal open
  if (els.btnExport) els.btnExport.onclick = async () => {
    // Prefill defaults: path under Descargas, format based on toggle, grid from current, scale x1
    try {
      const sug = await eel.api_suggest_download_path()();
      if (sug && typeof sug === 'string' && !els.expPath.value) {
        els.expPath.placeholder = sug;
        els.expPath.value = sug;
        els.expPath.title = sug;
      }
    } catch { if (!els.expPath.value) els.expPath.value = '/Descargas/'; }
    els.expChkGrid.checked = !!state.visual.show_axis_labels;
    els.expScale.value = '1';
    setFormat('png');
    if (els.exportModal) els.exportModal.classList.remove('hidden');
    // Posicionar el panel encima del botón Exportar (sin animar)
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

  function setFormat(fmt){
    const isPng = fmt === 'png';
    els.expFmtPng.classList.toggle('active', isPng);
    els.expFmtSvg.classList.toggle('active', !isPng);
    els.expFmtPng.dataset.fmt = 'png';
    els.expFmtSvg.dataset.fmt = 'svg';
  }
  if (els.expFmtPng) els.expFmtPng.onclick = ()=> { setFormat('png'); if (els.expScale) { els.expScale.disabled = false; } };
  if (els.expFmtSvg) els.expFmtSvg.onclick = ()=> { setFormat('svg'); if (els.expScale) { els.expScale.disabled = true; } };

  if (els.expClose) els.expClose.onclick = ()=> { if (els.exportModal) els.exportModal.classList.add('hidden'); };

  // Cerrar al hacer click fuera del diálogo (sin ofuscar el fondo)
  document.addEventListener('click', (ev)=>{
    const panel = els.exportModal;
    if (!panel || panel.classList.contains('hidden')) return;
    const isInside = panel.contains(ev.target) || (els.btnExport && els.btnExport.contains(ev.target));
    if (!isInside) panel.classList.add('hidden');
  });

  if (els.expBrowse) els.expBrowse.onclick = async ()=> {
    // Requerimiento: al pulsar '…' iniciar directamente descarga del navegador (Edge)
    const fmt = els.expFmtSvg.classList.contains('active') ? 'svg' : 'png';
    const includeGrid = !!els.expChkGrid.checked;
    const scale = parseInt(els.expScale.value || '1');
    const url = `/export?fmt=${encodeURIComponent(fmt)}&includeGrid=${includeGrid?'1':'0'}&scale=${encodeURIComponent(scale)}`;
    showToast('Generando archivo…', 'info');
    window.open(url, '_blank');
    if (els.exportModal) els.exportModal.classList.add('hidden');
  };

  if (els.expSave) els.expSave.onclick = async () => {
    const fmt = els.expFmtSvg.classList.contains('active') ? 'svg' : 'png';
    const includeGrid = !!els.expChkGrid.checked;
    const scale = parseInt(els.expScale.value || '1');
    const path = (els.expPath.value || '').trim();
    // Requerimiento: Guardar directo usa la ruta autodetectada; si ruta vacía o inválida, usar gestor de descargas del navegador
    if (!path || path === '/Descargas/') {
      const url = `/export?fmt=${encodeURIComponent(fmt)}&includeGrid=${includeGrid?'1':'0'}&scale=${encodeURIComponent(scale)}`;
      showToast('Generando archivo…', 'info');
      window.open(url, '_blank');
      if (els.exportModal) els.exportModal.classList.add('hidden');
      setTimeout(()=> showToast('Descarga iniciada.', 'success'), 600);
      return;
    }
    showLoader(true);
    try {
      const res = await eel.api_export_options({ fmt, includeGrid, scale, path })();
      if (res && res.ok) {
        if (els.exportModal) els.exportModal.classList.add('hidden');
        showToast('Guardado correctamente.', 'success', 3000);
      } else {
        showToast('No se pudo guardar el archivo.', 'error', 4000);
      }
    } catch { /* ignore */ }
    showLoader(false);
  };
  // Options panel (side-tab behavior): open over the tab button; close on outside click/⦿
  let _optOutsideHandler = null;
  const openOptions = (anchorEl) => {
    if (!els.optPanel) return;
    els.optPanel.classList.remove('hidden');
    try {
      if (anchorEl && anchorEl.getBoundingClientRect) {
        const rect = anchorEl.getBoundingClientRect();
        const panelRect = els.optPanel.getBoundingClientRect();
        // Align panel so it appears to expand from the tab toward the left side (away from sidebar)
        let top = rect.top;
  let left = rect.left - panelRect.width + 34; // nudge 12px to the right compared to -8
        // Keep within viewport vertically
        if (top + panelRect.height > window.innerHeight - 16) {
          top = Math.max(16, window.innerHeight - panelRect.height - 16);
        }
        // Keep within viewport horizontally
        if (left < 16) {
          left = 16;
        }
        els.optPanel.style.top = `${top}px`;
        els.optPanel.style.left = `${left}px`;
        els.optPanel.style.right = 'auto';
      }
    } catch {}
    // outside click handler
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
  if (els.btnOptionsTab) els.btnOptionsTab.onclick = (e)=> { e.stopPropagation(); openOptions(e.currentTarget); };
  if (els.btnCloseOptions) els.btnCloseOptions.onclick = (e)=> { e.stopPropagation(); closeOptions(); };

  // Position the side tab along the left edge of the sidebar
  const sidebar = document.querySelector('aside.panel');
  const placeSideTab = () => {
    if (!els.btnOptionsTab || !sidebar) return;
    const sb = sidebar.getBoundingClientRect();
    // Place the tab exactly outside the sidebar's left edge so the right border touches the sidebar's left border
    const tabRect = els.btnOptionsTab.getBoundingClientRect();
    const left = sb.left - tabRect.width - 0; // right edge of tab flush with sidebar left edge
    let top = sb.top + 80; // approximate vertical placement near first section label
    // Keep on screen
    top = Math.max(16, Math.min(top, window.innerHeight - 80));
    els.btnOptionsTab.style.left = `${left}px`;
    els.btnOptionsTab.style.top = `${top}px`;
  };
  placeSideTab();
  window.addEventListener('resize', placeSideTab);
  els.btnSeedRandom.onclick = ()=> eel.api_random_seed()().then((r)=>{ state.terrain.seed=r.seed; applyState({terrain:state.terrain, visual:state.visual, preview:r.preview}); });
  els.seedInput.onchange = ()=> { let v = parseInt(els.seedInput.value||'0'); if(isNaN(v)||v<1) v = 1; v = Math.abs(v)%10000000 || 1; els.seedInput.value = v; state.terrain.seed = v; previewUpdate(); };
  els.colorInput.onchange = ()=> { state.visual.line_color = els.colorInput.value; els.colorSwatch.style.background = state.visual.line_color; previewUpdate(); };
  els.chkAxes.onchange = ()=> { state.visual.show_axis_labels = !!els.chkAxes.checked; if (els.gridOptions) els.gridOptions.hidden = !els.chkAxes.checked; previewUpdate(); };
  if (els.gridColor) els.gridColor.onchange = ()=> { state.visual.grid_color = els.gridColor.value; if (els.gridSwatch) els.gridSwatch.style.background = els.gridColor.value; previewUpdate(); };
  if (els.gridWidth) els.gridWidth.oninput = ()=> { const v = parseFloat(els.gridWidth.value); state.visual.grid_width = v; if (els.gridWidthNum) els.gridWidthNum.value = v.toFixed(1); previewUpdate(); };
  if (els.gridWidthNum) els.gridWidthNum.onchange = ()=> { let v = parseFloat(els.gridWidthNum.value); if (isNaN(v)) v = state.visual.grid_width ?? 0.6; v = Math.min(2.0, Math.max(0.2, v)); els.gridWidthNum.value = v.toFixed(1); els.gridWidth.value = v; state.visual.grid_width = v; previewUpdate(); };
  if (els.gridOpacity) els.gridOpacity.oninput = ()=> { const v = parseInt(els.gridOpacity.value); if (els.gridOpacityNum) els.gridOpacityNum.value = v; state.visual.grid_opacity = Math.max(1, Math.min(255, v)) / 255; previewUpdate(); };
  if (els.gridOpacityNum) els.gridOpacityNum.onchange = ()=> { let v = parseInt(els.gridOpacityNum.value); if (isNaN(v)) v = Math.round((state.visual.grid_opacity ?? 0.35) * 255); v = Math.min(255, Math.max(1, v)); els.gridOpacityNum.value = v; els.gridOpacity.value = v; state.visual.grid_opacity = v / 255; previewUpdate(); };
  els.chkCraters.onchange = ()=> { state.terrain.crater_enabled = !!els.chkCraters.checked; els.cratersSection.hidden = !state.terrain.crater_enabled; previewUpdate(); };

  els.vh.oninput = ()=> { state.terrain.height_variation = parseFloat(els.vh.value); els.vhVal.textContent = state.terrain.height_variation.toFixed(1); previewUpdate(); };
  els.rough.oninput = ()=> { state.terrain.terrain_roughness = parseInt(els.rough.value); els.roughVal.textContent = `${state.terrain.terrain_roughness}%`; previewUpdate(); };
  els.dens.oninput = ()=> { state.visual.num_contour_levels = parseInt(els.dens.value); els.densVal.textContent = state.visual.num_contour_levels; previewUpdate(); };
  // Rotación: AZ
  const clamp = (v,min,max)=> Math.max(min, Math.min(max, v));
  els.azRange.oninput = ()=> { const v = clamp(parseInt(els.azRange.value),0,360); els.azInput.value = v; state.visual.azimuth_angle = v; previewUpdate(); };
  els.azInput.onchange = ()=> { let v = parseInt(els.azInput.value); if(isNaN(v)) v = state.visual.azimuth_angle; v = clamp(v,0,360); els.azInput.value=v; els.azRange.value=v; state.visual.azimuth_angle=v; previewUpdate(); };
  // Rotación: EL
  els.elRange.oninput = ()=> { const v = clamp(parseInt(els.elRange.value),0,90); els.elInput.value = v; state.visual.elevation_angle = v; previewUpdate(); };
  els.elInput.onchange = ()=> { let v = parseInt(els.elInput.value); if(isNaN(v)) v = state.visual.elevation_angle; v = clamp(v,0,90); els.elInput.value=v; els.elRange.value=v; state.visual.elevation_angle=v; previewUpdate(); };

  els.cDen.oninput = ()=> { state.terrain.num_craters = parseInt(els.cDen.value); els.cDenVal.textContent = state.terrain.num_craters; previewUpdate(); };
  els.cSize.oninput = ()=> { state.terrain.crater_size = parseFloat(els.cSize.value); els.cSizeVal.textContent = state.terrain.crater_size.toFixed(1); previewUpdate(); };
  els.cDepth.oninput = ()=> { state.terrain.crater_depth = parseFloat(els.cDepth.value); els.cDepthVal.textContent = state.terrain.crater_depth.toFixed(1); previewUpdate(); };

  els.btnReset.onclick = ()=> { eel.api_reset_view()().then((r)=>{ state.visual.azimuth_angle=r.az; state.visual.elevation_angle=r.el; applyState({terrain:state.terrain, visual:state.visual, preview:r.preview}); }); };

}

async function init(){
  const s = await eel.api_get_state()();
  applyState(s); wire();
}

init();
