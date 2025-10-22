import { getEls, showLoader, showToast } from './ui.js';
import { state, applyState } from './state.js';
import { getState, updatePreview, suggestDownloadPath, selectSavePath, exportOptions } from './api.js';
import { initLateralMenus } from './menu-controller.js';

/**
 * Debounce utility
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Update preview by sending current state to backend
 */
const handleUpdate = debounce(async () => {
  showLoader(true);
  try {
    const params = { terrain: state.terrain, visual: state.visual, craters: state.craters };
    const res = await updatePreview(params);
    
    if (res && res.ok) {
      if (res.preview) {
        const els = getEls();
        els.preview.src = res.preview + '?t=' + Date.now();
        els.preview.classList.remove('hidden');
      }
      
      if (res.terrain_stats && res.terrain_stats.max_height !== undefined) {
        const maxHeight = Math.floor(res.terrain_stats.max_height);
        const els = getEls();
        if (els.seaLevelSlider) {
          els.seaLevelSlider.max = String(maxHeight);
          if (state.visual.sea_level > maxHeight) {
            state.visual.sea_level = maxHeight;
            els.seaLevelSlider.value = String(maxHeight);
            els.seaLevelValue.value = String(maxHeight);
          }
        }
      }
    } else {
      showToast(res?.error || 'Error al actualizar', 'error');
    }
  } catch (error) {
    showToast('Error al actualizar', 'error');
  } finally {
    showLoader(false);
  }
}, 250);

/**
 * Wire up slider and its value input to state property
 */
function wireSlider(sliderEl, valueEl, stateObject, key, formatter = null) {
  if (!sliderEl || !valueEl) return;
  
  const formatValue = (value) => {
    if (formatter) return String(formatter(value));
    const decimals = sliderEl.step && sliderEl.step.includes('.') ? 1 : 0;
    return value.toFixed(decimals);
  };
  
  const parseValue = (str) => {
    const cleaned = str.replace(/[^\d.-]/g, '');
    return parseFloat(cleaned) || 0;
  };
  
  sliderEl.addEventListener('input', () => {
    const value = parseFloat(sliderEl.value);
    stateObject[key] = value;
    valueEl.value = formatValue(value);
    handleUpdate();
  });
  
  valueEl.addEventListener('input', () => {
    const value = parseValue(valueEl.value);
    const min = parseFloat(sliderEl.min);
    const max = parseFloat(sliderEl.max);
    const clampedValue = Math.max(min, Math.min(max, value));
    stateObject[key] = clampedValue;
    sliderEl.value = clampedValue;
  });
  
  valueEl.addEventListener('blur', () => {
    const value = parseValue(valueEl.value);
    const min = parseFloat(sliderEl.min);
    const max = parseFloat(sliderEl.max);
    const clampedValue = Math.max(min, Math.min(max, value));
    stateObject[key] = clampedValue;
    sliderEl.value = clampedValue;
    valueEl.value = formatValue(clampedValue);
    handleUpdate();
  });
  
  valueEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') valueEl.blur();
  });
}

/**
 * Wire up all UI event listeners
 */
function wireEventListeners() {
  const els = getEls();

  if (els.lab3dButton) {
    els.lab3dButton.addEventListener('click', async () => {
      showLoader(true);
      try {
        const mod = await import('../laboratorio-3d/preload.js');
        await mod.preloadThreeDeps();
        window.location.href = '/laboratorio-3d';
      } catch (e) {
        showToast('No se pudieron preparar las librerías 3D.', 'error');
        showLoader(false);
      }
    });
  }

  if (els.chkCraters) {
    els.chkCraters.addEventListener('change', () => {
      const enabled = els.chkCraters.checked;
      state.craters.enabled = enabled;
      els.cratersSection.classList.toggle('hidden', !enabled);
      handleUpdate();
    });
  }

  wireSlider(els.vh, els.vhVal, state.terrain, 'height_variation');
  wireSlider(els.rough, els.roughVal, state.terrain, 'terrain_roughness', (v) => `${Math.round(v)}%`);
  wireSlider(els.dens, els.densVal, state.visual, 'num_contour_levels', (v) => `${Math.round(v)}`);
  wireSlider(els.azRange, els.azVal, state.visual, 'azimuth_angle', (v) => `${Math.round(v)}°`);
  wireSlider(els.elRange, els.elVal, state.visual, 'elevation_angle', (v) => `${Math.round(v)}°`);
  wireSlider(els.cDen, els.cDenVal, state.craters, 'density', (v) => `${Math.round(v)}`);
  wireSlider(els.cSize, els.cSizeVal, state.craters, 'size', (v) => `${v.toFixed(1)}`);
  wireSlider(els.cDepth, els.cDepthVal, state.craters, 'depth', (v) => `${v.toFixed(1)}`);

  wireMenuControls(els);
}

/**
 * Wire up menu-specific controls
 */
