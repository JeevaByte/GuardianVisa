export default function HeatmapRow({ label, value }) {
  const pct = Math.max(0, Math.min(100, Math.round(value || 0)))
  const hue = pct < 35 ? 'bg-emerald-500' : pct < 60 ? 'bg-amber-500' : pct < 80 ? 'bg-orange-500' : 'bg-red-500'
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs text-slate-300">
        <span className="capitalize">{label}</span>
        <span>{pct}</span>
      </div>
      <div className="h-2 bg-slate-800 rounded">
        <div className={`h-2 rounded ${hue}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

