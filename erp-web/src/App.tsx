import React, { useState, useEffect } from 'react'
import { solicitarRelatorio } from './services/api'
import { sincronizarVendasPendentes } from './services/syncService'
import { carregarCatalogoProdutos } from './services/catalogService'
import { PdvCaixa } from './components/PdvCaixa'
import './App.css'

type TabType = 'dashboard' | 'financeiro' | 'estoque' | 'vendas' | 'caixa'

export function App() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard')
  const [loading, setLoading] = useState<boolean>(false)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [statusMsg, setStatusMsg] = useState<string | null>(null)

  // Ciclo de Vida: Carga do catálogo e Polling de Sincronização Offline
  useEffect(() => {
    // 1. Atualiza o catálogo local IndexedDB ao inicializar
    carregarCatalogoProdutos()

    // 2. Polling automático a cada 30 segundos para enviar vendas pendentes ao Django
    const interval = setInterval(() => {
      sincronizarVendasPendentes()
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  const handleSolicitarRelatorio = async () => {
    setLoading(true)
    setStatusMsg(null)
    setTaskId(null)

    try {
      const data = await solicitarRelatorio()
      setTaskId(data.task_id)
      setStatusMsg(data.mensagem || 'Relatório enviado para a fila do Celery!')
    } catch (error: any) {
      console.error('Erro ao conectar com a API:', error)
      setStatusMsg('Falha de conexão com a API Django.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#0f172a', color: '#f8fafc', fontFamily: 'system-ui, sans-serif' }}>
      
      {/* Sidebar Local do ERP */}
      <aside style={{ width: '260px', backgroundColor: '#1e293b', borderRight: '1px solid #334155', padding: '24px 16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div style={{ marginBottom: '24px', paddingLeft: '8px' }}>
          <h2 style={{ fontSize: '20px', color: '#38bdf8', margin: 0, fontWeight: 'bold' }}>KNOWLEDGE ERP</h2>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>BI & Analytics Hub</span>
        </div>

        <button 
          onClick={() => setActiveTab('dashboard')} 
          style={{ ...navButtonStyle, backgroundColor: activeTab === 'dashboard' ? '#0284c7' : 'transparent' }}
        >
          📊 Dashboard Principal
        </button>
        <button 
          onClick={() => setActiveTab('financeiro')} 
          style={{ ...navButtonStyle, backgroundColor: activeTab === 'financeiro' ? '#0284c7' : 'transparent' }}
        >
          💰 Financeiro & DRE
        </button>
        <button 
          onClick={() => setActiveTab('estoque')} 
          style={{ ...navButtonStyle, backgroundColor: activeTab === 'estoque' ? '#0284c7' : 'transparent' }}
        >
          📦 Controle de Estoque
        </button>
        <button 
          onClick={() => setActiveTab('vendas')} 
          style={{ ...navButtonStyle, backgroundColor: activeTab === 'vendas' ? '#0284c7' : 'transparent' }}
        >
          🛒 Vendas & Pedidos
        </button>
        <button 
          onClick={() => setActiveTab('caixa')} 
          style={{ ...navButtonStyle, backgroundColor: activeTab === 'caixa' ? '#0284c7' : 'transparent' }}
        >
          💵 Frente de Caixa (PDV)
        </button>

        <div style={{ marginTop: 'auto', paddingTop: '16px', borderTop: '1px solid #334155' }}>
          <a href="http://localhost:5000" style={{ color: '#94a3b8', textDecoration: 'none', fontSize: '14px', display: 'block', padding: '8px' }}>
            ← Voltar ao Knowledge Hub
          </a>
        </div>
      </aside>

      {/* Conteúdo Principal */}
      <main style={{ flex: 1, padding: '32px', overflowY: 'auto' }}>
        
        {/* Topo do Header */}
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '26px', color: '#f8fafc' }}>
              {activeTab === 'dashboard' && 'Visão Geral & Inteligência de Negócio'}
              {activeTab === 'financeiro' && 'Gestão Financeira & DRE'}
              {activeTab === 'estoque' && 'Gestão de Insumos e Produtos'}
              {activeTab === 'vendas' && 'Funil de Vendas e Faturamento'}
              {activeTab === 'caixa' && 'Frente de Caixa (PDV) & Contingência'}
            </h1>
            <p style={{ margin: '4px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>
              Dados consolidados em tempo real via API Django, Workers Celery e Sync Offline
            </p>
          </div>

          <button
            onClick={handleSolicitarRelatorio}
            disabled={loading}
            style={{
              backgroundColor: loading ? '#475569' : '#0284c7',
              color: '#fff',
              border: 'none',
              padding: '12px 20px',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 'bold',
            }}
          >
            {loading ? 'Disparando Worker...' : '⚡ Processar Relatório BI'}
          </button>
        </header>

        {/* Feedback da Task Celery ou Erro */}
        {taskId && (
          <div style={{ backgroundColor: '#1e293b', borderLeft: '4px solid #4ade80', padding: '12px 16px', marginBottom: '24px', borderRadius: '4px' }}>
            <span style={{ color: '#4ade80', fontWeight: 'bold' }}>Task Celery Criada com Sucesso!</span> — ID: <code style={{ color: '#38bdf8' }}>{taskId}</code>
          </div>
        )}
        {statusMsg && !taskId && (
          <div style={{ backgroundColor: '#1e293b', borderLeft: '4px solid #f87171', padding: '12px 16px', marginBottom: '24px', borderRadius: '4px' }}>
            <span style={{ color: '#f87171' }}>{statusMsg}</span>
          </div>
        )}

        {/* Tab 1: Dashboard Principal BI */}
        {activeTab === 'dashboard' && (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '32px' }}>
              <CardKpi title="Receita Bruta" value="R$ 148.500,00" color="#4ade80" detail="+12% em relação ao mês anterior" />
              <CardKpi title="Despesas Totais" value="R$ 62.300,00" color="#f87171" detail="Dentro do orçamento previsto" />
              <CardKpi title="Margem Líquida" value="58.0%" color="#38bdf8" detail="Excelente rentabilidade" />
              <CardKpi title="Inadimplência Projetada" value="3.2%" color="#fbbf24" detail="Risco Baixo (Classificação A)" />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
              <div style={cardStyle}>
                <h3 style={cardTitleStyle}>📈 Análise de Tendência & Projeção de Caixa</h3>
                <p style={{ color: '#94a3b8', fontSize: '14px' }}>
                  Previsão de entrada x saída ajustada por algoritmos de análise de risco para os próximos 30 dias.
                </p>
                <div style={{ height: '220px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px dashed #475569', borderRadius: '8px', color: '#64748b' }}>
                  [ Gráfico Interativo de Performance BI ]
                </div>
              </div>

              <div style={cardStyle}>
                <h3 style={cardTitleStyle}>🧠 Matriz de Decisão Automatizada</h3>
                <ul style={{ paddingLeft: '18px', color: '#cbd5e1', lineHeight: '1.8', fontSize: '14px' }}>
                  <li><strong>Aporte em Capital:</strong> Saldo liberado para aplicações pós-fixadas.</li>
                  <li><strong>Estoque Alerta:</strong> 4 itens atingiram o Ponto de Pedido Crítico.</li>
                  <li><strong>Gestão de Risco:</strong> 1 cliente corporativo em atraso (Notificação emitida).</li>
                </ul>
              </div>
            </div>
          </>
        )}

        {/* Tab 2: Financeiro */}
        {activeTab === 'financeiro' && (
          <div style={cardStyle}>
            <h3 style={cardTitleStyle}>💰 DRE - Demonstrativo do Resultado do Exercício</h3>
            <table style={tableStyle}>
              <thead>
                <tr style={{ textAlign: 'left', borderBottom: '1px solid #334155' }}>
                  <th style={thStyle}>Categoria</th>
                  <th style={thStyle}>Previsto</th>
                  <th style={thStyle}>Realizado</th>
                  <th style={thStyle}>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr><td style={tdStyle}>Receita Operacional</td><td style={tdStyle}>R$ 150.000,00</td><td style={tdStyle}>R$ 148.500,00</td><td style={{ ...tdStyle, color: '#4ade80' }}>99%</td></tr>
                <tr><td style={tdStyle}>Custo das Mercadorias (CMV)</td><td style={tdStyle}>R$ 45.000,00</td><td style={tdStyle}>R$ 42.100,00</td><td style={{ ...tdStyle, color: '#4ade80' }}>Efetivado</td></tr>
                <tr><td style={tdStyle}>Despesas com Pessoal</td><td style={tdStyle}>R$ 20.000,00</td><td style={tdStyle}>R$ 20.200,00</td><td style={{ ...tdStyle, color: '#fbbf24' }}>Alerta +1%</td></tr>
              </tbody>
            </table>
          </div>
        )}

        {/* Tab 3: Estoque */}
        {activeTab === 'estoque' && (
          <div style={cardStyle}>
            <h3 style={cardTitleStyle}>📦 Inventário & Reposição</h3>
            <table style={tableStyle}>
              <thead>
                <tr style={{ textAlign: 'left', borderBottom: '1px solid #334155' }}>
                  <th style={thStyle}>Produto</th>
                  <th style={thStyle}>Qtd em Estoque</th>
                  <th style={thStyle}>Qtd Mínima</th>
                  <th style={thStyle}>Ação Recomendada</th>
                </tr>
              </thead>
              <tbody>
                <tr><td style={tdStyle}>Servidor Micro-node ESP32</td><td style={tdStyle}>45 un.</td><td style={tdStyle}>15 un.</td><td style={{ ...tdStyle, color: '#4ade80' }}>Estoque Normal</td></tr>
                <tr><td style={tdStyle}>Módulo Sensor AHT20</td><td style={tdStyle}>8 un.</td><td style={tdStyle}>10 un.</td><td style={{ ...tdStyle, color: '#f87171', fontWeight: 'bold' }}>⚠️ Disparar Compra</td></tr>
              </tbody>
            </table>
          </div>
        )}

        {/* Tab 4: Vendas */}
        {activeTab === 'vendas' && (
          <div style={cardStyle}>
            <h3 style={cardTitleStyle}>🛒 Performance de Vendas</h3>
            <p style={{ color: '#94a3b8' }}>Total de 142 ordens executadas no ciclo atual.</p>
          </div>
        )}

        {/* Tab 5: Frente de Caixa (PDV Offline-First) */}
        {activeTab === 'caixa' && (
          <div style={cardStyle}>
            <PdvCaixa />
          </div>
        )}

      </main>
    </div>
  )
}

function CardKpi({ title, value, color, detail }: { title: string; value: string; color: string; detail: string }) {
  return (
    <div style={{ backgroundColor: '#1e293b', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
      <span style={{ color: '#94a3b8', fontSize: '14px' }}>{title}</span>
      <h2 style={{ color, margin: '8px 0 4px 0', fontSize: '24px' }}>{value}</h2>
      <small style={{ color: '#64748b', fontSize: '12px' }}>{detail}</small>
    </div>
  )
}

const navButtonStyle: React.CSSProperties = {
  textAlign: 'left',
  padding: '12px 16px',
  color: '#f8fafc',
  border: 'none',
  borderRadius: '8px',
  cursor: 'pointer',
  fontSize: '14px',
  fontWeight: 500,
  transition: 'background-color 0.2s ease',
}

const cardStyle: React.CSSProperties = {
  backgroundColor: '#1e293b',
  padding: '24px',
  borderRadius: '12px',
  border: '1px solid #334155',
}

const cardTitleStyle: React.CSSProperties = {
  marginTop: 0,
  color: '#f1f5f9',
  fontSize: '18px',
  marginBottom: '16px',
}

const tableStyle: React.CSSProperties = {
  width: '100%',
  borderCollapse: 'collapse',
  color: '#cbd5e1',
  fontSize: '14px',
}

const thStyle: React.CSSProperties = {
  padding: '12px 8px',
  color: '#94a3b8',
}

const tdStyle: React.CSSProperties = {
  padding: '12px 8px',
  borderBottom: '1px solid #334155',
}

export default App