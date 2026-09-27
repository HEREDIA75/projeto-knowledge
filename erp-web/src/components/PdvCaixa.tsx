import React, { useState, useEffect } from 'react';
import { dbLocal, type ProdutoLocal, type ItemVendaLocal } from '../db/offlineDb';
import { sincronizarVendasPendentes } from '../services/syncService';

export const PdvCaixa: React.FC = () => {
  const [codigoBarras, setCodigoBarras] = useState('');
  const [carrinho, setCarrinho] = useState<ItemVendaLocal[]>([]);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendentesCount, setPendentesCount] = useState(0);

  // Monitora status da rede e quantidade de vendas pendentes no IndexedDB
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    atualizarContadorPendentes();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const atualizarContadorPendentes = async () => {
    const qtd = await dbLocal.vendasOffline
      .where('status')
      .equals('PENDENTE_SYNC')
      .count();
    setPendentesCount(qtd);
  };

  // 1. Adiciona produto ao carrinho via leitura de código de barras
  const handleAdicionarProduto = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!codigoBarras.trim()) return;

    // Busca o produto no banco local
    const produto = await dbLocal.produtos
      .where('codigo_barras')
      .equals(codigoBarras)
      .first();

    if (produto) {
      setCarrinho(prev => {
        const itemExistente = prev.find(i => i.produto_id === produto.id);
        if (itemExistente) {
          return prev.map(i =>
            i.produto_id === produto.id
              ? { ...i, quantidade: i.quantidade + 1 }
              : i
          );
        }
        return [
          ...prev,
          {
            produto_id: produto.id,
            quantidade: 1,
            preco_unitario: produto.preco_venda
          }
        ];
      });
      setCodigoBarras('');
    } else {
      alert('Produto não encontrado no catálogo local!');
    }
  };

  // 2. Calcula o total do carrinho
  const valorTotal = carrinho.reduce(
    (acc, item) => acc + item.quantidade * item.preco_unitario,
    0
  );

  // 3. Finaliza a venda e salva no IndexedDB
  const handleFinalizarVenda = async () => {
    if (carrinho.length === 0) return;

    const novaVenda = {
      id: crypto.randomUUID(), // UUID gerado no navegador (Idempotência)
      data_venda: new Date().toISOString(),
      valor_total: valorTotal,
      tipo_emissao: isOnline ? '1' : '9', // '1' = Normal, '9' = Contingência
      status: 'PENDENTE_SYNC' as const,
      itens: carrinho
    };

    // Salva na fila do banco local
    await dbLocal.vendasOffline.add(novaVenda);
    setCarrinho([]);
    await atualizarContadorPendentes();

    // Tenta sincronizar imediatamente se estiver online
    if (isOnline) {
      await sincronizarVendasPendentes();
      await atualizarContadorPendentes();
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      {/* Indicator Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h2>Frente de Caixa (PDV)</h2>
        <div>
          <span style={{ color: isOnline ? 'green' : 'red', fontWeight: 'bold', marginRight: '15px' }}>
            ● {isOnline ? 'ONLINE' : 'OFFLINE (Contingência)'}
          </span>
          <span>Vendas Pendentes: <strong>{pendentesCount}</strong></span>
        </div>
      </div>

      {/* Input Código de Barras */}
      <form onSubmit={handleAdicionarProduto} style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Bipe o código de barras aqui..."
          value={codigoBarras}
          onChange={e => setCodigoBarras(e.target.value)}
          style={{ width: '100%', padding: '12px', fontSize: '18px' }}
          autoFocus
        />
      </form>

      {/* Lista do Carrinho */}
      <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '20px' }}>
        <thead>
          <tr style={{ background: '#f4f4f4', textAlign: 'left' }}>
            <th style={{ padding: '8px' }}>Produto ID</th>
            <th style={{ padding: '8px' }}>Qtd</th>
            <th style={{ padding: '8px' }}>Preço Un.</th>
            <th style={{ padding: '8px' }}>Subtotal</th>
          </tr>
        </thead>
        <tbody>
          {carrinho.map((item, idx) => (
            <tr key={idx} style={{ borderBottom: '1px solid #ddd' }}>
              <td style={{ padding: '8px' }}>{item.produto_id}</td>
              <td style={{ padding: '8px' }}>{item.quantidade}</td>
              <td style={{ padding: '8px' }}>R$ {item.preco_unitario.toFixed(2)}</td>
              <td style={{ padding: '8px' }}>R$ {(item.quantidade * item.preco_unitario).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Total e Ações */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3>Total: R$ {valorTotal.toFixed(2)}</h3>
        <button
          onClick={handleFinalizarVenda}
          disabled={carrinho.length === 0}
          style={{
            padding: '12px 24px',
            fontSize: '18px',
            backgroundColor: '#28a745',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Concluir Venda (F10)
        </button>
      </div>
    </div>
  );
};