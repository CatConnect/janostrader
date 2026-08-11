import { useState } from 'react'
import useClock from '../hooks/useClock'

export default function Header({ onStart, lastUpdate }) {
  const time = useClock()
  const [key, setKey] = useState(() => localStorage.getItem('janos_key') || '')
  const [live, setLive] = useState(false)

  function handleStart() {
    if (!key.trim()) return
    localStorage.setItem('janos_key', key)
    setLive(true)
    onStart(key.trim())
  }

  return (
    <header className="sticky top-0 z-50 bg-bg/90 backdrop-blur-md border-b border-edge">
      <div className="max-w-7xl mx-auto px-4 h-12 flex items-center justify-between gap-4">

        {/* Logo */}
        <div className="flex items-center gap-2 shrink-0">
          <span className="w-1.5 h-1.5 rounded-full bg-teal shadow-[0_0_6px_#1fffd4] animate-pulse" />
          <span className="text-xs font-bold tracking-widest uppercase text-ink">janostrader</span>
          {live && (
            <span className="flex items-center gap-1 text-[9px] font-bold tracking-widest uppercase text-teal/70 ml-1">
              <span className="w-1 h-1 rounded-full bg-teal/70 animate-pulse" />
              ao vivo
            </span>
          )}
        </div>

        {/* Controls + clock */}
        <div className="flex items-center gap-3">
          {lastUpdate && (
            <span className="hidden sm:block text-[10px] text-dim font-mono tabular">
              atualizado {lastUpdate.toLocaleTimeString('pt-BR')}
            </span>
          )}
          <span className="font-mono text-sm tabular text-dim tracking-wider hidden sm:block">
            {time} <span className="text-[9px] text-dim/50 ml-0.5">utc</span>
          </span>
          <div className="w-px h-4 bg-edge" />
          <input
            type="password"
            value={key}
            onChange={e => setKey(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleStart()}
            placeholder="access key"
            className="bg-card border border-edge text-ink text-xs px-3 py-1.5 rounded-lg w-32 sm:w-40 outline-none focus:border-teal/40 transition-colors font-mono"
          />
          <button
            onClick={handleStart}
            className="bg-teal text-bg text-xs font-bold px-3 py-1.5 rounded-lg hover:opacity-90 transition-opacity whitespace-nowrap"
          >
            Carregar
          </button>
        </div>

      </div>
    </header>
  )
}
