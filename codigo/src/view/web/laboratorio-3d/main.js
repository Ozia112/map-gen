import { 
  initDeps, 
  initScene, 
  loadTerrainMesh, 
  addPoi, 
  buildRoadBetween, 
  exportPNG, 
  exportOBJ, 
  exportSVG, 
  getPoiList, 
  applyLabelStyles, 
  addArea, 
  disposeScene, 
  setVisualizationMode 
} from './scene.js';
import { fetchHeightmap } from './services.js';

/**
 * UI Helpers
 */
const byId = (id) => document.getElementById(id);

const showLoader = (show) => {
  const el = byId('loading');
  if (el) el.classList.toggle('hidden', !show);
};

const showToast = (message, kind = 'info', timeout = 3000) => {
  const toast = document.createElement('div');
  toast.className = `toast ${kind === 'error' ? 'error' : kind === 'success' ? 'success' : ''}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), timeout);
};

const showBanner = (message, kind = 'error') => {
  const banner = byId('statusBanner');
  if (banner) {
    banner.textContent = message;
    banner.className = `toast ${kind}`;
    banner.classList.remove('hidden');
  }
};

/**
 * Navigation helpers
 */
const exitLaboratory = (ctx) => {
  const btn = byId('btnExit');
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Saliendo…';
  }
  
  showLoader(true);
  showToast('Cerrando escena 3D…', 'info', 1200);
  
  try {
    disposeScene(ctx);
  } catch (error) {
    console.error('Error disposing scene:', error);
  }
  
  // Navigate to home using multiple strategies
  setTimeout(() => {
    window.location.href = '/home';
  }, 100);
  
  // Fallback to root if still not redirected
  setTimeout(() => {
    if (window.location.pathname.includes('laboratorio-3d')) {
      window.location.href = '/';
    }
  }, 500);
};

/**
 * Initialize Three.js dependencies
 */
const initializeDependencies = async () => {
  try {
    await initDeps();
    window.__lab3dBooted = true;
    return true;
  } catch (error) {
    console.error('Failed to load Three.js dependencies:', error);
    showBanner('No se pudieron cargar librerías 3D. Verifica dependencias locales.');
    return false;
  }
};

/**
 * Load terrain heightmap
 */
const loadTerrain = async (scene) => {
  showLoader(true);
  
  try {
    const heightmap = await fetchHeightmap();
    
    if (!heightmap || !Array.isArray(heightmap.z) || heightmap.z.length === 0) {
      showBanner('No hay heightmap disponible. Genera el mapa en Home e inténtalo nuevamente.');
      return false;
    }
    
    await loadTerrainMesh(scene, heightmap);
    return true;
  } catch (error) {
    console.error('Error loading heightmap:', error);
    showToast('Error al cargar el mapa 3D.', 'error', 5000);
    showBanner('Error al cargar el mapa 3D. Genera un nuevo mapa en Home.');
    return false;
  } finally {
    showLoader(false);
  }
};

/**
 * Wire export buttons
 */
const wireExportButtons = (renderer, scene, root) => {
  byId('btnExportPng').onclick = () => {
    showToast('Exportando PNG...', 'info');
    exportPNG(renderer);
  };
  
  byId('btnExportObj').onclick = () => {
    showToast('Exportando OBJ...', 'info');
    exportOBJ(scene);
  };
  
  byId('btnExportSvg').onclick = () => {
    showToast('Exportando SVG...', 'info');
    exportSVG(scene, renderer, root);
  };

};

/**
 * Wire visualization mode selector
 */
const wireVisualizationMode = () => {
  const visMode = byId('visMode');
  if (visMode) {
    visMode.addEventListener('change', () => {
      setVisualizationMode(visMode.value);
      showToast(`Modo: ${visMode.value === 'contours' ? 'Líneas topográficas' : 'Mesh 3D'}`, 'success', 1500);
    });
  }
};

/**
 * Refresh POI selectors
 */
const refreshPoiSelectors = () => {
  const list = getPoiList();
  const options = list.map((poi, idx) => `<option value="${idx}">${poi.name}</option>`).join('');
  
  const roadFrom = byId('roadFrom');
  const roadTo = byId('roadTo');
  const poiSelect = byId('poiSelect');
  
  if (roadFrom) roadFrom.innerHTML = options;
  if (roadTo) roadTo.innerHTML = options;
  if (poiSelect) poiSelect.innerHTML = options;
};

/**
 * Wire POI controls
 */
const wirePoiControls = (scene) => {
  // Add POI
  byId('btnAddPoi').onclick = () => {
    const name = (byId('poiName').value || '').trim() || 'POI';
    const type = byId('poiType').value;
    const x = parseFloat(byId('poiX').value || '0');
    const z = parseFloat(byId('poiZ').value || '0');
    const yaw = parseFloat(byId('poiYaw').value || '0');
    
    addPoi(scene, { name, type, x, z, yaw });
    refreshPoiSelectors();
    showToast(`POI "${name}" añadido`, 'success');
  };

  // Delete single POI
  byId('btnDeletePoi').onclick = () => {
    const sel = byId('poiSelect');
    const idx = parseInt(sel.value || '-1');
    
    if (!isNaN(idx) && idx >= 0) {
      const event = new CustomEvent('remove-poi', { detail: { index: idx } });
      window.dispatchEvent(event);
      refreshPoiSelectors();
      showToast('POI eliminado', 'success');
    }
  };

  // Delete all POIs
  byId('btnDeleteAllPois').onclick = () => {
    if (getPoiList().length === 0) {
      showToast('No hay POIs para eliminar', 'info');
      return;
    }
    
    const event = new CustomEvent('clear-pois');
    window.dispatchEvent(event);
    refreshPoiSelectors();
    showToast('Todos los POIs eliminados', 'success');
  };
};

/**
 * Wire label style controls
 */
const wireLabelControls = () => {
  byId('btnApplyLabels').onclick = () => {
    const background = byId('lblBg').checked;
    const backgroundColor = byId('lblBgColor').value || 'rgba(0,0,0,0.5)';
    const bold = byId('lblBold').checked;
    const italic = byId('lblItalic').checked;
    const connector = byId('lblConnector').value;
    
    applyLabelStyles({ background, backgroundColor, bold, italic, connector });
    showToast('Estilos de etiquetas aplicados', 'success');
  };
};

/**
 * Wire area controls
 */
const wireAreaControls = () => {
  byId('btnAddArea').onclick = () => {
    const name = (byId('areaName').value || 'Área').trim();
    const shape = byId('areaShape').value;
    const pattern = byId('areaPattern').value;
    const x = parseFloat(byId('areaX').value || '20');
    const z = parseFloat(byId('areaZ').value || '20');
    const size = Math.max(4, parseFloat(byId('areaSize').value || '10'));
    
    addArea({ name, shape, pattern, x, z, size });
    showToast(`Área "${name}" añadida`, 'success');
  };
};

/**
 * Wire road generation controls
 */
const wireRoadControls = () => {
  byId('btnGenRoad').onclick = () => {
    const fromIdx = parseInt(byId('roadFrom').value || '-1');
    const toIdx = parseInt(byId('roadTo').value || '-1');
    
    if (isNaN(fromIdx) || isNaN(toIdx) || fromIdx === toIdx) {
      showToast('Selecciona dos POIs diferentes', 'error');
      return;
    }
    
    const color = byId('roadColor').value || '#ff7825';
    const width = Math.max(1, parseFloat(byId('roadWidth').value || '2'));
    const opacity = Math.min(1, Math.max(0.05, parseFloat(byId('roadOpacity').value || '0.9')));
    
    buildRoadBetween(fromIdx, toIdx, { color, width, opacity });
    showToast('Carretera generada', 'success');
  };
};

/**
 * Main initialization
 */
const boot = async () => {
  // Initialize Three.js dependencies
  const depsLoaded = await initializeDependencies();
  if (!depsLoaded) return;

  // Initialize 3D scene
  const root = byId('threeRoot');
  if (!root) {
    showBanner('Error: No se encontró el contenedor de la escena 3D');
    return;
  }

  const ctx = initScene(root);
  const { scene, renderer } = ctx;

  // Load terrain
  const terrainLoaded = await loadTerrain(scene);
  if (!terrainLoaded) return;

  // Wire all UI controls
  byId('btnExit').onclick = () => exitLaboratory(ctx);
  wireExportButtons(renderer, scene, root);
  wireVisualizationMode();
  wirePoiControls(scene);
  wireLabelControls();
  wireAreaControls();
  wireRoadControls();

  showToast('Laboratorio 3D iniciado correctamente', 'success', 2000);
};

// Start application
boot();
