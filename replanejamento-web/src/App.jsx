import React, { useState, useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  // Referências para as instâncias dos gráficos
  const chartPerformanceRef = useRef(null);
  const chartFaltasRef = useRef(null);
  const chartRadarTurmaRef = useRef(null);
  const chartRadarAlunosRef = useRef(null);

  useEffect(() => {
    // Chart 1: Performance por Disciplina
    const ctxPerf = document.getElementById('chartSubjectPerformance');
    if (ctxPerf) {
      if (chartPerformanceRef.current) chartPerformanceRef.current.destroy();
      chartPerformanceRef.current = new Chart(ctxPerf, {
        type: 'bar',
        data: {
          labels: ['Lógica e Prog.', 'Redes & SO', 'Metodologias Ágeis', 'Carreiras Tech'],
          datasets: [
            { label: 'Média da Turma (3º Bim)', data: [6.1, 6.5, 7.2, 7.8], backgroundColor: '#0284c7' },
            { label: 'Prova Paulista (Benchmark)', data: [5.8, 6.0, 7.0, 8.0], backgroundColor: '#94a3b8' }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });
    }

    // Chart 2: Faltas x Rendimento
    const ctxFaltas = document.getElementById('chartFaltasRendimento');
    if (ctxFaltas) {
      if (chartFaltasRef.current) chartFaltasRef.current.destroy();
      chartFaltasRef.current = new Chart(ctxFaltas, {
        type: 'scatter',
        data: {
          datasets: [{
            label: 'Alunos',
            data: [
              { x: 2, y: 9.0 }, { x: 3, y: 8.5 }, { x: 5, y: 6.5 },
              { x: 8, y: 6.8 }, { x: 14, y: 4.2 }, { x: 16, y: 4.8 }, { x: 18, y: 4.5 }
            ],
            backgroundColor: '#ef4444'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { title: { display: true, text: 'Total de Faltas' } },
            y: { title: { display: true, text: 'Média de Notas' }, min: 0, max: 10 }
          }
        }
      });
    }

    // Chart 3: Radar da Turma
    const ctxRadarTurma = document.getElementById('chartRadarTurma');
    if (ctxRadarTurma && activeTab === 'radar') {
      if (chartRadarTurmaRef.current) chartRadarTurmaRef.current.destroy();
      chartRadarTurmaRef.current = new Chart(ctxRadarTurma, {
        type: 'radar',
        data: {
          labels: ['Raciocínio Lógico', 'Arquitetura de Redes', 'Trabalho em Equipe', 'Autonomia', 'Resolução de Problemas'],
          datasets: [
            {
              label: 'Média da Turma',
              data: [62, 68, 85, 70, 65],
              fill: true,
              backgroundColor: 'rgba(2, 132, 199, 0.2)',
              borderColor: '#0284c7'
            },
            {
              label: 'Meta Esperada',
              data: [80, 80, 80, 80, 80],
              fill: true,
              backgroundColor: 'rgba(148, 163, 184, 0.1)',
              borderColor: '#94a3b8',
              borderDash: [5, 5]
            }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { r: { min: 0, max: 100 } } }
      });
    }

    // Chart 4: Radar Comparativo de Alunos (Monitor vs Recomposição)
    const ctxRadarAlunos = document.getElementById('chartRadarAlunos');
    if (ctxRadarAlunos && activeTab === 'radar') {
      if (chartRadarAlunosRef.current) chartRadarAlunosRef.current.destroy();
      chartRadarAlunosRef.current = new Chart(ctxRadarAlunos, {
        type: 'radar',
        data: {
          labels: ['Lógica POO', 'Estruturas de Dados', 'Comandos Linux/Redes', 'Gestão de Projetos', 'Assiduidade'],
          datasets: [
            {
              label: 'Carlos (Monitor Sugerido)',
              data: [90, 85, 88, 75, 95],
              fill: true,
              backgroundColor: 'rgba(16, 185, 129, 0.2)',
              borderColor: '#10b981'
            },
            {
              label: 'Ana Clara (Em Recomposição)',
              data: [40, 45, 50, 70, 60],
              fill: true,
              backgroundColor: 'rgba(239, 68, 68, 0.2)',
              borderColor: '#ef4444'
            }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { r: { min: 0, max: 100 } } }
      });
    }
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
      {/* HEADER NAV */}
      <header className="bg-slate-900 text-white sticky top-0 z-40 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <span className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                EduMetrics <span className="bg-sky-500/20 text-sky-300 text-xs px-2 py-0.5 rounded border border-sky-500/30 font-semibold uppercase">Pro</span>
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="bg-slate-800 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700">2026 - 3º Bimestre</span>
            </div>
          </div>
        </div>

        {/* TABS */}
        <div className="bg-slate-800/80 border-t border-slate-700 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto flex space-x-2 text-xs font-medium py-1">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-4 py-2 rounded-md ${activeTab === 'dashboard' ? 'bg-sky-600 text-white font-semibold' : 'text-slate-300 hover:text-white'}`}
            >
              📊 Visão Geral
            </button>
            <button
              onClick={() => setActiveTab('radar')}
              className={`px-4 py-2 rounded-md ${activeTab === 'radar' ? 'bg-sky-600 text-white font-semibold' : 'text-slate-300 hover:text-white'}`}
            >
              🕸️ Radar de Competências
            </button>
            <button
              onClick={() => setActiveTab('interventions')}
              className={`px-4 py-2 rounded-md ${activeTab === 'interventions' ? 'bg-sky-600 text-white font-semibold' : 'text-slate-300 hover:text-white'}`}
            >
              🎯 Central de Intervenção
            </button>
          </div>
        </div>
      </header>

      {/* MAIN CONTENT */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* BANNER */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
          <div>
            <span className="px-2.5 py-0.5 bg-sky-100 text-sky-800 text-xs font-semibold rounded-full">Ensino Técnico Integral (9h)</span>
            <h1 className="text-xl font-bold text-slate-900 mt-1">Conselho de Classe e Replanejamento Contínuo</h1>
          </div>
        </div>

        {/* TAB CONTENT: DASHBOARD */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-7 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <h3 className="font-bold text-slate-900 text-sm mb-4">Média por Componente Curricular</h3>
                <div className="h-64"><canvas id="chartSubjectPerformance"></canvas></div>
              </div>
              <div className="lg:col-span-5 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <h3 className="font-bold text-slate-900 text-sm mb-4">Matriz: Absenteísmo x Rendimento</h3>
                <div className="h-64"><canvas id="chartFaltasRendimento"></canvas></div>
              </div>
            </div>
          </div>
        )}

        {/* TAB CONTENT: RADAR */}
        {activeTab === 'radar' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-6 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="font-bold text-slate-900 text-base mb-2">Diagnóstico de Habilidades da Turma</h3>
              <p className="text-xs text-slate-500 mb-4">Média da Turma x Meta Esperada (BNCC / Currículo Paulista)</p>
              <div className="h-80"><canvas id="chartRadarTurma"></canvas></div>
            </div>
            <div className="lg:col-span-6 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="font-bold text-slate-900 text-base mb-2">Perfil de Alunos: Monitor vs Recomposição</h3>
              <p class="text-xs text-slate-500 mb-4">Mapeamento para Formação de Duplas de Tutoria</p>
              <div className="h-80"><canvas id="chartRadarAlunos"></canvas></div>
            </div>
          </div>
        )}

        {/* TAB CONTENT: INTERVENTIONS */}
        {activeTab === 'interventions' && (
          <div className="bg-slate-900 text-white p-6 rounded-xl border border-slate-800 space-y-4">
            <h3 className="font-bold text-base">Agrupamento Produtivo Automático (Duplas de Tutoria)</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                <span className="text-xs text-sky-400 font-bold block mb-1">Dupla #1 - Lógica de Programação</span>
                <p className="text-xs text-emerald-400">👑 Monitor: Carlos Eduardo (Nota: 8.8)</p>
                <p className="text-xs text-red-400">🎯 Recomposição: Ana Clara Souza (Nota: 4.2)</p>
              </div>
              <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                <span className="text-xs text-sky-400 font-bold block mb-1">Dupla #2 - Redes e SO</span>
                <p className="text-xs text-emerald-400">👑 Monitor: Fernanda Ribeiro (Nota: 9.5)</p>
                <p className="text-xs text-red-400">🎯 Recomposição: Bruno Henrique (Nota: 3.5)</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}