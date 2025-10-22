import { loadDeps } from './deps.js';
let THREE, OrbitControls, SVGRenderer, OBJExporter;
export async function initDeps(){
	const mod = await loadDeps();
	THREE = mod.THREE;
	OrbitControls = mod.OrbitControls;
	SVGRenderer = mod.SVGRenderer;
	OBJExporter = mod.OBJExporter;
	return mod.cdn;
}

let _heightmap = { width: 0, height: 0, z: [] };
let _terrainMesh = null;
let _terrainWire = null;
let _visMode = 'mesh'; // 'mesh' | 'contours'
let _renderer, _scene, _camera, _controls;
let _rootEl;
const _pois = [];
const _roads = [];
const _areas = [];
let _animHandle = null;
let _onResizeBound = null;

export function initScene(root){
	_rootEl = root;
	const scene = new THREE.Scene();
	scene.background = new THREE.Color(0x000000);
	const camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 0.1, 2000);
	camera.position.set(80, 120, 120);

	const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
	renderer.setSize(window.innerWidth, window.innerHeight);
	root.appendChild(renderer.domElement);

	const controls = new OrbitControls(camera, renderer.domElement);
	controls.enableDamping = true;

	// Lights
	const dir = new THREE.DirectionalLight(0xffffff, 0.8);
	dir.position.set(1,2,1);
	scene.add(dir);
	scene.add(new THREE.AmbientLight(0xffffff, 0.2));

	// Grid helper
	const grid = new THREE.GridHelper(200, 20, 0x00ffff, 0x003333);
	grid.position.y = 0;
	scene.add(grid);

	function onResize(){
		camera.aspect = window.innerWidth/window.innerHeight;
		camera.updateProjectionMatrix();
		renderer.setSize(window.innerWidth, window.innerHeight);
	}
	_onResizeBound = onResize;
	window.addEventListener('resize', _onResizeBound);

	_renderer = renderer; _scene = scene; _camera = camera; _controls = controls;

	(function animate(){
		_animHandle = requestAnimationFrame(animate);
		controls.update();
		renderer.render(scene, camera);
	})();

	return { scene, camera, renderer, controls };
}

export async function loadTerrainMesh(scene, hm){
	_heightmap = hm;
	if (_terrainMesh) { scene.remove(_terrainMesh); _terrainMesh.geometry.dispose(); }
	if (_terrainWire) { _terrainMesh.remove(_terrainWire); _terrainWire.geometry?.dispose(); _terrainWire.material?.dispose(); _terrainWire = null; }
	const { geometry, mesh } = buildTerrainGeometry(hm);
	_terrainMesh = mesh;
	scene.add(mesh);
	applyVisualizationMode();
}

function buildTerrainGeometry(hm){
	const { width: W, height: H, z } = hm;
	const geom = new THREE.PlaneGeometry(W-1, H-1, W-1, H-1);
	// PlaneGeometry is X right, Y up, Z toward camera; rotate to XZ-plane
	geom.rotateX(-Math.PI/2);
	// Assign heights from z (assumes z is a flat array or nested)
	const isNested = Array.isArray(z[0]);
	const verts = geom.attributes.position;
	for (let j = 0; j < H; j++){
		for (let i = 0; i < W; i++){
			const idx = j*W + i;
			const h = isNested ? (z[i]?.[j] ?? 0) : (z[idx] ?? 0);
			// Find corresponding vertex index in PlaneGeometry grid
			const vi = j*W + i; // after segments = W-1/H-1 this aligns 1:1
			verts.setY(vi, h);
		}
	}
	verts.needsUpdate = true;
	geom.computeVertexNormals();

	const mat = new THREE.MeshStandardMaterial({ color: 0x444444, wireframe: false, metalness: 0.1, roughness: 0.9 });
	const mesh = new THREE.Mesh(geom, mat);
	mesh.position.set(0, 0, 0);
	mesh.receiveShadow = false; mesh.castShadow = false;

	// Wire/contour helper
	const wireMat = new THREE.MeshBasicMaterial({ color: 0xff7825, wireframe: true, transparent: true, opacity: 0.2 });
	_terrainWire = new THREE.Mesh(geom.clone(), wireMat);
	mesh.add(_terrainWire);

	return { geometry: geom, mesh };
}

