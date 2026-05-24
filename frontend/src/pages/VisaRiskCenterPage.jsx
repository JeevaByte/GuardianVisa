export default function VisaRiskCenterPage({ latestState }) {
  const visa = latestState?.outputs?.visa_agent
  return (
    <div className="p-4 rounded-xl border border-slate-800 bg-slate-900 space-y-3">
      <h2 className="text-lg font-semibold text-white">Visa Risk Center</h2>
      <div className="text-sm text-slate-300">Days until expiry: {visa?.days_until_expiry ?? 'N/A'}</div>
      <div className="text-sm text-slate-300">Proposed hours: {visa?.proposed_hours ?? 'N/A'}</div>
      <div className="text-sm text-slate-400">{visa?.analysis || 'Run planner analysis to see visa insights.'}</div>
    </div>
  )
}

