// UI helpers and element getters (home page)

export function getEls() {
  return {
    // Main elements
    preview: document.getElementById('preview'),
    lab3dButton: document.getElementById('lab3dButton'),
    loading: document.getElementById('loading'),
    
    // Terrain parameters
    vh: document.getElementById('vh'),
    vhVal: document.getElementById('vhVal'),
    rough: document.getElementById('rough'),
    roughVal: document.getElementById('roughVal'),
    dens: document.getElementById('dens'),
    densVal: document.getElementById('densVal'),
    
    // Rotation
    azRange: document.getElementById('azRange'),
    azVal: document.getElementById('azVal'),
    elRange: document.getElementById('elRange'),
    elVal: document.getElementById('elVal'),
    
    // Craters
    chkCraters: document.getElementById('chkCraters'),
    cratersSection: document.getElementById('cratersSection'),
    cDen: document.getElementById('cDen'),
    cDenVal: document.getElementById('cDenVal'),
    cSize: document.getElementById('cSize'),
    cSizeVal: document.getElementById('cSizeVal'),
    cDepth: document.getElementById('cDepth'),
    cDepthVal: document.getElementById('cDepthVal'),
    
    // Lateral buttons and menus
    lateralButtonExport: document.getElementById('lateral-button-export'),
    lateralButtonOptions: document.getElementById('lateral-button-options'),
    lateralMenuExport: document.getElementById('lateral-menu-export'),
    lateralMenuOptions: document.getElementById('lateral-menu-options'),
    
    // Options menu controls
    closeOptionsBtn: document.getElementById('closeOptionsBtn'),
    seedInput: document.getElementById('seedInput'),
    randomSeedBtn: document.getElementById('randomSeedBtn'),
    lineColorInput: document.getElementById('lineColorInput'),
    lineColorHex: document.getElementById('lineColorHex'),
    colorSwatch: document.getElementById('colorSwatch'),
    baseHeightSlider: document.getElementById('baseHeightSlider'),
    baseHeightValue: document.getElementById('baseHeightValue'),
    seaLevelSlider: document.getElementById('seaLevelSlider'),
    seaLevelValue: document.getElementById('seaLevelValue'),
    gridToggle: document.getElementById('gridToggle'),
    gridOptions: document.getElementById('gridOptions'),
    gridColorInput: document.getElementById('gridColorInput'),
    gridColorHex: document.getElementById('gridColorHex'),
    gridColorSwatch: document.getElementById('gridColorSwatch'),
    gridWidthSlider: document.getElementById('gridWidthSlider'),
    gridWidthValue: document.getElementById('gridWidthValue'),
    gridOpacitySlider: document.getElementById('gridOpacitySlider'),
    gridOpacityValue: document.getElementById('gridOpacityValue'),
    
    // Reset buttons
    resetRotationBtn: document.getElementById('resetRotationBtn'),
    
    // Export menu controls
    closeExportBtn: document.getElementById('closeExportBtn'),
    exportFormat: document.getElementById('exportFormat'),
    exportScaleSection: document.getElementById('exportScaleSection'),
    exportScale1x: document.getElementById('exportScale1x'),
    exportScale2x: document.getElementById('exportScale2x'),
    exportScale4x: document.getElementById('exportScale4x'),
    exportSelectPath: document.getElementById('exportSelectPath'),
    exportPathDisplay: document.getElementById('exportPathDisplay'),
    exportConfirm: document.getElementById('exportConfirm'),
  };
}

export function showLoader(show) {
  const el = document.getElementById('loading');
  if (!el) return;
  el.classList.toggle('hidden', !show);
}

export function showToast(message, kind = 'info', timeout = 3000) {
  try {
    const t = document.createElement('div');
    t.className = 'toast' + (kind === 'error' ? ' error' : (kind === 'success' ? ' success' : ''));
    t.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      padding: 12px 20px;
      background: ${kind === 'error' ? '#d32f2f' : kind === 'success' ? '#388e3c' : '#1976d2'};
      color: white;
      border-radius: 4px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      z-index: 10000;
      animation: slideIn 0.3s ease-out;
    `;
    t.textContent = message;
    document.body.appendChild(t);
    setTimeout(() => { 
      t.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => t.remove(), 300);
    }, timeout);
  } catch { /* noop */ }
}