export function disposeScene(ctx){
	try {
		if (_animHandle) { cancelAnimationFrame(_animHandle); _animHandle = null; }
		if (_onResizeBound) { window.removeEventListener('resize', _onResizeBound); _onResizeBound = null; }
		// Dispose geometries/materials
		const disposeObj = (obj) => {
			obj.traverse((child) => {
				if (child.geometry) { try { child.geometry.dispose(); } catch {} }
				if (child.material) {
					const mats = Array.isArray(child.material) ? child.material : [child.material];
					mats.forEach(m => { try { if (m.map) m.map.dispose(); m.dispose(); } catch {} });
				}
			});
		};
		if (_terrainMesh) disposeObj(_terrainMesh);
		_roads.forEach(r => disposeObj(r));
		_areas.forEach(a => disposeObj(a.group ?? a));
		_pois.forEach(p => disposeObj(p.object));
		if (_renderer) { try { _renderer.dispose(); } catch {} }
		if (_rootEl && _renderer && _renderer.domElement && _rootEl.contains(_renderer.domElement)) {
			try { _rootEl.removeChild(_renderer.domElement); } catch {}
		}
	} catch (e) {
		console.warn('disposeScene warning:', e);
	}
}

export function addPoi(scene, { name, type, x, z, yaw=0 }){
	// Clamp within heightmap bounds and snap to ground
	const W=_heightmap.width, H=_heightmap.height;
	const cx = Math.max(0, Math.min(W-1, x));
	const cz = Math.max(0, Math.min(H-1, z));
	const y = sampleHeightAt(cx, cz);
	let obj;
	if (type === 'building'){
		const g = new THREE.BoxGeometry(3, 8, 3);
		const m = new THREE.MeshStandardMaterial({ color: 0x99ccff });
		obj = new THREE.Mesh(g, m);
		obj.position.set(cx, y + 4, cz);
	} else if (type === 'vehicle'){
		const g = new THREE.SphereGeometry(1.8, 12, 12);
		const m = new THREE.MeshStandardMaterial({ color: 0xffee88 });
		obj = new THREE.Mesh(g, m);
		obj.position.set(cx, y + 1.8, cz);
	} else {
		// air: tetrahedron
		const g = new THREE.TetrahedronGeometry(2.2);
		const m = new THREE.MeshStandardMaterial({ color: 0xff8888 });
		obj = new THREE.Mesh(g, m);
		obj.position.set(cx, y + 6, cz);
	}
	obj.rotation.y = THREE.MathUtils.degToRad(yaw || 0);

	// Label
	const label = makeLabelSprite(name);
	label.position.set(0, (type === 'building') ? 6.5 : 3.0, 0);
	obj.add(label);

	const poi = { name, type, x: cx, y, z: cz, yaw, object: obj, label, connector: null };
	// default connector
	poi.connector = drawConnectorLine(obj, label, { dashed: false });
	_pois.push(poi);
	_scene.add(obj);
	return poi;
}

function makeLabelSprite(text){
	const canvas = document.createElement('canvas');
	const ctx = canvas.getContext('2d');
	const font = 'bold 24px sans-serif';
	ctx.font = font;
	const metrics = ctx.measureText(text);
	const pad = 8;
	canvas.width = Math.ceil(metrics.width) + pad*2;
	canvas.height = 36 + pad*2;
	ctx.font = font;
	ctx.fillStyle = 'rgba(0,0,0,0.5)';
	ctx.fillRect(0,0,canvas.width,canvas.height);
	ctx.fillStyle = '#fff';
	ctx.textBaseline = 'middle';
	ctx.fillText(text, pad, canvas.height/2);
	const tex = new THREE.CanvasTexture(canvas);
	const mat = new THREE.SpriteMaterial({ map: tex, transparent: true });
	const spr = new THREE.Sprite(mat);
	const scale = 0.15; // scale down sprite
	spr.scale.set(canvas.width*scale, canvas.height*scale, 1);
	return spr;
}

