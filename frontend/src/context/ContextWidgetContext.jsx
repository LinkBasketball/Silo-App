import { createContext, useCallback, useContext, useMemo, useState } from 'react'

const Ctx = createContext(null)

/**
 * Global state for the floating context widget. A page "publishes" what the reader is
 * looking at (a stored article id, or a fresh analysis payload); the widget renders it.
 */
export function ContextWidgetProvider({ children }) {
  const [source, setSource] = useState(null) // {kind:'article', id} | {kind:'analysis', payload}
  const [open, setOpen] = useState(false)
  const [tab, setTab] = useState('overview')
  const [focusClaim, setFocusClaim] = useState(null)

  const showClaim = useCallback((sentenceIndex) => {
    setFocusClaim(sentenceIndex)
    setTab('evidence')
    setOpen(true)
  }, [])

  const value = useMemo(() => ({ source, setSource, open, setOpen, tab, setTab, focusClaim, setFocusClaim, showClaim }),
    [source, open, tab, focusClaim, showClaim])
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useContextWidget() {
  const v = useContext(Ctx)
  if (!v) throw new Error('useContextWidget must be used inside ContextWidgetProvider')
  return v
}
