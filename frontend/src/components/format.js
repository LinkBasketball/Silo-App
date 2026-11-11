export const fmtDate = (d, opts = { month: 'short', day: 'numeric', year: 'numeric' }) => {
  if (!d) return '—'
  const date = typeof d === 'string' && d.length === 10 ? new Date(`${d}T12:00:00Z`) : new Date(d)
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleDateString('en-US', { ...opts, timeZone: 'UTC' })
}
export const fmtDateTime = (d) => (d ? new Date(d).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit', timeZone: 'UTC', timeZoneName: 'short' }) : '—')
export const fmtUSD = (cents, compact = false) => {
  if (cents === null || cents === undefined) return '—'
  return (cents / 100).toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0, notation: compact ? 'compact' : 'standard' })
}
export const fmtPct = (x, digits = 0) => (x === null || x === undefined ? '—' : `${(x * 100).toFixed(digits)}%`)
export const fmtNum = (x) => (x === null || x === undefined ? '—' : Number(x).toLocaleString('en-US'))
