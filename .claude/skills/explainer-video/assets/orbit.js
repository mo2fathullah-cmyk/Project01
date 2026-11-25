// Orbit reveal: a three.js camera that starts close on a detail and pulls back while orbiting
// (default 270 deg) to show the whole subject. Deterministic: call Orbit.render(t) from seek().
// Needs ../shared/three.min.js loaded first. Flat, unlit-looking style that matches the 2D episodes.
//
//   Orbit.mount('#orbit', {
//     t0: 30, t1: 36,                         // base-timeline seconds of the move
//     from: {r: 3, theta: -30, phi: 15},      // close-up: distance, azimuth deg, elevation deg
//     to:   {r: 14, theta: 240, phi: 28},     // wide: theta - from.theta = orbit angle
//     target: [0, 1, 0], focusFrom: [0.6, 2.2, 0.3],  // look-at point moves from detail to centre
//     build: (THREE, scene, k) => { scene.add(k.box(2, 2, 2, '#E9E0CC', 0, 1, 0)); }
//   });
//   Orbit.render(t)   // inside window.seek
(function () {
  const C = {cream: '#E9E0CC', teal: '#2E7D6B', sky: '#3FA9E0', orange: '#E07B39', ink: '#0B1F35',
             steel: '#9FB3C8', dark: '#13314F', gold: '#F2C14E', green: '#4ADE80'};
  const ease = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  const S = [];
  function kit(THREE) {
    const mat = c => new THREE.MeshLambertMaterial({color: C[c] || c});
    const edge = (m, c = '#0B1F35') => { const e = new THREE.LineSegments(new THREE.EdgesGeometry(m.geometry),
      new THREE.LineBasicMaterial({color: c, transparent: true, opacity: .35})); m.add(e); return m; };
    return {
      C, mat,
      box: (w, h, d, c, x = 0, y = 0, z = 0) => { const m = edge(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat(c))); m.position.set(x, y, z); return m; },
      cyl: (r, h, c, x = 0, y = 0, z = 0, rx = 0, rz = 0) => { const m = edge(new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, 32), mat(c))); m.position.set(x, y, z); m.rotation.set(rx, 0, rz); return m; },
      label: (text, x, y, z, bg = '#3FA9E0') => {           // billboard pill label
        const cv = document.createElement('canvas'); cv.width = 512; cv.height = 128; const g = cv.getContext('2d');
        g.fillStyle = bg; g.beginPath(); g.roundRect(4, 14, 504, 100, 50); g.fill();
        g.fillStyle = '#fff'; g.font = '800 54px Inter'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(text, 256, 66);
        const sp = new THREE.Sprite(new THREE.SpriteMaterial({map: new THREE.CanvasTexture(cv), transparent: true, depthTest: false, sizeAttenuation: false}));
        sp.scale.set(.22, .055, 1); sp.position.set(x, y, z); sp.renderOrder = 10; return sp;
      }
    };
  }
  window.Orbit = {
    mount(sel, o) {
      const el = document.querySelector(sel), W = el.clientWidth, H = el.clientHeight;
      const r = new THREE.WebGLRenderer({antialias: true, alpha: true, preserveDrawingBuffer: true});
      r.setPixelRatio(window.devicePixelRatio); r.setSize(W, H); el.appendChild(r.domElement);
      const scene = new THREE.Scene();
      scene.add(new THREE.HemisphereLight(0xffffff, 0x6a7f99, 1.5));
      const d = new THREE.DirectionalLight(0xffffff, .45); d.position.set(5, 10, 7); scene.add(d);
      const cam = new THREE.PerspectiveCamera(o.fov || 35, W / H, .05, 200);
      const k = kit(THREE); o.labels = [];
      o.build(THREE, scene, k);
      S.push({r, scene, cam, o});
      this.render(0);
    },
    render(t) {
      for (const {r, scene, cam, o} of S) {
        const p = ease(Math.max(0, Math.min(1, (t - o.t0) / (o.t1 - o.t0))));
        const L = (a, b) => a + (b - a) * p, rad = Math.PI / 180;
        const R = L(o.from.r, o.to.r), th = L(o.from.theta, o.to.theta) * rad, ph = L(o.from.phi, o.to.phi) * rad;
        const tg = o.target || [0, 0, 0], ff = o.focusFrom || tg;
        const T = [L(ff[0], tg[0]), L(ff[1], tg[1]), L(ff[2], tg[2])];
        cam.position.set(T[0] + R * Math.cos(ph) * Math.sin(th), T[1] + R * Math.sin(ph), T[2] + R * Math.cos(ph) * Math.cos(th));
        cam.lookAt(T[0], T[1], T[2]);
        if (o.onFrame) o.onFrame(t, p, scene);
        r.render(scene, cam);
      }
    }
  };
})();