export function getPoiList(){ return _pois.slice(); }

export function setVisualizationMode(mode){
	_visMode = (mode === 'contours') ? 'contours' : 'mesh';
	applyVisualizationMode();
}

function applyVisualizationMode(){
	if (!_terrainMesh) return;
	const isContours = _visMode === 'contours';
	if (_terrainMesh.material) {
		const mats = Array.isArray(_terrainMesh.material) ? _terrainMesh.material : [_terrainMesh.material];
		mats.forEach(m => { m.wireframe = false; m.visible = !isContours; });
	}
	if (_terrainWire) {
		_terrainWire.visible = isContours;
	}
}

export function buildRoadBetween(idxA, idxB, style){
	const A = _pois[idxA];
	const B = _pois[idxB];
	if (!A || !B) return;
	if (A.type !== 'building' || B.type !== 'building'){
		console.warn('Las carreteras solo pueden generarse entre POIs de tipo edificio');
		return;
	}
	const path = findEffortPath([A.x, A.z], [B.x, B.z]);
	const pts3 = path.map(([x,z]) => new THREE.Vector3(x, sampleHeightAt(x,z) + 0.3, z));
	const geo = new THREE.BufferGeometry().setFromPoints(pts3);
	const mat = new THREE.LineBasicMaterial({ color: new THREE.Color(style.color || '#ff7825'), linewidth: 1, transparent: true, opacity: style.opacity ?? 0.9 });
	const line = new THREE.Line(geo, mat);
	_scene.add(line);
	_roads.push(line);
}

function findEffortPath(start, end){
	// Simple A* on a coarse grid with slope penalty and small chance of bridge
	const W = _heightmap.width, H = _heightmap.height;
	const sx = Math.max(0, Math.min(W-1, Math.round(start[0])));
	const sz = Math.max(0, Math.min(H-1, Math.round(start[1])));
	const ex = Math.max(0, Math.min(W-1, Math.round(end[0])));
	const ez = Math.max(0, Math.min(H-1, Math.round(end[1])));

	const key = (x,z)=>`${x},${z}`;
	const h = (x,z)=>Math.hypot(x-ex, z-ez);
	const gScore = new Map();
	const fScore = new Map();
	const came = new Map();
	const open = new Set();
	gScore.set(key(sx,sz), 0);
	fScore.set(key(sx,sz), h(sx,sz));
	open.add(key(sx,sz));

	function neighbors(x,z){
		const dirs = [[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]];
		const out=[]; for (const [dx,dz] of dirs){ const nx=x+dx, nz=z+dz; if(nx>=0&&nx<W&&nz>=0&&nz<H) out.push([nx,nz]); }
		return out;
	}
	function height(x,z){
		const nested = Array.isArray(_heightmap.z[0]);
		return nested ? (_heightmap.z[x]?.[z] ?? 0) : (_heightmap.z[z*W + x] ?? 0);
	}

	while (open.size){
		// get lowest fScore
		let currentK = null, bestF=Infinity; for(const k of open){ const fs = fScore.get(k) ?? Infinity; if(fs<bestF){ bestF=fs; currentK=k; } }
		const [cx,cz] = currentK.split(',').map(Number);
		if (cx===ex && cz===ez){
			// reconstruct
			const path=[[cx,cz]]; let ck=currentK; while(came.has(ck)){ ck = came.get(ck); path.push(ck.split(',').map(Number)); }
			return path.reverse();
		}
		open.delete(currentK);
		for (const [nx,nz] of neighbors(cx,cz)){
			const dist = Math.hypot(nx-cx, nz-cz);
			const slope = Math.abs(height(nx,nz) - height(cx,cz)) / (dist||1);
			const bridge = Math.random()<0.03 ? 5.0 : 0.0; // small chance bridge effort
			const tentative = (gScore.get(currentK)??Infinity) + dist*1.0 + Math.pow(slope*6.0, 2.2) + bridge;
			const nk = key(nx,nz);
			if (tentative < (gScore.get(nk)??Infinity)){
				came.set(nk, currentK);
				gScore.set(nk, tentative);
				fScore.set(nk, tentative + h(nx,nz));
				open.add(nk);
			}
		}
	}
	return [[sx,sz],[ex,ez]]; // fallback straight line
}

