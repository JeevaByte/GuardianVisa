import RiskBadge from '../components/ui/RiskBadge'
import ConfidenceChip from '../components/ui/ConfidenceChip'
import HeatmapRow from '../components/ui/HeatmapRow'

export default function DashboardPage({ latestState }) {
  const risk = latestState?.risk
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900">
          <div className="text-xs text-slate-400 uppercase">Current Severity</div>
          <div className="mt-2"><RiskBadge severity={risk?.severity} /></div>
        </div>
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900">
          <div className="text-xs text-slate-400 uppercase">Risk Score</div>
          <div className="text-2xl font-semibold text-white mt-1">{risk?.normalized_score ?? '--'}</div>
        </div>
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900">
          <div className="text-xs text-slate-400 uppercase">Confidence</div>
          <div className="mt-2"><ConfidenceChip value={risk?.confidence || 0} /></div>
        </div>
      </div>

      <div className="p-4 rounded-xl border border-slate-800 bg-slate-900 space-y-3">
        <div className="text-sm font-semibold text-white">Risk Heatmap</div>
        {risk?.breakdown ? Object.entries(risk.breakdown).map(([k, v]) => <HeatmapRow key={k} label={k} value={v} />) : (
          <div className="text-sm text-slate-400">Run an analysis to populate heatmap.</div>
        )}
      </div>
    </div>
  )
}

