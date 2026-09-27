import { dbLocal } from '../db/offlineDb';

export async function sincronizarVendasPendentes(): Promise<void> {
  if (!navigator.onLine) {
    console.log('[SyncWorker] Dispositivo off-line. Sincronização adiada.');
    return;
  }

  const pendentes = await dbLocal.vendasOffline
    .where('status')
    .equals('PENDENTE_SYNC')
    .toArray();

  if (pendentes.length === 0) {
    console.log('[SyncWorker] Nenhuma venda pendente para sincronizar.');
    return;
  }

  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/v1/vendas/sincronizar', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(pendentes)
    });

    if (!response.ok) {
      throw new Error(`Falha na sincronização. Status HTTP: ${response.status}`);
    }

    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      throw new Error('Resposta inválida do servidor ao sincronizar vendas.');
    }

    const resultado = await response.json();

    if (resultado.processados && Array.isArray(resultado.processados)) {
      for (const item of resultado.processados) {
        if (item.status === 'SUCESSO' || item.status === 'JA_EXISTIA') {
          await dbLocal.vendasOffline.update(item.id, { status: 'SYNCED' });
        }
      }
      console.log(`[SyncWorker] ${resultado.processados.length} vendas sincronizadas com sucesso!`);
    }
  } catch (error) {
    console.error('[SyncWorker] Falha ao conectar com o servidor central:', error);
  }
}

// Escuta a reconexão à internet para disparar a sincronização
window.addEventListener('online', () => {
  console.log('[Network] Conexão reestabelecida. Disparando sync...');
  sincronizarVendasPendentes();
});