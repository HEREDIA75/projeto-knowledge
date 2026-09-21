// Módulo: Formulário Interativo de Auth & Animação
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

  inputEmail?.addEventListener('focus', () => {
    avatar.textContent = '👀';
    avatar.style.transform = 'scale(1.1) rotate(-5deg)';
    avatar.style.borderColor = '#58a6ff';
  });

  inputEmail?.addEventListener('blur', () => {
    avatar.textContent = '🤖';
    avatar.style.transform = 'scale(1) rotate(0deg)';
  });

  inputPass?.addEventListener('focus', () => {
    avatar.textContent = '🙈';
    avatar.style.transform = 'scale(1.05)';
    avatar.style.borderColor = '#ff9e64';
  });

  inputPass?.addEventListener('blur', () => {
    avatar.textContent = '🤖';
    avatar.style.borderColor = '#58a6ff';
  });

  form?.addEventListener('submit', (e) => {
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