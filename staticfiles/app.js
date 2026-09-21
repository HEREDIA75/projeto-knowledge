// =============================================================
// CONFIGURAÇÕES E ESTADOS GLOBAIS
// =============================================================
const RENDER_API_URL = "https://projeto-knowledge.onrender.com/api";

let currentAnimationId = null;
let sortingInterval = null;
let matrixInterval = null;

// =============================================================
// INICIALIZAÇÃO
// =============================================================
document.addEventListener('DOMContentLoaded', () => {
  initFirebaseCheck();
  checkRenderHealth();
  switchTab('fibonacci');
});

function initFirebaseCheck() {
  const fbStatus = document.getElementById('firebase-status');
  if (!fbStatus) return;

  try {
    if (typeof firebase !== 'undefined' && firebase.app()) {
      fbStatus.innerHTML = '<span class="dot" style="background:#00ff66"></span> Firebase: OK';
    } else {
      throw new Error();
    }
  } catch (e) {
    fbStatus.innerHTML = '<span class="dot" style="background:#ff7b72"></span> Firebase: Offline';
  }
}

async function checkRenderHealth() {
  const renderStatus = document.getElementById('render-status');
  if (!renderStatus) return;

  try {
    const res = await fetch(`${RENDER_API_URL}/healthcheck`);
    if (res.ok) {
      renderStatus.innerHTML = '<span class="dot" style="background:#00ff66"></span> Render API: OK';
    } else {
      throw new Error();
    }
  } catch (e) {
    renderStatus.innerHTML = '<span class="dot" style="background:#ff7b72"></span> Render API: Offline';
  }
}

// =============================================================
// ROTEAMENTO & GERENCIAMENTO DE CICLO DE VIDA
// =============================================================
function clearActiveAnimations() {
  if (currentAnimationId) {
    cancelAnimationFrame(currentAnimationId);
    currentAnimationId = null;
  }
  if (sortingInterval) {
    clearInterval(sortingInterval);
    sortingInterval = null;
  }
  if (matrixInterval) {
    clearInterval(matrixInterval);
    matrixInterval = null;
  }
}

function switchTab(tabName) {
  clearActiveAnimations();

  const title = document.getElementById('tab-title');
  const container = document.getElementById('view-container');
  if (!container || !title) return;

  document.querySelectorAll('.menu-item').forEach(btn => btn.classList.remove('active'));
  const currentBtn = document.querySelector(`[onclick="switchTab('${tabName}')"]`);
  if (currentBtn) currentBtn.classList.add('active');

  switch (tabName) {
    case 'fibonacci':
      title.textContent = "Esfera 3D & Geometria Sagrada (Fibonacci Sphere)";
      renderFibonacciModule(container);
      break;
    case 'galaxy':
      title.textContent = "Simulação Espacial: Galáxia 3D (Three.js)";
      renderGalaxyModule(container);
      break;
    case 'sorting':
      title.textContent = "Visualizador de Algoritmos (Insertion Sort & Big-O)";
      renderSortingModule(container);
      break;
    case 'terminal':
      title.textContent = "Terminal OSINT / Cyber Security CLI";
      renderTerminalModule(container);
      break;
    case 'login_anim':
      title.textContent = "Componente UI: Autenticação Dinâmica";
      renderLoginAnimModule(container);
      break;
    case 'courses':
      title.textContent = "Cursos & Módulos Cadastrados";
      loadCourses(container);
      break;
    default:
      container.innerHTML = '<div class="card"><p>Módulo não encontrado.</p></div>';
  }
}

// =============================================================
// MÓDULO: GALÁXIA 3D
// =============================================================
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

// =============================================================
// MÓDULO: LOGIN INTERATIVO
// =============================================================
function renderLoginAnimModule(container) {
  container.innerHTML = `
    <div style="max-width: 480px; margin: 0 auto;" class="card">
      <div style="text-align: center; margin-bottom: 20px;">
        <div id="avatar-box" style="width: 90px; height: 90px; margin: 0 auto 10px; background: #1a2332; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; transition: transform 0.3s ease, border-color 0.3s ease; border: 2px solid var(--accent-blue);">
          🤖
        </div>
        <h3 id="form-title" style="color: var(--neon-green); margin-bottom: 5px;">Acesso ao Sistema</h3>
        <p style="color: var(--text-dim); font-size: 0.85rem;">Insira suas credenciais corporativas</p>
      </div>

      <form id="interactive-form" onsubmit="return false;" style="display: flex; flex-direction: column; gap: 15px;">
        <div>
          <label style="display: block; font-size: 0.85rem; margin-bottom: 5px; color: var(--text-main);">E-mail do Usuário</label>
          <input type="email" id="input-email" required placeholder="dev@knowledge.io" style="width: 100%; padding: 10px; background: #05070a; border: 1px solid var(--border-color); color: #fff; border-radius: 4px; outline: none;">
        </div>

        <div>
          <label style="display: block; font-size: 0.85rem; margin-bottom: 5px; color: var(--text-main);">Chave de Acesso</label>
          <input type="password" id="input-pass" required placeholder="••••••••" style="width: 100%; padding: 10px; background: #05070a; border: 1px solid var(--border-color); color: #fff; border-radius: 4px; outline: none;">
        </div>

        <button type="submit" id="btn-login-submit" class="menu-item" style="margin-top: 10px; background: var(--accent-blue); color: #000; font-weight: bold; text-align: center; justify-content: center;">
          Autenticar
        </button>
      </form>

      <div id="auth-feedback" style="margin-top: 15px; padding: 10px; border-radius: 4px; display: none; text-align: center; font-size: 0.85rem;"></div>
    </div>
  `;

  initLoginInteractions();
}

