/**
 * Laboratorio 3D Configuration
 * Centralized configuration for easy testing and iteration
 */

export const config = {
  // Scene settings
  scene: {
    backgroundColor: 0x000000,
    cameraFOV: 55,
    cameraNear: 0.1,
    cameraFar: 2000,
    cameraPosition: { x: 80, y: 120, z: 120 }
  },

  // Lighting
  lighting: {
    directional: {
      color: 0xffffff,
      intensity: 0.8,
      position: { x: 1, y: 2, z: 1 }
    },
    ambient: {
      color: 0xffffff,
      intensity: 0.2
    }
  },

  // Grid helper
  grid: {
    size: 200,
    divisions: 20,
    colorCenterLine: 0x00ffff,
    colorGrid: 0x003333
  },

  // Terrain material
  terrain: {
    color: 0x444444,
    metalness: 0.1,
    roughness: 0.9,
    wireframeColor: 0xff7825,
    wireframeOpacity: 0.2
  },

  // POI defaults
  poi: {
    building: {
      width: 3,
      height: 8,
      depth: 3,
      color: 0x99ccff,
      labelOffset: 6.5
    },
    vehicle: {
      radius: 1.8,
      color: 0xffee88,
      labelOffset: 3.0
    },
    air: {
      radius: 2.2,
      color: 0xff8888,
      labelOffset: 3.0,
      heightOffset: 6
    }
  },

  // Label settings
  label: {
    font: '24px sans-serif',
    padding: 8,
    backgroundColor: 'rgba(0,0,0,0.5)',
    textColor: '#fff',
    scale: 0.15
  },

  // Road generation
  road: {
    heightOffset: 0.3,
    defaultColor: '#ff7825',
    defaultWidth: 2,
    defaultOpacity: 0.9,
    bridgeProbability: 0.03,
    slopePenaltyExponent: 2.2,
    slopePenaltyMultiplier: 6.0
  },

  // Area patterns
  area: {
    defaultColor: '#00ffaa',
    lineSpacing: 1.5,
    pointSpacing: 2.0,
    opacity: 0.6,
    heightOffset: 0.1
  },

  // Export settings
  export: {
    png: {
      format: 'image/png',
      filename: 'laboratorio3d.png'
    },
    obj: {
      filename: 'laboratorio3d.obj'
    },
    svg: {
      filename: 'laboratorio3d.svg'
    }
  },

  // UI feedback
  ui: {
    loaderDelay: 100,
    toastDuration: 3000,
    toastDurationError: 5000,
    toastDurationSuccess: 2000,
    exitDelay: 100,
    exitFallbackDelay: 500
  }
};

/**
 * Get nested config value safely
 */
export const getConfig = (path, defaultValue = null) => {
  return path.split('.').reduce((obj, key) => obj?.[key], config) ?? defaultValue;
};
