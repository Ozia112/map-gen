// UI helpers and element getters

export function getEls() {
  return {
    preview: document.getElementById('preview'),
    btnExport: document.getElementById('btnExport'),
    btnOpenOptions: document.getElementById('btnOpenOptions'),
    btnCloseOptions: document.getElementById('btnCloseOptions'),
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
    baseHeight: document.getElementById('baseHeight'), baseHeightVal: document.getElementById('baseHeightVal'),
    seaLevel: document.getElementById('seaLevel'), seaLevelVal: document.getElementById('seaLevelVal'),
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
    t.textContent = message;
    document.body.appendChild(t);
    setTimeout(() => { t.remove(); }, timeout);
  } catch { /* noop */ }
}

export function placeSideTab(btnOptionsTab, sidebar) {
  if (!btnOptionsTab || !sidebar) return;
  const sb = sidebar.getBoundingClientRect();
  const tabRect = btnOptionsTab.getBoundingClientRect();
  const left = sb.left - tabRect.width - 0;
  let top = sb.top + 80;
  top = Math.max(16, Math.min(top, window.innerHeight - 80));
  btnOptionsTab.style.left = `${left}px`;
  btnOptionsTab.style.top = `${top}px`;
}
