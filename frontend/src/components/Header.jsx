import { useState, useEffect } from 'react'
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
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center gap-4">

        {/* Logo */}
        <div className="flex items-center gap-2.5 shrink-0">
          <span className="w-2 h-2 rounded-full bg-teal shadow-[0_0_8px_#1fffd4] animate-pulse" />
          <span className="text-xs font-bold tracking-widest uppercase text-ink">janostrader</span>
        </div>

        {/* Clock — centro */}
        <div className="flex-1 flex flex-col items-center">
          <span className="font-mono text-teal tabular text-2xl sm:text-3xl font-light tracking-widest leading-none">
            {time}
          </span>
          <span className="text-[9px] tracking-[.2em] uppercase text-dim mt-0.5">UTC</span>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2 shrink-0">
          {live && (
            <span className="hidden sm:flex items-center gap-1.5 text-[10px] font-bold tracking-widest uppercase text-teal bg-teal/10 border border-teal/20 rounded-full px-3 py-1">
              <span className="w-1.5 h-1.5 rounded-full bg-teal animate-pulse" />
              ao vivo
            </span>
          )}
          {lastUpdate && (
            <span className="hidden md:block text-[10px] text-dim font-mono">
              {lastUpdate.toLocaleTimeString('pt-BR')}
            </span>
          )}
          <input
            type="password"
            value={key}
            onChange={e => setKey(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleStart()}
            placeholder="access key"
            className="bg-card border border-edge text-ink text-sm px-3 py-1.5 rounded-lg w-32 sm:w-44 outline-none focus:border-teal/50 transition-colors font-sans"
          />
          <button
            onClick={handleStart}
            className="bg-teal text-bg text-sm font-bold px-4 py-1.5 rounded-lg hover:opacity-90 transition-opacity whitespace-nowrap"
          >
            Carregar
          </button>
        </div>
      </div>
    </header>
  )
}
