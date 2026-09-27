import { dbLocal, type ProdutoLocal } from '../db/offlineDb';

export async function carregarCatalogoProdutos(): Promise<ProdutoLocal[]> {
  if (!navigator.onLine) {
    console.log('[Catalogo] Dispositivo offline. Carregando dados locais...');
    return await dbLocal.produtos.toArray();
  }

  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('http://127.0.0.1:8000/api/v1/produtos', {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Servidor retornou status HTTP ${response.status}`);
    }

    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      throw new Error('A resposta do backend não é um JSON válido.');
    }

    const produtos: ProdutoLocal[] = await response.json();

    // Atualiza a tabela local de forma atômica
    await dbLocal.transaction('rw', dbLocal.produtos, async () => {
      await dbLocal.produtos.clear();
      await dbLocal.produtos.bulkAdd(produtos);
    });

    console.log('[Catalogo] Catálogo local de produtos atualizado!');
    return produtos;
  } catch (error) {
    console.error('[Catalogo] Erro ao carregar catálogo do backend, usando dados locais:', error);
    return await dbLocal.produtos.toArray();
  }
}