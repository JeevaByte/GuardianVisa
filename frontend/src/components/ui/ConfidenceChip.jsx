export default function ConfidenceChip({ value = 0 }) {
  const pct = Math.round(value * 100)
  return (
    <span className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-xs text-slate-300">
      Confidence: {pct}%
    </span>
  )
}

