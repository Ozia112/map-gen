// Dynamic loader for Three.js and helpers with CDN fallbacks
// Tries local vendor first, then unpkg, then jsDelivr. Cache the result for reuse.

let cached = null;

export async function loadDeps() {
  if (cached) return cached;
  const sources = [
    {
      three: '/vendor/three/0.157.0/build/three.module.js',
      orbit: '/vendor/three/0.157.0/examples/jsm/controls/OrbitControls.js',
      svg: '/vendor/three/0.157.0/examples/jsm/renderers/SVGRenderer.js',
      obj: '/vendor/three/0.157.0/examples/jsm/exporters/OBJExporter.js',
      name: 'local'
    },
    {
      three: 'https://unpkg.com/three@0.157.0/build/three.module.js',
      orbit: 'https://unpkg.com/three@0.157.0/examples/jsm/controls/OrbitControls.js',
      svg: 'https://unpkg.com/three@0.157.0/examples/jsm/renderers/SVGRenderer.js',
      obj: 'https://unpkg.com/three@0.157.0/examples/jsm/exporters/OBJExporter.js',
      name: 'unpkg'
    },
    {
      three: 'https://cdn.jsdelivr.net/npm/three@0.157.0/build/three.module.js',
      orbit: 'https://cdn.jsdelivr.net/npm/three@0.157.0/examples/jsm/controls/OrbitControls.js',
      svg: 'https://cdn.jsdelivr.net/npm/three@0.157.0/examples/jsm/renderers/SVGRenderer.js',
      obj: 'https://cdn.jsdelivr.net/npm/three@0.157.0/examples/jsm/exporters/OBJExporter.js',
      name: 'jsdelivr'
    }
  ];

  let lastErr;
  for (const s of sources) {
    try {
      const THREE = await import(s.three);
      const { OrbitControls } = await import(s.orbit);
      const { SVGRenderer } = await import(s.svg);
      const { OBJExporter } = await import(s.obj);
      cached = { THREE, OrbitControls, SVGRenderer, OBJExporter, cdn: s.name };
      return cached;
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr || new Error('No se pudieron cargar dependencias Three.js');
}
