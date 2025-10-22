/**
 * Utility functions for Laboratorio 3D
 * Helpers for testing, debugging, and common operations
 */

/**
 * Performance monitoring
 */
export class PerformanceMonitor {
  constructor() {
    this.metrics = {};
  }

  start(label) {
    this.metrics[label] = performance.now();
  }

  end(label) {
    if (this.metrics[label]) {
      const duration = performance.now() - this.metrics[label];
      delete this.metrics[label];
      return duration;
    }
    return null;
  }

  measure(label, fn) {
    this.start(label);
    const result = fn();
    const duration = this.end(label);
    console.log(`[Performance] ${label}: ${duration.toFixed(2)}ms`);
    return result;
  }

  async measureAsync(label, fn) {
    this.start(label);
    const result = await fn();
    const duration = this.end(label);
    console.log(`[Performance] ${label}: ${duration.toFixed(2)}ms`);
    return result;
  }
}

/**
 * Debug helpers
 */
export const debug = {
  enabled: false,

  log(...args) {
    if (this.enabled) {
      console.log('[Lab3D Debug]', ...args);
    }
  },

  warn(...args) {
    if (this.enabled) {
      console.warn('[Lab3D Debug]', ...args);
    }
  },

  error(...args) {
    console.error('[Lab3D Error]', ...args);
  },

  table(data) {
    if (this.enabled) {
      console.table(data);
    }
  }
};

/**
 * Validate heightmap structure
 */
export const validateHeightmap = (heightmap) => {
  const errors = [];

  if (!heightmap) {
    errors.push('Heightmap is null or undefined');
    return { valid: false, errors };
  }

  if (typeof heightmap.width !== 'number' || heightmap.width <= 0) {
    errors.push(`Invalid width: ${heightmap.width}`);
  }

  if (typeof heightmap.height !== 'number' || heightmap.height <= 0) {
    errors.push(`Invalid height: ${heightmap.height}`);
  }

  if (!Array.isArray(heightmap.z)) {
    errors.push('Heightmap z is not an array');
    return { valid: false, errors };
  }

  if (heightmap.z.length === 0) {
    errors.push('Heightmap z array is empty');
  }

  const isNested = Array.isArray(heightmap.z[0]);
  if (isNested) {
    const expectedLength = heightmap.height || heightmap.z[0].length;
    for (let i = 0; i < heightmap.z.length; i++) {
      if (!Array.isArray(heightmap.z[i])) {
        errors.push(`Row ${i} is not an array`);
      } else if (heightmap.z[i].length !== expectedLength) {
        errors.push(`Row ${i} has unexpected length: ${heightmap.z[i].length} (expected ${expectedLength})`);
      }
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    info: {
      width: heightmap.width,
      height: heightmap.height,
      dataPoints: isNested 
        ? heightmap.z.reduce((sum, row) => sum + (row?.length || 0), 0)
        : heightmap.z.length,
      isNested
    }
  };
};

/**
 * Clamp value between min and max
 */
export const clamp = (value, min, max) => {
  return Math.max(min, Math.min(max, value));
};

/**
 * Parse numeric input safely
 */
export const parseNumericInput = (value, defaultValue = 0, min = -Infinity, max = Infinity) => {
  const parsed = parseFloat(value);
  if (isNaN(parsed)) return defaultValue;
  return clamp(parsed, min, max);
};

/**
 * Format number for display
 */
export const formatNumber = (value, decimals = 2) => {
  return Number(value).toFixed(decimals);
};

/**
 * Generate random color hex
 */
export const randomColor = () => {
  return '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0');
};

/**
 * Validate color hex
 */
export const isValidHex = (hex) => {
  return /^#?[0-9A-F]{6}$/i.test(hex);
};

/**
 * Ensure color has # prefix
 */
export const normalizeColorHex = (hex) => {
  const cleaned = hex.toUpperCase().replace('#', '');
  return isValidHex(cleaned) ? `#${cleaned}` : '#FF7825';
};

/**
 * Safe element getter
 */
export const safeGetElement = (id, errorMessage = null) => {
  const element = document.getElementById(id);
  if (!element && errorMessage) {
    debug.warn(errorMessage || `Element with id "${id}" not found`);
  }
  return element;
};

/**
 * Create download link and trigger download
 */
export const downloadFile = (content, filename, mimeType = 'text/plain') => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};

/**
 * Test mode helpers
 */
export const testMode = {
  _enabled: false,

  enable() {
    this._enabled = true;
    debug.enabled = true;
    window.__lab3dTestMode = true;
    debug.log('Test mode enabled');
  },

  disable() {
    this._enabled = false;
    debug.enabled = false;
    window.__lab3dTestMode = false;
    debug.log('Test mode disabled');
  },

  isEnabled() {
    return this._enabled;
  }
};

// Enable test mode from URL parameter
if (window.location.search.includes('test=1')) {
  testMode.enable();
}