function wireMenuControls(els) {
  const menuController = initLateralMenus(els);

  // Estado del menú de exportación
  let selectedScale = 1;
  let selectedSavePath = null;

  // Inicializar ruta por defecto
  (async () => {
    const defaultPath = await suggestDownloadPath();
    if (defaultPath) {
      selectedSavePath = defaultPath;
      const folderName = defaultPath.split(/[/\\]/).pop() || 'Descargas';
      els.exportPathDisplay.textContent = folderName;
      els.exportPathDisplay.title = defaultPath;
    }
  })();

  // Cambio de formato: habilitar/deshabilitar escala
  els.exportFormat.addEventListener('change', () => {
    const format = els.exportFormat.value;
    const isSvg = format === 'svg';
    
    // Deshabilitar escala para SVG
    els.exportScaleSection.style.opacity = isSvg ? '0.5' : '1';
    els.exportScale1x.disabled = isSvg;
    els.exportScale2x.disabled = isSvg;
    els.exportScale4x.disabled = isSvg;
  });

  // Botones de escala
  const scaleButtons = [els.exportScale1x, els.exportScale2x, els.exportScale4x];
  
  scaleButtons.forEach(button => {
    button.addEventListener('click', () => {
      if (button.disabled) return;
      
      // Remover active de todos
      scaleButtons.forEach(btn => btn.classList.remove('active'));
      
      // Activar el clickeado
      button.classList.add('active');
      selectedScale = parseInt(button.dataset.scale);
    });
  });

  // Seleccionar carpeta de guardado
  els.exportSelectPath.addEventListener('click', async () => {
    try {
      const path = await selectSavePath();
      if (path) {
        selectedSavePath = path;
        const folderName = path.split(/[/\\]/).pop() || path;
        els.exportPathDisplay.textContent = folderName;
        els.exportPathDisplay.title = path;
      }
    } catch (error) {
      console.error('Error selecting path:', error);
      showToast('Error al seleccionar carpeta', 'error');
    }
  });

  // Botón de exportar
  els.exportConfirm.addEventListener('click', async () => {
    const format = els.exportFormat.value;
    
    showLoader(true);
    showToast(`Exportando como ${format.toUpperCase()}...`, 'info');
    
    try {
      // Usar la ruta seleccionada o la por defecto
      const savePath = selectedSavePath || await suggestDownloadPath();
      
      if (!savePath) {
        showToast('No se pudo determinar la ruta de guardado', 'error');
        showLoader(false);
        return;
      }
      
      // Generar nombre de archivo
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const filename = `terrain_map_${timestamp}.${format}`;
      const fullPath = `${savePath}/${filename}`;
      
      // Obtener escala (para SVG siempre es 1)
      const scale = format === 'svg' ? 1 : selectedScale;
      
      // Llamar a la API de exportación
      const result = await exportOptions({
        fmt: format,
        path: fullPath,
        scale: scale,
        includeGrid: state.visual.show_axis_labels
      });
      
      if (result && result.ok) {
        showToast(`✓ Exportado exitosamente: ${filename}`, 'success', 4000);
        // NO cerrar el menú - comportamiento esperado
      } else {
        showToast(result?.error || 'Error al exportar', 'error');
      }
    } catch (error) {
      console.error('Export error:', error);
      showToast('Error al exportar el mapa', 'error');
    } finally {
      showLoader(false);
    }
  });

  els.seedInput.addEventListener('change', () => {
    let value = parseInt(els.seedInput.value.replace(/\D/g, '')) || 1;
    value = Math.max(1, Math.min(100000, Math.abs(value)));
    els.seedInput.value = String(value).padStart(6, '0');
    state.terrain.seed = value;
    handleUpdate();
  });

  els.randomSeedBtn.addEventListener('click', () => {
    const randomSeed = Math.floor(Math.random() * 100000) + 1;
    els.seedInput.value = String(randomSeed).padStart(6, '0');
    state.terrain.seed = randomSeed;
    handleUpdate();
  });

  els.colorSwatch.addEventListener('click', () => {
    els.lineColorInput.click();
  });

  els.lineColorInput.addEventListener('input', () => {
    const color = els.lineColorInput.value;
    els.colorSwatch.style.backgroundColor = color;
    els.lineColorHex.value = color.toUpperCase();
    state.visual.line_color = color;
    handleUpdate();
  });

  els.lineColorHex.addEventListener('change', () => {
    let hex = els.lineColorHex.value.trim().toUpperCase().replace('#', '');
    if (/^[0-9A-F]{6}$/.test(hex)) {
      const color = '#' + hex;
      els.lineColorInput.value = color;
      els.colorSwatch.style.backgroundColor = color;
      els.lineColorHex.value = color;
      state.visual.line_color = color;
      handleUpdate();
    } else {
      const currentColor = state.visual.line_color ?? '#FF7825';
      els.lineColorHex.value = currentColor.toUpperCase();
    }
  });

  els.baseHeightSlider.addEventListener('input', () => {
    const value = parseInt(els.baseHeightSlider.value);
    state.terrain.base_height = value;
    els.baseHeightValue.value = String(value);
    handleUpdate();
  });

  els.baseHeightValue.addEventListener('change', () => {
    let value = parseInt(els.baseHeightValue.value) || 5;
    value = Math.max(5, Math.min(30, value));
    state.terrain.base_height = value;
    els.baseHeightSlider.value = String(value);
    els.baseHeightValue.value = String(value);
    handleUpdate();
  });

  els.seaLevelSlider.addEventListener('input', () => {
    const value = parseInt(els.seaLevelSlider.value);
    state.visual.sea_level = value;
    els.seaLevelValue.value = String(value);
    handleUpdate();
  });

  els.seaLevelValue.addEventListener('change', () => {
    let value = parseInt(els.seaLevelValue.value) || 0;
    const maxValue = parseInt(els.seaLevelSlider.max) || 30;
    value = Math.max(0, Math.min(maxValue, value));
    state.visual.sea_level = value;
    els.seaLevelSlider.value = String(value);
    els.seaLevelValue.value = String(value);
    handleUpdate();
  });

  els.gridToggle.addEventListener('change', () => {
    const enabled = els.gridToggle.checked;
    state.visual.show_axis_labels = enabled;
    els.gridOptions.classList.toggle('hidden', !enabled);
    menuController.updateMenuPositions();
    handleUpdate();
  });

  els.gridColorSwatch.addEventListener('click', () => {
    els.gridColorInput.click();
  });

  els.gridColorInput.addEventListener('input', () => {
    const color = els.gridColorInput.value;
    els.gridColorSwatch.style.backgroundColor = color;
    els.gridColorHex.value = color.toUpperCase();
    state.visual.grid_color = color;
    handleUpdate();
  });

  els.gridColorHex.addEventListener('change', () => {
    let hex = els.gridColorHex.value.trim().toUpperCase().replace('#', '');
    if (/^[0-9A-F]{6}$/.test(hex)) {
      const color = '#' + hex;
      els.gridColorInput.value = color;
      els.gridColorSwatch.style.backgroundColor = color;
      els.gridColorHex.value = color;
      state.visual.grid_color = color;
      handleUpdate();
    } else {
      const currentColor = state.visual.grid_color ?? '#00FFFF';
      els.gridColorHex.value = currentColor.toUpperCase();
    }
  });

  els.gridWidthSlider.addEventListener('input', () => {
    const pxValue = parseInt(els.gridWidthSlider.value);
    const internalValue = pxValue / 3.33;
    state.visual.grid_width = internalValue;
    els.gridWidthValue.value = pxValue + 'px';
    handleUpdate();
  });

  els.gridWidthValue.addEventListener('change', () => {
    let pxValue = parseInt(els.gridWidthValue.value.replace(/\D/g, '')) || 1;
    pxValue = Math.max(1, Math.min(6, pxValue));
    const internalValue = pxValue / 3.33;
    state.visual.grid_width = internalValue;
    els.gridWidthSlider.value = String(pxValue);
    els.gridWidthValue.value = pxValue + 'px';
    handleUpdate();
  });

  els.gridOpacitySlider.addEventListener('input', () => {
    const opacity255 = parseInt(els.gridOpacitySlider.value);
    const internalValue = opacity255 / 255;
    state.visual.grid_opacity = internalValue;
    els.gridOpacityValue.value = String(opacity255);
    handleUpdate();
  });

  els.gridOpacityValue.addEventListener('change', () => {
    let opacity255 = parseInt(els.gridOpacityValue.value) || 1;
    opacity255 = Math.max(1, Math.min(255, opacity255));
    const internalValue = opacity255 / 255;
    state.visual.grid_opacity = internalValue;
    els.gridOpacitySlider.value = String(opacity255);
    els.gridOpacityValue.value = String(opacity255);
    handleUpdate();
  });

  els.resetRotationBtn.addEventListener('click', () => {
    const defaultAzimuth = 340;
    const defaultElevation = 24;
    
    els.azRange.value = defaultAzimuth;
    els.azVal.value = `${defaultAzimuth}°`;
    state.visual.azimuth_angle = defaultAzimuth;
    
    els.elRange.value = defaultElevation;
    els.elVal.value = `${defaultElevation}°`;
    state.visual.elevation_angle = defaultElevation;
    
    handleUpdate();
  });
}

/**
 * Main initialization function
 */
async function main() {
  showLoader(true);
  try {
    const initialState = await getState();
    if (initialState) {
      applyState(initialState);
    }
    wireEventListeners();
    await handleUpdate();
  } catch (error) {
    showToast('Error al inicializar la aplicación', 'error');
  } finally {
    showLoader(false);
  }
}

document.addEventListener('DOMContentLoaded', main);
