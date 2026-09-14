import { useState, type ReactNode } from 'react'
import heroImg from './assets/hero.png'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import './App.css'

interface ExternalLink {
  href: string
  label: string
  icon: ReactNode
}

interface RelatorioResponse {
  task_id: string
  mensagem: string
}

const API_BASE_URL = 'http://127.0.0.1:8000/api'

async function solicitarRelatorioAPI(): Promise<RelatorioResponse> {
  const response = await fetch(`${API_BASE_URL}/financeiro/relatorios/solicitar`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Erro ${response.status}: ${response.statusText}`)
  }

  return response.json()
}

function Icon({ symbolId, className = 'icon' }: { symbolId: string; className?: string }) {
  return (
    <svg className={className} role="presentation" aria-hidden="true">
      <use href={`/icons.svg#${symbolId}`} />
    </svg>
  )
}

const DOCS_LINKS: ExternalLink[] = [
  {
    href: 'https://vite.dev/',
    label: 'Explore Vite',
    icon: <img className="logo" src={viteLogo} alt="Vite" />,
  },
  {
    href: 'https://react.dev/',
    label: 'Learn more',
    icon: <img className="button-icon" src={reactLogo} alt="React" />,
  },
]

const SOCIAL_LINKS: ExternalLink[] = [
  {
    href: 'https://github.com/vitejs/vite',
    label: 'GitHub',
    icon: <Icon symbolId="github-icon" className="button-icon" />,
  },
  {
    href: 'https://chat.vite.dev/',
    label: 'Discord',
    icon: <Icon symbolId="discord-icon" className="button-icon" />,
  },
  {
    href: 'https://x.com/vite_js',
    label: 'X.com',
    icon: <Icon symbolId="x-icon" className="button-icon" />,
  },
  {
    href: 'https://bsky.app/profile/vite.dev',
    label: 'Bluesky',
    icon: <Icon symbolId="bluesky-icon" className="button-icon" />,
  },
]

function SectionCard({
  iconId,
  title,
  subtitle,
  links,
}: {
  iconId: string
  title: string
  subtitle: string
  links: ExternalLink[]
}) {
  return (
    <div>
      <Icon symbolId={iconId} />
      <h2>{title}</h2>
      <p>{subtitle}</p>
      <ul>
        {links.map((link) => (
          <li key={link.href}>
            <a href={link.href} target="_blank" rel="noreferrer">
              {link.icon}
              {link.label}
            </a>
          </li>
        ))}
      </ul>
    </div>
  )
}

export function App() {
  const [loading, setLoading] = useState<boolean>(false)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [statusMsg, setStatusMsg] = useState<string | null>(null)

  const handleSolicitarRelatorio = async () => {
    setLoading(true)
    setStatusMsg(null)
    setTaskId(null)

    try {
      const data = await solicitarRelatorioAPI()
      setTaskId(data.task_id)
      setStatusMsg(data.mensagem || 'Tarefa enviada com sucesso!')
    } catch (error) {
      console.error('Erro ao conectar com a API:', error)
      setStatusMsg('Erro de conexão ou rota não encontrada.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <section id="center">
        <div className="hero">
          <img src={heroImg} className="base" width="170" height="179" alt="Hero" />
          <img src={reactLogo} className="framework" alt="React logo" />
          <img src={viteLogo} className="vite" alt="Vite logo" />
        </div>

        <div>
          <h1>Módulo Financeiro & Celery</h1>
          <p>
            Clique no botão abaixo para disparar o processamento assíncrono via <code>Celery Worker</code>.
          </p>
        </div>

        <button
          type="button"
          className="counter"
          onClick={handleSolicitarRelatorio}
          disabled={loading}
          style={{ cursor: loading ? 'not-allowed' : 'pointer' }}
        >
          {loading ? 'Disparando Task...' : 'Gerar Relatório Celery'}
        </button>

        {taskId && (
          <p style={{ marginTop: '1rem', color: '#4caf50', wordBreak: 'break-all' }}>
            <strong>Task ID:</strong> <code>{taskId}</code>
          </p>
        )}

        {statusMsg && (
          <p style={{ marginTop: '0.5rem', fontSize: '0.9rem', opacity: 0.9 }}>
            {statusMsg}
          </p>
        )}
      </section>

      <div className="ticks" />

      <section id="next-steps">
        <SectionCard
          iconId="documentation-icon"
          title="Documentation"
          subtitle="Your questions, answered"
          links={DOCS_LINKS}
        />
        <SectionCard
          iconId="social-icon"
          title="Connect with us"
          subtitle="Join the Vite community"
          links={SOCIAL_LINKS}
        />
      </section>

      <div className="ticks" />
      <section id="spacer" />
    </>
  )
}

export default App