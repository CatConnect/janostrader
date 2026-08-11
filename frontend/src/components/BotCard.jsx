import { useState, useEffect } from 'react'
import { countdownStr, candleProgress, reltime, seenStatus } from '../utils/time'
import { fmt, pct } from '../utils/fmt'

const seenColor = {
  ok:   'text-emerald',
  warn: 'text-amber',
  dead: 'text-rose',
}

export default function BotCard({ bot, perf }) {
  const [tick, setTick] = useState(0)
  useEffect(() => {
    const id = setInterval(() => setTick(t => t + 1), 1000)
    return () => clearInterval(id)
  }, [])

  const tf = bot.timeframe || '1h'
  const ls = bot.last_seen
  const status = seenStatus(ls)
  const alive  = status === 'ok'
  const p = perf || {}
  const pnl = p.total_profit_usdt ?? null

  return (
    <div className={`
      relative bg-card rounded-xl border overflow-hidden transition-all duration-300
      ${alive ? 'border-teal/30 shadow-[0_0_20px_rgba(31,255,212,.06)]' : 'border-edge'}
    `}>
      {/* top accent bar */}
      <div className={`h-px w-full ${alive ? 'bg-gradient-to-r from-transparent via-teal/60 to-transparent' : 'bg-edge'}`} />

      <div className="p-5">
        {/* name + badges */}
        <div className="flex items-start justify-between gap-3 mb-5">
          <div>
            <div className="text-base font-bold text-ink capitalize">{bot.name}</div>
            <div className="text-[11px] text-dim font-mono mt-0.5">{bot.strategy}</div>
          </div>
          <div className="flex gap-1.5 flex-wrap justify-end">
            <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wide
              ${bot.dry_run ? 'bg-amber/10 text-amber border border-amber/20' : 'bg-emerald/10 text-emerald border border-emerald/20'}`}>
              {bot.dry_run ? 'dry' : 'live'}
            </span>
            <span className="text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wide bg-white/5 text-dim border border-edge">
              {tf}
            </span>
          </div>
        </div>

        {/* stats grid */}
        <div className="grid grid-cols-2 gap-4 mb-5">
          <div>
            <div className="text-[9px] uppercase tracking-widest text-dim mb-1.5">Próxima vela</div>
            <div className="font-mono text-2xl font-light text-teal tabular leading-none">
              {countdownStr(tf)}
            </div>
          </div>
          <div>
            <div className="text-[9px] uppercase tracking-widest text-dim mb-1.5">Último sinal</div>
            <div className={`font-mono text-sm tabular leading-none ${seenColor[status]}`}>
              {reltime(ls)}
            </div>
          </div>
          <div>
            <div className="text-[9px] uppercase tracking-widest text-dim mb-1.5">P&amp;L</div>
            <div className={`font-mono text-sm font-semibold tabular leading-none
              ${pnl == null ? 'text-dim' : pnl >= 0 ? 'text-emerald' : 'text-rose'}`}>
              {pnl == null ? '—' : (pnl >= 0 ? '+' : '') + fmt(pnl) + ' USDT'}
            </div>
          </div>
          <div>
            <div className="text-[9px] uppercase tracking-widest text-dim mb-1.5">Win rate</div>
            <div className="font-mono text-sm tabular leading-none text-ink">
              {pct(p.win_rate_pct)}
            </div>
          </div>
        </div>

        {/* candle progress */}
        <div>
          <div className="flex justify-between text-[9px] text-dim mb-1.5 uppercase tracking-widest">
            <span>progresso da vela</span>
            <span>{candleProgress(tf).toFixed(0)}%</span>
          </div>
          <div className="h-0.5 bg-edge rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-teal/40 to-teal transition-all duration-1000"
              style={{ width: `${candleProgress(tf)}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
