export default function KpiTile({ label, value, sub, valueClass = '' }) {
  return (
    <div className="bg-card border border-edge rounded-xl p-5">
      <div className="text-[9px] font-bold uppercase tracking-widest text-dim mb-3">{label}</div>
      <div className={`font-mono text-3xl font-semibold tabular leading-none ${valueClass}`}>
        {value ?? '—'}
      </div>
      {sub && <div className="text-[11px] text-dim font-mono mt-2">{sub}</div>}
    </div>
  )
}
