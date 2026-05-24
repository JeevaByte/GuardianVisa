import RiskBadge from '../components/ui/RiskBadge'

export default function AlertsCenterPage({ alerts }) {
  return (
    <div className="p-4 rounded-xl border border-slate-800 bg-slate-900">
      <h2 className="text-lg font-semibold text-white mb-3">Alerts Center</h2>
      <div className="space-y-2">
        {alerts.map((alert) => (
          <div key={alert.id} className="p-3 rounded-lg border border-slate-700 bg-slate-950">
            <div className="flex items-center justify-between gap-2">
              <RiskBadge severity={alert.severity} />
              <span className="text-xs text-slate-500">{alert.created_at}</span>
            </div>
            <div className="text-sm text-slate-200 mt-2">{alert.message}</div>
          </div>
        ))}
        {!alerts.length && <div className="text-sm text-slate-400">No active alerts.</div>}
      </div>
    </div>
  )
}