function sampleHeightAt(x,z){
	// Bilinear sample on heightmap
	const W=_heightmap.width, H=_heightmap.height; if(W<2||H<2) return 0;
	const xi=Math.floor(x), zi=Math.floor(z); const xf=x-xi, zf=z-zi;
	function get(ix,iz){ const nested = Array.isArray(_heightmap.z[0]); return nested? (_heightmap.z[Math.max(0,Math.min(W-1,ix))]?.[Math.max(0,Math.min(H-1,iz))] ?? 0) : (_heightmap.z[Math.max(0,Math.min(H-1,iz))*W + Math.max(0,Math.min(W-1,ix))] ?? 0); }
	const h00 = get(xi,zi);
	const h10 = get(xi+1,zi);
	const h01 = get(xi,zi+1);
	const h11 = get(xi+1,zi+1);
	const hx0 = h00*(1-xf) + h10*xf;
	const hx1 = h01*(1-xf) + h11*xf;
	return hx0*(1-zf) + hx1*zf;
}

export function exportPNG(renderer){
	const url = renderer.domElement.toDataURL('image/png');
	const a = document.createElement('a');
	a.href = url; a.download = 'laboratorio3d.png'; a.click();
}

export function exportOBJ(scene){
	const exporter = new OBJExporter();
	const objText = exporter.parse(scene);
	const blob = new Blob([objText], { type: 'text/plain' });
	const a = document.createElement('a');
	a.href = URL.createObjectURL(blob);
	a.download = 'laboratorio3d.obj';
	a.click();
}

export function exportSVG(scene, renderer, root){
	// Render lines to SVG (terrain wire + roads)
	const svgRenderer = new SVGRenderer({ antialias: true });
	svgRenderer.setSize(root.clientWidth, root.clientHeight);
	svgRenderer.render(scene, _camera);
	const data = new XMLSerializer().serializeToString(svgRenderer.domElement);
	const blob = new Blob([data], { type: 'image/svg+xml' });
	const a = document.createElement('a');
	a.href = URL.createObjectURL(blob);
	a.download = 'laboratorio3d.svg';
	a.click();
}

export function applyLabelStyles({ background=true, backgroundColor='rgba(0,0,0,0.5)', bold=true, italic=false, connector='solid' }){
	for (const p of _pois){
		// rebuild label texture
		const text = p.name;
		const canvas = document.createElement('canvas');
		const ctx = canvas.getContext('2d');
		const font = `${bold?'bold ':''}${italic?'italic ':''}24px sans-serif`;
		ctx.font = font;
		const metrics = ctx.measureText(text);
		const pad = 8;
		canvas.width = Math.ceil(metrics.width) + pad*2;
		canvas.height = 36 + pad*2;
		ctx.font = font;
		if (background){
			ctx.fillStyle = backgroundColor || 'rgba(0,0,0,0.5)';
			ctx.fillRect(0,0,canvas.width,canvas.height);
		}
		ctx.fillStyle = '#fff';
		ctx.textBaseline = 'middle';
		ctx.fillText(text, pad, canvas.height/2);
		const tex = new THREE.CanvasTexture(canvas);
		p.label.material.map?.dispose();
		p.label.material.map = tex;
		p.label.material.needsUpdate = true;
		const scale = 0.15;
		p.label.scale.set(canvas.width*scale, canvas.height*scale, 1);

		// connector
		if (p.connector){ _scene.remove(p.connector); }
		p.connector = drawConnectorLine(p.object, p.label, { dashed: connector==='dashed' });
	}
}

