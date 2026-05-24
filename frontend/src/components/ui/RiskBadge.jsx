const COLOR_MAP = {
  SAFE: 'bg-emerald-900 text-emerald-300 border-emerald-700',
  LOW: 'bg-cyan-900 text-cyan-300 border-cyan-700',
  MEDIUM: 'bg-amber-900 text-amber-300 border-amber-700',
  HIGH: 'bg-orange-900 text-orange-300 border-orange-700',
  CRITICAL: 'bg-red-900 text-red-300 border-red-700',
}

export default function RiskBadge({ severity }) {
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${COLOR_MAP[severity] || COLOR_MAP.LOW}`}>
      {severity || 'UNKNOWN'}
    </span>
  )
}

