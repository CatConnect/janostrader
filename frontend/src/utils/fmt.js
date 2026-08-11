export const fmt   = (n, d = 2) => n == null ? '—' : Number(n).toFixed(d)
export const pct   = n => n == null ? '—' : Number(n).toFixed(1) + '%'
export const sign  = n => n > 0 ? 'pos' : n < 0 ? 'neg' : ''
export const fmtDate = d => d
  ? new Date(d).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
  : '—'

export const fmtDur = h => {
  if (h == null) return '—'
  const hh = Math.floor(h), mm = Math.round((h - hh) * 60)
  return hh > 0 ? `${hh}h ${mm}m` : `${mm}m`
}

export const signedUsdt = n => {
  if (n == null) return '—'
  return (n >= 0 ? '+' : '') + fmt(n) + ' U'
}
