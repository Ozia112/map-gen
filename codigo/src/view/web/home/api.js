import { showLoader } from './ui.js';

function eel() {
  const e = (typeof window !== 'undefined' ? window.eel : undefined) || (typeof globalThis !== 'undefined' ? globalThis.eel : undefined);
  if (!e) throw new Error('Eel no está disponible en el contexto global');
  return e;
}

export async function getState() {
  return await eel().api_get_state()();
}

export async function updatePreview(state) {
  showLoader(true);
  try {
    const res = await eel().api_update(state)();
    return res;
  } finally {
    // caller hides loader on image load
  }
}

export async function randomSeed() {
  return await eel().api_random_seed()();
}

export async function resetView() {
  return await eel().api_reset_view()();
}

export async function suggestDownloadPath() {
  try { return await eel().api_suggest_download_path()(); } catch { return undefined; }
}

export async function selectSavePath() {
  try { return await eel().api_select_save_path()(); } catch { return undefined; }
}

export async function exportOptions(opts) {
  return await eel().api_export_options(opts)();
}
