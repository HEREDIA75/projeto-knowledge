// Módulo: Visualizador de Algoritmos (Insertion Sort & Big-O)
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