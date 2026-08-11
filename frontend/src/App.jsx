import { useState } from 'react'
import Header from './components/Header'
import BotCard from './components/BotCard'
import KpiTile from './components/KpiTile'
import EquityChart from './components/EquityChart'
import ExitChip from './components/ExitChip'
import SectionLabel from './components/SectionLabel'
import { Table, Tr, Td, EmptyRow } from './components/Table'
import useLiveData from './hooks/useLiveData'
import { fmt, pct, fmtDate, fmtDur } from './utils/fmt'
import { elapsed } from './utils/time'

export default function App() {
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('janos_key') || '')
  const { data, lastUpdate } = useLiveData(apiKey)

  const perf   = data?.perf   ?? []
  const open   = data?.open   ?? []
  const trades = data?.trades ?? []
  const bots   = data?.bots   ?? []

  const perfMap = Object.fromEntries(perf.map(p => [p.strategy, p]))

  const totalPnl    = perf.reduce((s, b) => s + (b.total_profit_usdt || 0), 0)
  const totalTrades = perf.reduce((s, b) => s + (b.total_trades     || 0), 0)
  const avgWr       = perf.length ? perf.reduce((s, b) => s + (b.win_rate_pct || 0), 0) / perf.length : null

  return (
    <div className="min-h-dvh">
      <Header onStart={setApiKey} lastUpdate={lastUpdate} />

      <main className="max-w-7xl mx-auto px-4 py-7 flex flex-col gap-8 pb-20">

        {/* Bots */}
        <section>
          <SectionLabel>Bots em execução</SectionLabel>
          {bots.length === 0 ? (
            <div className="bg-card border border-edge rounded-xl p-8 text-center text-dim text-sm italic">
              {apiKey ? 'Nenhum bot registrado' : 'Informe a access key e clique em Carregar'}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {bots.map(b => (
                <BotCard key={b.name} bot={b} perf={perfMap[b.strategy]} />
              ))}
            </div>
          )}
        </section>

        {/* KPIs */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <KpiTile
            label="P&L realizado"
            value={data ? (totalPnl >= 0 ? '+' : '') + fmt(totalPnl) + ' USDT' : null}
            sub={`${perf.length} estratégia${perf.length !== 1 ? 's' : ''}`}
            valueClass={data ? (totalPnl >= 0 ? 'text-emerald' : 'text-rose') : 'text-dim'}
          />
          <KpiTile
            label="Trades fechados"
            value={data ? totalTrades : null}
            sub={`${trades.length} carregados`}
          />
          <KpiTile
            label="Win rate"
            value={data ? pct(avgWr) : null}
            sub="média geral"
            valueClass={avgWr != null && avgWr >= 50 ? 'text-emerald' : avgWr != null ? 'text-rose' : ''}
          />
          <KpiTile
            label="Abertas"
            value={data ? open.length : null}
            sub={open.length ? open.map(t => t.pair.split('/')[0]).join(' · ') : 'nenhuma'}
          />
        </div>

        {/* Equity */}
        {trades.length >= 2 && <EquityChart trades={trades} />}

        {/* Posições abertas */}
        <section>
          <SectionLabel>Posições abertas</SectionLabel>
          <Table headers={['Bot', 'Par', 'Dir', 'Entrada', 'Stake', 'Lav.', 'Há']}>
            {open.length === 0
              ? <EmptyRow cols={7} message="Nenhuma posição aberta" />
              : open.map(t => (
                <Tr key={t.id}>
                  <Td className="text-dim">{t.strategy}</Td>
                  <Td className="font-mono text-ink">{t.pair}</Td>
                  <Td className={t.is_short ? 'text-rose' : 'text-emerald'}>
                    {t.is_short ? '▼ Short' : '▲ Long'}
                  </Td>
                  <Td className="font-mono">{fmt(t.open_rate, 4)}</Td>
                  <Td className="font-mono">{fmt(t.stake_amount)} USDT</Td>
                  <Td className="font-mono">{t.leverage}×</Td>
                  <Td className="font-mono text-dim">{elapsed(t.open_date)}</Td>
                </Tr>
              ))
            }
          </Table>
        </section>

        {/* Performance */}
        <section>
          <SectionLabel>Performance por estratégia</SectionLabel>
          <Table headers={['Estratégia', 'Trades', 'Win rate', 'P&L USDT', 'Avg %', 'Dur. média']}>
            {perf.length === 0
              ? <EmptyRow cols={6} message={apiKey ? 'Sem trades fechados ainda' : 'Informe a access key'} />
              : perf.map(b => (
                <Tr key={b.strategy}>
                  <Td className="font-mono text-ink">{b.strategy}</Td>
                  <Td className="font-mono">{b.total_trades}</Td>
                  <Td className={`font-mono ${b.win_rate_pct >= 50 ? 'text-emerald' : 'text-rose'}`}>
                    {pct(b.win_rate_pct)}
                  </Td>
                  <Td className={`font-mono font-semibold ${b.total_profit_usdt >= 0 ? 'text-emerald' : 'text-rose'}`}>
                    {(b.total_profit_usdt >= 0 ? '+' : '') + fmt(b.total_profit_usdt)}
                  </Td>
                  <Td className={`font-mono ${b.avg_profit_ratio >= 0 ? 'text-emerald' : 'text-rose'}`}>
                    {pct((b.avg_profit_ratio || 0) * 100)}
                  </Td>
                  <Td className="font-mono text-dim">{fmtDur(b.avg_duration_hours)}</Td>
                </Tr>
              ))
            }
          </Table>
        </section>

        {/* Trades recentes */}
        <section>
          <SectionLabel>Trades recentes</SectionLabel>
          <Table headers={['Bot', 'Par', 'Dir', 'P&L %', 'P&L USDT', 'Saída', 'Fechado']}>
            {trades.length === 0
              ? <EmptyRow cols={7} message="Sem trades fechados" />
              : trades.slice(0, 30).map(t => (
                <Tr key={t.id}>
                  <Td className="text-dim text-xs">{t.strategy}</Td>
                  <Td className="font-mono text-ink">{t.pair}</Td>
                  <Td className={t.is_short ? 'text-rose' : 'text-emerald'}>
                    {t.is_short ? '▼' : '▲'}
                  </Td>
                  <Td className={`font-mono ${t.close_profit >= 0 ? 'text-emerald' : 'text-rose'}`}>
                    {pct((t.close_profit || 0) * 100)}
                  </Td>
                  <Td className={`font-mono font-semibold ${t.close_profit_abs >= 0 ? 'text-emerald' : 'text-rose'}`}>
                    {(t.close_profit_abs >= 0 ? '+' : '') + fmt(t.close_profit_abs)}
                  </Td>
                  <Td><ExitChip reason={t.exit_reason} /></Td>
                  <Td className="font-mono text-dim">{fmtDate(t.close_date)}</Td>
                </Tr>
              ))
            }
          </Table>
        </section>

      </main>
    </div>
  )
}
