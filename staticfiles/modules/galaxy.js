// Módulo: Simulação de Galáxia 3D (Three.js)
function renderGalaxyModule(container) {
  container.innerHTML = `
    <div class="card" style="text-align: center;">
      <div style="margin-bottom: 15px; display: flex; justify-content: center; gap: 15px; align-items: center; flex-wrap: wrap;">
        <label>Partículas: <input type="range" id="galaxy-count" min="5000" max="40000" step="2500" value="20000"></label>
        <label>Braços: <input type="range" id="galaxy-branches" min="2" max="8" value="4"></label>
        <label>Velocidade: <input type="range" id="galaxy-speed" min="1" max="10" value="3"></label>
      </div>
      <div id="galaxy-canvas-container" style="width: 100%; height: 500px; background: #030508; border-radius: 6px; overflow: hidden; position: relative;"></div>
    </div>
  `;

  if (typeof THREE === 'undefined') {
    const script = document.createElement('script');
    script.src = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js";
    script.onload = () => initGalaxyScene();
    document.head.appendChild(script);
  } else {
    initGalaxyScene();
  }
}

function initGalaxyScene() {
  const mountPoint = document.getElementById('galaxy-canvas-container');
  if (!mountPoint) return;

  const width = mountPoint.clientWidth;
  const height = mountPoint.clientHeight;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 100);
  camera.position.set(3, 3, 3);
  camera.lookAt(0, 0, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  mountPoint.appendChild(renderer.domElement);

  let count = 20000;
  let branches = 4;
  let speed = 0.003;
  let points = null;

  const generateGalaxy = () => {
    if (points !== null) {
      points.geometry.dispose();
      points.material.dispose();
      scene.remove(points);
    }

    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);

    const colorInside = new THREE.Color('#ff6000');
    const colorOutside = new THREE.Color('#1b3984');

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      const radius = Math.random() * 5;
      const branchAngle = ((i % branches) / branches) * Math.PI * 2;
      const spinAngle = radius * 1.5;

      const randomX = Math.pow(Math.random(), 3) * (Math.random() < 0.5 ? 1 : -1) * 0.3 * radius;
      const randomY = Math.pow(Math.random(), 3) * (Math.random() < 0.5 ? 1 : -1) * 0.3 * radius;
      const randomZ = Math.pow(Math.random(), 3) * (Math.random() < 0.5 ? 1 : -1) * 0.3 * radius;

      positions[i3] = Math.cos(branchAngle + spinAngle) * radius + randomX;
      positions[i3 + 1] = randomY;
      positions[i3 + 2] = Math.sin(branchAngle + spinAngle) * radius + randomZ;

      const mixedColor = colorInside.clone();
      mixedColor.lerp(colorOutside, radius / 5);

      colors[i3] = mixedColor.r;
      colors[i3 + 1] = mixedColor.g;
      colors[i3 + 2] = mixedColor.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.015,
      sizeAttenuation: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      vertexColors: true
    });

    points = new THREE.Points(geometry, material);
    scene.add(points);
  };

  generateGalaxy();

  document.getElementById('galaxy-count')?.addEventListener('input', (e) => {
    count = parseInt(e.target.value);
    generateGalaxy();
  });

  document.getElementById('galaxy-branches')?.addEventListener('input', (e) => {
    branches = parseInt(e.target.value);
    generateGalaxy();
  });

  document.getElementById('galaxy-speed')?.addEventListener('input', (e) => {
    speed = parseFloat(e.target.value) * 0.001;
  });

  function animate() {
    currentAnimationId = requestAnimationFrame(animate);
    if (points) {
      points.rotation.y += speed;
    }
    renderer.render(scene, camera);
  }

  animate();
}