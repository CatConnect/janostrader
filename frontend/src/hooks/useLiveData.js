import { useState, useEffect, useCallback, useRef } from 'react'

const INTERVAL = 30_000

export default function useLiveData(apiKey) {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)
  const [lastUpdate, setLastUpdate] = useState(null)
  const timerRef = useRef(null)

  const load = useCallback(async () => {
    if (!apiKey) return
    setLoading(true)
    try {
      const headers = { 'x-api-key': apiKey }
      const [bots, perf, open, trades] = await Promise.all([
        fetch('/api/bots',                            { headers }).then(r => r.json()),
        fetch('/api/trades/performance',              { headers }).then(r => r.json()),
        fetch('/api/trades/open',                     { headers }).then(r => r.json()),
        fetch('/api/trades?limit=100&is_open=false',  { headers }).then(r => r.json()),
      ])
      setData({ bots, perf, open, trades })
      setLastUpdate(new Date())
      setError(null)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [apiKey])

  useEffect(() => {
    if (!apiKey) return
    load()
    timerRef.current = setInterval(load, INTERVAL)
    return () => clearInterval(timerRef.current)
  }, [apiKey, load])

  return { data, loading, error, lastUpdate, reload: load }
}