function drawConnectorLine(baseObj, labelSprite, { dashed }){
	const p1 = new THREE.Vector3(); baseObj.getWorldPosition(p1);
	const p2 = new THREE.Vector3(); labelSprite.getWorldPosition(p2);
	const pts = [p1, p2];
	const geo = new THREE.BufferGeometry().setFromPoints(pts);
	let line;
	if (dashed){
		const mat = new THREE.LineDashedMaterial({ color: 0xffffff, dashSize: 2, gapSize: 1, transparent: true, opacity: 0.7 });
		line = new THREE.LineSegments(geo, mat);
		line.computeLineDistances();
	} else {
		const mat = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.7 });
		line = new THREE.Line(geo, mat);
	}
	_scene.add(line);
	return line;
}

export function addArea({ name='Área', shape='square', pattern='lines', x=20, z=20, size=10 }){
	// Draw on terrain as a set of small lines or points following height
	const group = new THREE.Group();
	const half = size/2;
	const minX = x - half, maxX = x + half, minZ = z - half, maxZ = z + half;
	const color = new THREE.Color('#00ffaa');
	if (shape==='circle'){
		const r = half;
		if (pattern==='lines'){
			for (let zz = -r; zz <= r; zz += 1.5){
				const len = Math.sqrt(r*r - zz*zz);
				const x0 = x - len, x1 = x + len; const pts = [];
				for (let xx = x0; xx <= x1; xx += 1.0){ pts.push(new THREE.Vector3(xx, sampleHeightAt(xx, z+zz)+0.1, z+zz)); }
				if (pts.length>=2){ const g = new THREE.BufferGeometry().setFromPoints(pts); const m = new THREE.LineBasicMaterial({ color, transparent:true, opacity:0.6 }); const l=new THREE.Line(g,m); group.add(l); }
			}
		} else {
			const dots = new THREE.Group();
			for (let ang=0; ang<Math.PI*2; ang+=0.12){ const xx = x + Math.cos(ang)*r*0.7; const zz = z + Math.sin(ang)*r*0.7; const y = sampleHeightAt(xx,zz)+0.1; const geo = new THREE.SphereGeometry(0.25, 6, 6); const mat = new THREE.MeshBasicMaterial({ color }); const dot = new THREE.Mesh(geo, mat); dot.position.set(xx,y,zz); dots.add(dot); }
			group.add(dots);
		}
	} else {
		if (pattern==='lines'){
			for (let zz=minZ; zz<=maxZ; zz+=1.5){
				const pts=[]; for(let xx=minX; xx<=maxX; xx+=1.0){ pts.push(new THREE.Vector3(xx, sampleHeightAt(xx, zz)+0.1, zz)); }
				if (pts.length>=2){ const g = new THREE.BufferGeometry().setFromPoints(pts); const m = new THREE.LineBasicMaterial({ color, transparent:true, opacity:0.6 }); const l=new THREE.Line(g,m); group.add(l); }
			}
		} else {
			for (let zz=minZ; zz<=maxZ; zz+=2){ for(let xx=minX; xx<=maxX; xx+=2){ const y=sampleHeightAt(xx,zz)+0.1; const geo=new THREE.SphereGeometry(0.25,6,6); const mat=new THREE.MeshBasicMaterial({ color }); const dot=new THREE.Mesh(geo,mat); dot.position.set(xx,y,zz); group.add(dot);} }
		}
	}
	_areas.push({ name, group });
	_scene.add(group);
	return group;
}

// POI removal events
window.addEventListener('remove-poi', (ev) => {
	const idx = ev?.detail?.index;
	if (typeof idx !== 'number' || idx < 0 || idx >= _pois.length) return;
	const [poi] = _pois.splice(idx, 1);
	try { if (poi.connector) _scene.remove(poi.connector); } catch {}
	try { _scene.remove(poi.object); } catch {}
});

window.addEventListener('clear-pois', () => {
	while (_pois.length) {
		const poi = _pois.pop();
		try { if (poi.connector) _scene.remove(poi.connector); } catch {}
		try { _scene.remove(poi.object); } catch {}
	}
});