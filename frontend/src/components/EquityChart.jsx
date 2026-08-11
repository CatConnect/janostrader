import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, ReferenceLine,
} from 'recharts'
import { fmtDate } from '../utils/fmt'

function buildEquity(trades) {
  let cum = 0
  return trades
    .filter(t => !t.is_open && t.close_profit_abs != null && t.close_date)
    .sort((a, b) => new Date(a.close_date) - new Date(b.close_date))
    .map(t => {
      cum += Number(t.close_profit_abs)
      return { date: t.close_date, equity: parseFloat(cum.toFixed(4)) }
    })
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  const v = d.equity
  const pos = v >= 0
  return (
    <div className="bg-card border border-edge rounded-lg px-3 py-2 text-xs font-mono shadow-xl">
      <div className="text-dim mb-1">{fmtDate(d.date)}</div>
      <div className={pos ? 'text-emerald' : 'text-rose'}>
        {(pos ? '+' : '') + v.toFixed(4)} USDT
      </div>
    </div>
  )
}

export default function EquityChart({ trades }) {
  const pts = buildEquity(trades)
  if (pts.length < 2) return null

  const last = pts[pts.length - 1].equity
  const color = last >= 0 ? '#00e087' : '#ff4f6a'

  return (
    <div className="bg-card border border-edge rounded-xl p-5">
      <div className="text-[9px] font-bold uppercase tracking-widest text-dim mb-5">
        Curva de equity
      </div>
      <ResponsiveContainer width="100%" height={140}>
        <AreaChart data={pts} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id="eq" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%"   stopColor={color} stopOpacity={0.25} />
              <stop offset="100%" stopColor={color} stopOpacity={0.01} />
            </linearGradient>
          </defs>
          <XAxis dataKey="date" hide />
          <YAxis hide domain={['auto', 'auto']} />
          <ReferenceLine y={0} stroke="#132030" strokeDasharray="3 3" />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="equity"
            stroke={color}
            strokeWidth={2}
            fill="url(#eq)"
            dot={false}
            activeDot={{ r: 4, fill: color, strokeWidth: 0 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
