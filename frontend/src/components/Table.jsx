export function Table({ headers, children, minWidth = 520 }) {
  return (
    <div className="overflow-x-auto rounded-xl">
      <table className="w-full bg-card border border-edge rounded-xl" style={{ minWidth, borderCollapse: 'separate', borderSpacing: 0 }}>
        <thead>
          <tr>
            {headers.map(h => (
              <th key={h} className="text-left px-4 py-3 text-[9px] font-bold uppercase tracking-widest text-dim border-b border-edge whitespace-nowrap">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  )
}

export function Tr({ children, className = '' }) {
  return (
    <tr className={`border-b border-edge/50 last:border-0 hover:bg-white/[.02] transition-colors ${className}`}>
      {children}
    </tr>
  )
}

export function Td({ children, className = '' }) {
  return (
    <td className={`px-4 py-3 text-sm whitespace-nowrap font-variant-numeric tabular-nums ${className}`}>
      {children}
    </td>
  )
}

export function EmptyRow({ cols, message = '—' }) {
  return (
    <tr>
      <td colSpan={cols} className="text-center text-dim text-sm italic px-4 py-8">{message}</td>
    </tr>
  )
}
