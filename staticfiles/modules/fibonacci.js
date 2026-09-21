// Módulo: Esfera 3D & Geometria Sagrada (Fibonacci Sphere)
function renderFibonacciModule(container) {
  container.innerHTML = `
    <div class="card" style="text-align: center;">
      <div style="margin-bottom: 15px; display: flex; justify-content: center; gap: 15px; align-items: center; flex-wrap: wrap;">
        <label>Pontos (N): <input type="range" id="points-slider" min="300" max="3000" value="1100"> <span id="points-val">1100</span></label>
        <label>Velocidade: <input type="range" id="speed-slider" min="1" max="10" value="3"></label>
      </div>
      <div id="canvas-3d-container" style="width: 100%; height: 500px; background: #05070a; border-radius: 6px; overflow: hidden; position: relative;"></div>
    </div>
  `;

  if (typeof THREE === 'undefined') {
    const script = document.createElement('script');
    script.src = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js";
    script.onload = () => initFibonacciScene();
    document.head.appendChild(script);
  } else {
    initFibonacciScene();
  }
}

function initFibonacciScene() {
  const mountPoint = document.getElementById('canvas-3d-container');
  if (!mountPoint) return;

  const width = mountPoint.clientWidth;
  const height = mountPoint.clientHeight;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
  camera.position.z = 2.5;

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  mountPoint.appendChild(renderer.domElement);

  let numPoints = 1100;
  let speed = 0.03;

  document.getElementById('points-slider')?.addEventListener('input', (e) => {
    numPoints = parseInt(e.target.value);
    document.getElementById('points-val').textContent = numPoints;
    createSphereGeometry();
  });

  document.getElementById('speed-slider')?.addEventListener('input', (e) => {
    speed = parseFloat(e.target.value) * 0.01;
  });

  let pointCloud;
  const phi = Math.PI * (3 - Math.sqrt(5));

  function createSphereGeometry() {
    if (pointCloud) scene.remove(pointCloud);

    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(numPoints * 3);
    const colors = new Float32Array(numPoints * 3);

    const baseColor = new THREE.Color('#58a6ff');

    for (let i = 0; i < numPoints; i++) {
      const y = 1 - (i / (numPoints - 1)) * 2;
      const radius = Math.sqrt(1 - y * y);
      const theta = phi * i;

      positions[i * 3] = Math.cos(theta) * radius;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = Math.sin(theta) * radius;

      colors[i * 3] = baseColor.r;
      colors[i * 3 + 1] = baseColor.g;
      colors[i * 3 + 2] = baseColor.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.025,
      vertexColors: true,
      transparent: true,
      opacity: 0.85
    });

    pointCloud = new THREE.Points(geometry, material);
    scene.add(pointCloud);
  }

  createSphereGeometry();

  let clock = 0;
  function animate() {
    currentAnimationId = requestAnimationFrame(animate);
    clock += speed;

    if (pointCloud) {
      pointCloud.rotation.y += 0.005;
      const colors = pointCloud.geometry.attributes.color.array;
      const positions = pointCloud.geometry.attributes.position.array;

      for (let i = 0; i < numPoints; i++) {
        const y = positions[i * 3 + 1];
        const wave = Math.sin(clock * 3 + y * 4);
        
        if (wave > 0.7) {
          colors[i * 3] = 0.0;
          colors[i * 3 + 1] = 1.0;
          colors[i * 3 + 2] = 0.4;
        } else {
          colors[i * 3] = 0.34;
          colors[i * 3 + 1] = 0.65;
          colors[i * 3 + 2] = 1.0;
        }
      }
      pointCloud.geometry.attributes.color.needsUpdate = true;
    }

    renderer.render(scene, camera);
  }

  animate();
}