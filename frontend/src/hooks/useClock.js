import { useState, useEffect } from 'react'
import { utcClock } from '../utils/time'

export default function useClock() {
  const [time, setTime] = useState(utcClock())
  useEffect(() => {
    const id = setInterval(() => setTime(utcClock()), 1000)
    return () => clearInterval(id)
  }, [])
  return time
}
