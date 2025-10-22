import { loadDeps } from './deps.js';

export async function preloadThreeDeps() {
  const { cdn } = await loadDeps();
  return cdn;
}