function initLoginInteractions() {
  const avatar = document.getElementById('avatar-box');
  const inputEmail = document.getElementById('input-email');
  const inputPass = document.getElementById('input-pass');
  const form = document.getElementById('interactive-form');
  const feedback = document.getElementById('auth-feedback');

  if (!avatar || !inputEmail || !inputPass || !form) return;

  inputEmail.addEventListener('focus', () => {
    avatar.textContent = '👀';
    avatar.style.transform = 'scale(1.1) rotate(-5deg)';
    avatar.style.borderColor = '#58a6ff';
  });

  inputEmail.addEventListener('blur', () => {
    avatar.textContent = '🤖';
    avatar.style.transform = 'scale(1) rotate(0deg)';
  });

  inputPass.addEventListener('focus', () => {
    avatar.textContent = '🙈';
    avatar.style.transform = 'scale(1.05)';
    avatar.style.borderColor = '#ff9e64';
  });

  inputPass.addEventListener('blur', () => {
    avatar.textContent = '🤖';
    avatar.style.borderColor = '#58a6ff';
  });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    avatar.textContent = '⚡';
    avatar.style.transform = 'scale(1.2) rotate(360deg)';
    avatar.style.borderColor = '#00ff66';

    feedback.style.display = 'block';
    feedback.style.background = 'rgba(0, 255, 102, 0.1)';
    feedback.style.border = '1px solid #00ff66';
    feedback.style.color = '#00ff66';
    feedback.innerHTML = '✔ Autenticação realizada com sucesso!';

    setTimeout(() => {
      avatar.textContent = '😎';
    }, 600);
  });
}

// =============================================================
// MÓDULO: ESFERA DE FIBONACCI 3D
// =============================================================
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
  let pointCloud;
  const phi = Math.PI * (3 - Math.sqrt(5));

  document.getElementById('points-slider')?.addEventListener('input', (e) => {
    numPoints = parseInt(e.target.value);
    const label = document.getElementById('points-val');
    if (label) label.textContent = numPoints;
    createSphereGeometry();
  });

  document.getElementById('speed-slider')?.addEventListener('input', (e) => {
    speed = parseFloat(e.target.value) * 0.01;
  });

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

// =============================================================
// MÓDULO: INSERTION SORT
// =============================================================
function renderSortingModule(container) {
  container.innerHTML = `
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
        <div>
          <button id="btn-start" class="menu-item" style="display:inline-block; width:auto;">Iniciar Ordenação</button>
          <button id="btn-reset" class="menu-item" style="display:inline-block; width:auto;">Gerar Novo Array</button>
        </div>
        <div>
          <label>Tamanho: <input type="range" id="array-size" min="10" max="50" value="25"></label>
          <label style="margin-left: 15px;">Velocidade (ms): <input type="range" id="sort-speed" min="20" max="400" value="100"></label>
        </div>
      </div>

      <div id="bars-container" style="display: flex; align-items: flex-end; height: 260px; gap: 4px; background: #05070a; padding: 15px; border-radius: 6px;"></div>
    </div>

    <div class="card">
      <h3 style="color: var(--accent-blue); margin-bottom: 10px;">Complexidade Algorítmica (Big-O)</h3>
      <table style="width: 100%; text-align: left; border-collapse: collapse; font-size: 0.9rem;">
        <thead>
          <tr style="border-bottom: 1px solid var(--border-color); color: var(--neon-green);">
            <th style="padding: 8px;">Algoritmo</th>
            <th style="padding: 8px;">Melhor Caso</th>
            <th style="padding: 8px;">Caso Médio</th>
            <th style="padding: 8px;">Pior Caso</th>
            <th style="padding: 8px;">Espaço</th>
          </tr>
        </thead>
        <tbody>
          <tr style="border-bottom: 1px solid #1a2332;">
            <td style="padding: 8px; font-weight: bold; color: var(--text-main);">Insertion Sort</td>
            <td style="padding: 8px; color: #7ee787;">O(n)</td>
            <td style="padding: 8px; color: #ff9e64;">O(n²)</td>
            <td style="padding: 8px; color: #ff7b72;">O(n²)</td>
            <td style="padding: 8px;">O(1)</td>
          </tr>
        </tbody>
      </table>
    </div>
  `;

  initSortingLogic();
}

