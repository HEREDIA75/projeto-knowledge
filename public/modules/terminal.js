// Módulo: Terminal OSINT & Cyber Security CLI
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

  input?.addEventListener('keydown', (e) => {
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