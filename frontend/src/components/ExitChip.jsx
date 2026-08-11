const styles = {
  roi:    'bg-emerald/10 text-emerald border-emerald/20',
  trail:  'bg-teal/10 text-teal border-teal/20',
  stop:   'bg-rose/10 text-rose border-rose/20',
  signal: 'bg-white/5 text-dim border-edge',
  other:  'bg-white/5 text-dim border-edge',
}

function classify(r) {
  if (!r) return 'other'
  const l = r.toLowerCase()
  if (l.includes('roi'))    return 'roi'
  if (l.includes('trail'))  return 'trail'
  if (l.includes('stop'))   return 'stop'
  if (l.includes('signal')) return 'signal'
  return 'other'
}

export default function ExitChip({ reason }) {
  const cls = classify(reason)
  return (
    <span className={`inline-block text-[10px] font-bold font-mono px-2 py-0.5 rounded border ${styles[cls]}`}>
      {reason || '—'}
    </span>
  )
}