function initSortingLogic() {
  const container = document.getElementById('bars-container');
  const sizeInput = document.getElementById('array-size');
  const speedInput = document.getElementById('sort-speed');
  const btnStart = document.getElementById('btn-start');
  const btnReset = document.getElementById('btn-reset');

  if (!container || !sizeInput || !btnStart) return;

  let array = [];
  let isSorting = false;

  function generateArray() {
    if (isSorting) return;
    const count = parseInt(sizeInput.value);
    array = [];
    container.innerHTML = '';
    for (let i = 0; i < count; i++) {
      const val = Math.floor(Math.random() * 85) + 10;
      array.push(val);
      
      const bar = document.createElement('div');
      bar.className = 'sort-bar';
      bar.style.height = `${val}%`;
      bar.style.flex = '1';
      bar.style.background = '#58a6ff';
      bar.style.borderRadius = '2px 2px 0 0';
      bar.style.transition = 'background 0.1s ease';
      container.appendChild(bar);
    }
  }

  sizeInput.addEventListener('input', generateArray);
  btnReset.addEventListener('click', generateArray);

  btnStart.addEventListener('click', async () => {
    if (isSorting) return;
    isSorting = true;
    btnStart.disabled = true;
    btnReset.disabled = true;

    const bars = container.children;
    const delay = () => new Promise(resolve => setTimeout(resolve, 420 - parseInt(speedInput.value)));

    for (let i = 1; i < array.length; i++) {
      let key = array[i];
      let j = i - 1;

      bars[i].style.background = '#ff7b72';
      await delay();

      while (j >= 0 && array[j] > key) {
        bars[j].style.background = '#ff9e64';
        array[j + 1] = array[j];
        bars[j + 1].style.height = `${array[j]}%`;
        
        j--;
        await delay();

        for (let k = 0; k <= i; k++) {
          if (k !== j + 1) bars[k].style.background = '#58a6ff';
        }
      }

      array[j + 1] = key;
      bars[j + 1].style.height = `${key}%`;
      bars[i].style.background = '#58a6ff';
      bars[j + 1].style.background = '#00ff66';
      await delay();
    }

    for (let k = 0; k < bars.length; k++) {
      bars[k].style.background = '#00ff66';
    }

    isSorting = false;
    btnStart.disabled = false;
    btnReset.disabled = false;
  });

  generateArray();
}

// =============================================================
// MÓDULO: TERMINAL OSINT
// =============================================================
function renderTerminalModule(container) {
  container.innerHTML = `
    <div class="card" style="padding: 0; overflow: hidden; position: relative;">
      <canvas id="matrix-canvas" style="position: absolute; top:0; left:0; width:100%; height:100%; opacity: 0.15; pointer-events: none;"></canvas>
      <div style="background: #090d13; padding: 10px 15px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
        <span style="color: var(--neon-green); font-size: 0.85rem;">[OSINT CLI v2.4 - Security Operations]</span>
        <span style="color: var(--text-dim); font-size: 0.75rem;">Digite 'help' para listar comandos</span>
      </div>
      
      <div id="cli-output" style="height: 380px; padding: 15px; overflow-y: auto; font-family: 'Courier New', monospace; font-size: 0.9rem; color: #00ff66;">
        <div>System initialized... Type <span style="color: #7dcfff;">'help'</span> or <span style="color: #7dcfff;">'phoneintel 5511999999999'</span></div>
      </div>

      <div style="display: flex; border-top: 1px solid var(--border-color); background: #05070a;">
        <span style="padding: 10px 0 10px 15px; color: var(--neon-green); font-weight: bold;">root@knowledge:~#</span>
        <input type="text" id="cli-input" style="flex:1; background: transparent; border: none; outline: none; color: #c0caf5; padding: 10px; font-family: 'Courier New', monospace; font-size: 0.9rem;" placeholder="Insira o comando..." autofocus>
      </div>
    </div>
  `;

  initMatrixEffect();
  initCliLogic();
}

