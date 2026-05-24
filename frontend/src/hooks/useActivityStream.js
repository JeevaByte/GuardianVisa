import { useEffect, useState } from 'react'
import { createActivityStream } from '../api/client'

export function useActivityStream() {
  const [events, setEvents] = useState([])
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const source = createActivityStream()
    source.onopen = () => setConnected(true)
    source.onerror = () => setConnected(false)
    source.onmessage = (evt) => {
      if (!evt?.data) return
      try {
        const payload = JSON.parse(evt.data)
        setEvents((prev) => [payload, ...prev].slice(0, 100))
      } catch {
        // noop
      }
    }
    return () => source.close()
  }, [])

  return { events, connected }
}

