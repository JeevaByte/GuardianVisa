export default function EmergencyRecoveryPage({ latestState }) {
  const emergency = latestState?.outputs?.emergency_agent
  const timeline = latestState?.outputs?.action_engine?.timeline || []
  return (
    <div className="space-y-4">
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-900">
        <h2 className="text-lg font-semibold text-white">Emergency Recovery</h2>
        <div className="text-sm text-slate-300 mt-2">{emergency?.analysis || 'Run planner analysis for emergency playbook.'}</div>
      </div>
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-900">
        <div className="text-sm font-semibold text-white">Timeline</div>
        <ul className="mt-2 space-y-2">
          {timeline.map((entry) => (
            <li key={entry.day} className="text-sm text-slate-300">Day {entry.day}: {entry.focus}</li>
          ))}
          {!timeline.length && <li className="text-sm text-slate-400">No timeline generated yet.</li>}
        </ul>
      </div>
    </div>
  )
}

