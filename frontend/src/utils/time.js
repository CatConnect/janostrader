const TFM = { '1m':1,'3m':3,'5m':5,'15m':15,'30m':30,'1h':60,'4h':240,'1d':1440 }

export const nextCandleMs = tf => {
  const ms = (TFM[tf] || 60) * 60_000
  return Math.ceil((Date.now() + 1) / ms) * ms
}

export const candleProgress = tf => {
  const ms = (TFM[tf] || 60) * 60_000
  const next = nextCandleMs(tf)
  return ((ms - (next - Date.now())) / ms) * 100
}

export const countdownStr = tf => {
  const d = nextCandleMs(tf) - Date.now()
  if (d <= 0) return '00:00'
  const m = String(Math.floor(d / 60_000)).padStart(2, '0')
  const s = String(Math.floor((d % 60_000) / 1000)).padStart(2, '0')
  return `${m}:${s}`
}

export const reltime = iso => {
  if (!iso) return 'nunca'
  const s = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (s < 60)   return `${s}s atrás`
  if (s < 3600) return `${Math.floor(s / 60)}m atrás`
  return `${Math.floor(s / 3600)}h atrás`
}

export const seenStatus = iso => {
  if (!iso) return 'dead'
  const s = (Date.now() - new Date(iso).getTime()) / 1000
  if (s < 120) return 'ok'
  if (s < 600) return 'warn'
  return 'dead'
}

export const elapsed = iso => {
  if (!iso) return '—'
  const d = Date.now() - new Date(iso).getTime()
  const h = Math.floor(d / 3_600_000)
  const m = Math.floor((d % 3_600_000) / 60_000)
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}

export const utcClock = () => {
  const n = new Date()
  const p = v => String(v).padStart(2, '0')
  return `${p(n.getUTCHours())}:${p(n.getUTCMinutes())}:${p(n.getUTCSeconds())}`
}
