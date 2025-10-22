/**
 * API Services for Laboratorio 3D
 * Handles communication with backend for heightmap data
 */

/**
 * Fetch heightmap data from backend
 * @returns {Promise<{width: number, height: number, z: number[][]}>}
 */
export async function fetchHeightmap() {
  try {
    const response = await eel.api_get_heightmap()();
    
    if (!response) {
      throw new Error('No response from backend');
    }
    
    // El backend devuelve directamente el heightmap, no dentro de un objeto heightmap
    // Verificar ambos formatos para compatibilidad
    const heightmap = response.heightmap || response;
    
    // Validate heightmap structure
    if (!heightmap.z || !Array.isArray(heightmap.z) || heightmap.z.length === 0) {
      throw new Error('Invalid heightmap structure');
    }
    
    return {
      width: heightmap.width || heightmap.z.length,
      height: heightmap.height || (Array.isArray(heightmap.z[0]) ? heightmap.z[0].length : 1),
      z: heightmap.z
    };
  } catch (error) {
    console.error('Error fetching heightmap:', error);
    throw error;
  }
}

/**
 * Check if heightmap is available
 * @returns {Promise<boolean>}
 */
export async function checkHeightmapAvailable() {
  try {
    const response = await eel.api_get_heightmap()();
    return !!(response && response.heightmap && response.heightmap.z);
  } catch {
    return false;
  }
}