function initMatrixEffect() {
  const canvas = document.getElementById('matrix-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  canvas.width = canvas.parentElement.clientWidth;
  canvas.height = 430;

  const chars = "01010101ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%&*";
  const fontSize = 14;
  const columns = Math.floor(canvas.width / fontSize);
  const drops = Array(columns).fill(1);

  function draw() {
    ctx.fillStyle = "rgba(5, 7, 10, 0.05)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "#00ff66";
    ctx.font = `${fontSize}px monospace`;

    for (let i = 0; i < drops.length; i++) {
      const text = chars.charAt(Math.floor(Math.random() * chars.length));
      ctx.fillText(text, i * fontSize, drops[i] * fontSize);

      if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
        drops[i] = 0;
      }
      drops[i]++;
    }
  }

  matrixInterval = setInterval(draw, 33);
}

function initCliLogic() {
  const input = document.getElementById('cli-input');
  const output = document.getElementById('cli-output');
  if (!input || !output) return;

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const command = input.value.trim();
      if (!command) return;

      appendOutput(`root@knowledge:~# ${command}`, '#7dcfff');
      processCommand(command);
      input.value = '';
    }
  });

  function appendOutput(text, color = '#00ff66') {
    const line = document.createElement('div');
    line.style.color = color;
    line.style.marginTop = '4px';
    line.innerHTML = text;
    output.appendChild(line);
    output.scrollTop = output.scrollHeight;
  }

  function processCommand(cmd) {
    const parts = cmd.split(' ');
    const action = parts[0].toLowerCase();

    switch (action) {
      case 'help':
        appendOutput('Comandos disponíveis:', '#ff9e64');
        appendOutput(' - <b style="color:#7dcfff">help</b>: Exibe este menu');
        appendOutput(' - <b style="color:#7dcfff">clear</b>: Limpa o terminal');
        appendOutput(' - <b style="color:#7dcfff">phoneintel &lt;numero&gt;</b>: Simula varredura OSINT de número telefônico');
        appendOutput(' - <b style="color:#7dcfff">scan &lt;ip/domain&gt;</b>: Realiza varredura de portas');
        appendOutput(' - <b style="color:#7dcfff">status</b>: Verifica saúde dos serviços conectados');
        break;

      case 'clear':
        output.innerHTML = '';
        break;

      case 'status':
        appendOutput('[+] Firebase Hosting: OPERACIONAL', '#00ff66');
        appendOutput('[+] Render API Django: OPERACIONAL', '#00ff66');
        appendOutput('[+] Three.js Engine: CARREGADO', '#00ff66');
        break;

      case 'phoneintel':
        if (!parts[1]) {
          appendOutput('Uso correto: phoneintel <numero_telefone>', '#ff7b72');
          return;
        }
        appendOutput(`[i] Iniciando varredura OSINT para: ${parts[1]}...`, '#ff9e64');
        setTimeout(() => appendOutput(`[+] DDI: +${parts[1].substring(0,2)} (Brasil)`), 400);
        setTimeout(() => appendOutput(`[+] Região Detectada: São Paulo / Operadora Móvel`), 800);
        setTimeout(() => appendOutput(`[+] Vazamentos conhecidos (HIBP): 0 encontrados`), 1200);
        setTimeout(() => appendOutput(`[✔] Análise concluída com sucesso.`), 1600);
        break;

      case 'scan':
        const target = parts[1] || '127.0.0.1';
        appendOutput(`[i] Escaneando portas em ${target}...`, '#ff9e64');
        setTimeout(() => appendOutput(`Porta 80/tcp OPEN (HTTP)`), 300);
        setTimeout(() => appendOutput(`Porta 443/tcp OPEN (HTTPS)`), 600);
        setTimeout(() => appendOutput(`Porta 8000/tcp OPEN (Django API)`), 900);
        setTimeout(() => appendOutput(`[✔] Escaneamento finalizado.`), 1200);
        break;

      default:
        appendOutput(`Comando não reconhecido: '${cmd}'. Digite 'help'.`, '#ff7b72');
    }
  }
}

// =============================================================
// ROTA AUXILIAR: CURSOS
// =============================================================
async function loadCourses(container) {
  container.innerHTML = '<p style="color: var(--text-dim)">Buscando dados no Django...</p>';
  try {
    const res = await fetch(`${RENDER_API_URL}/courses`);
    const data = await res.json();
    
    if (!Array.isArray(data) || !data.length) {
      container.innerHTML = '<div class="card"><p>Nenhum curso cadastrado no banco de dados ainda.</p></div>';
      return;
    }

    container.innerHTML = data.map(item => `
      <div class="card" style="margin-bottom: 12px;">
        <h3 style="color: var(--accent-blue)">${item.title || item.name}</h3>
        <p style="margin-top: 8px;">${item.description || 'Sem descrição cadastrada.'}</p>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<div class="card"><p style="color: #ff7b72">Não foi possível carregar os cursos da API Render.</p></div>';
  }
}