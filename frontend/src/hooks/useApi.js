import { useCallback, useEffect, useRef, useState } from 'react'

const cache = new Map()

/** Fetch with loading/error state, abort on unmount and a small in-memory cache for GETs. */
export function useApi(fn, deps = [], { key, enabled = true } = {}) {
  const [state, setState] = useState(() => ({ data: key ? cache.get(key) : undefined, error: null, loading: enabled && !(key && cache.has(key)) }))
  const [nonce, setNonce] = useState(0)
  const fnRef = useRef(fn)
  fnRef.current = fn

  useEffect(() => {
    if (!enabled) return undefined
    const ctrl = new AbortController()
    const cached = key ? cache.get(key) : undefined
    setState({ data: cached, error: null, loading: !cached })
    fnRef.current({ signal: ctrl.signal })
      .then((data) => { if (key) cache.set(key, data); setState({ data, error: null, loading: false }) })
      .catch((error) => { if (error.name !== 'AbortError') setState({ data: cached, error, loading: false }) })
    return () => ctrl.abort()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce, enabled])

  const reload = useCallback(() => { if (key) cache.delete(key); setNonce((n) => n + 1) }, [key])
  return { ...state, reload }
}

export function clearApiCache() { cache.clear() }
