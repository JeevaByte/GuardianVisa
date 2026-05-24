export default function TimelineList({ items = [] }) {
  if (!items.length) {
    return <div className="text-sm text-slate-400">No timeline events yet.</div>
  }
  return (
    <div className="space-y-3">
      {items.map((item, idx) => (
        <div key={`${item.step || item.event_type}-${idx}`} className="p-3 rounded-lg border border-slate-700 bg-slate-900">
          <div className="text-xs uppercase tracking-wider text-slate-400">{item.step || item.event_type || 'event'}</div>
          <div className="text-sm text-slate-100 mt-1">{item.details || item.message || 'No details'}</div>
          {item.status && <div className="text-xs text-slate-500 mt-1">Status: {item.status}</div>}
        </div>
      ))}
    </div>
  )
}

