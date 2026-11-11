import { cx } from './ui'

/** Semi-circular gauge. Renders an explicit "Insufficient evidence" state instead of a number. */
export default function CoverageGauge({ coverage, size = 148 }) {
  const scored = coverage?.state === 'scored'
  const score = scored ? coverage.score : 0
  const r = 52, c = Math.PI * r
  const dash = (score / 100) * c
  return (
    <div className="inline-flex flex-col items-center" style={{ width: size }}>
      <div className="relative">
      <svg viewBox="0 0 128 72" width={size} height={size * 0.5625} role="img"
        aria-label={scored ? `Evidence coverage ${score} out of 100, ${coverage.band}` : 'Evidence coverage: insufficient evidence to score'}>
        <path d="M12 66 A52 52 0 0 1 116 66" fill="none" stroke="#E4E8EE" strokeWidth="10" strokeLinecap="round" strokeDasharray={scored ? undefined : '2 6'} />
        {scored && <path d="M12 66 A52 52 0 0 1 116 66" fill="none" stroke="#317F86" strokeWidth="10" strokeLinecap="round" strokeDasharray={`${dash} ${c}`} />}
      </svg>
      <div className="absolute inset-x-0 bottom-0 flex flex-col items-center">
        {scored
          ? <span className="text-3xl font-semibold tabular-nums leading-none text-navy">{score}</span>
          : <span className="px-2 text-center text-[11px] font-semibold leading-tight text-ink-500">Insufficient<br />evidence</span>}
      </div>
      </div>
      <span className={cx('mt-1.5 text-xs font-semibold', scored ? 'text-teal-700' : 'text-ink-500')}>{scored ? coverage.band : 'Not scored'}</span>
    </div>
  )
}
