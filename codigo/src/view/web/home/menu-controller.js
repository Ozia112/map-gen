/**
 * LATERAL MENUS CONTROLLER
 * Manages the positioning and visibility of lateral menus (Options & Export)
 */

let altura1 = 0; // Options menu hidden
let altura2 = 0; // Options menu compact (grid hidden)
let altura3 = 0; // Options menu expanded (grid visible)

/**
 * Calculate and store the three possible heights for export button/menu positioning
 */
function calculateHeights(elements) {
  altura1 = 0;

  const wasHidden = elements.lateralMenuOptions.classList.contains('hidden');
  const gridWasHidden = elements.gridOptions.classList.contains('hidden');

  elements.lateralMenuOptions.classList.remove('hidden');
  elements.gridOptions.classList.add('hidden');

  const compactHeight = elements.lateralMenuOptions.offsetHeight;
  const buttonHeight = elements.lateralButtonOptions.offsetHeight;
  const gap = 2;

  altura2 = compactHeight - buttonHeight - gap;

  elements.gridOptions.classList.remove('hidden');
  const expandedHeight = elements.lateralMenuOptions.offsetHeight;
  altura3 = expandedHeight - buttonHeight - gap;

  if (wasHidden) elements.lateralMenuOptions.classList.add('hidden');
  if (gridWasHidden) elements.gridOptions.classList.add('hidden');
}

/**
 * Get current height based on menu state
 */
function getCurrentHeight(elements) {
  const optionsVisible = !elements.lateralMenuOptions.classList.contains('hidden');
  const gridVisible = !elements.gridOptions.classList.contains('hidden');

  if (!optionsVisible) return altura1;
  else if (!gridVisible) return altura2;
  else return altura3;
}

/**
 * Update menu positions synchronously
 */
function updateMenuPositions(elements) {
  elements.lateralMenuOptions.style.top = '0px';
  elements.lateralMenuOptions.style.bottom = 'auto';

  const currentHeight = getCurrentHeight(elements);

  const btnTransition = elements.lateralButtonExport.style.transition;
  const menuTransition = elements.lateralMenuExport.style.transition;
  elements.lateralButtonExport.style.transition = 'none';
  elements.lateralMenuExport.style.transition = 'none';

  elements.lateralButtonExport.style.marginTop = currentHeight + 'px';

  // eslint-disable-next-line no-unused-expressions
  elements.lateralButtonExport.offsetHeight;

  const btnRect = elements.lateralButtonExport.getBoundingClientRect();
  elements.lateralMenuExport.style.top = btnRect.top + 'px';
  elements.lateralMenuExport.style.bottom = 'auto';

  // eslint-disable-next-line no-unused-expressions
  elements.lateralMenuExport.offsetHeight;

  elements.lateralButtonExport.style.transition = btnTransition;
  elements.lateralMenuExport.style.transition = menuTransition;
}

/**
 * Open options menu
 */
function openOptionsMenu(elements) {
  elements.lateralMenuOptions.classList.remove('hidden');
  elements.lateralButtonOptions.classList.add('active');
  updateMenuPositions(elements);
}

/**
 * Close options menu
 */
function closeOptionsMenu(elements) {
  elements.lateralMenuOptions.classList.add('hidden');
  elements.lateralButtonOptions.classList.remove('active');
  updateMenuPositions(elements);
}

/**
 * Open export menu
 */
function openExportMenu(elements) {
  elements.lateralMenuExport.classList.remove('hidden');
  elements.lateralButtonExport.classList.add('active');
}

/**
 * Close export menu
 */
function closeExportMenu(elements) {
  elements.lateralMenuExport.classList.add('hidden');
  elements.lateralButtonExport.classList.remove('active');
}

/**
 * Initialize lateral menus controller
 */
export function initLateralMenus(elements) {
  calculateHeights(elements);

  elements.lateralButtonOptions.addEventListener('click', (e) => {
    e.stopPropagation();
    openOptionsMenu(elements);
  });

  elements.lateralButtonExport.addEventListener('click', (e) => {
    e.stopPropagation();
    openExportMenu(elements);
  });

  elements.closeOptionsBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    closeOptionsMenu(elements);
  });

  elements.closeExportBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    closeExportMenu(elements);
  });

  window.addEventListener('resize', () => {
    calculateHeights(elements);
    updateMenuPositions(elements);
  });

  updateMenuPositions(elements);

  return { 
    updateMenuPositions: () => updateMenuPositions(elements),
    closeMenu: (menuName) => {
      if (menuName === 'export') closeExportMenu(elements);
      else if (menuName === 'options') closeOptionsMenu(elements);
    }
  };
}
