export default function ScamScannerPage({ latestState }) {
  const scam = latestState?.outputs?.scam_agent
  return (
    <div className="p-4 rounded-xl border border-slate-800 bg-slate-900 space-y-3">
      <h2 className="text-lg font-semibold text-white">Scam Scanner</h2>
      <div className="text-sm text-slate-300">Scam signal: {scam?.scam_signal ?? 'N/A'}</div>
      <ul className="list-disc ml-5 text-sm text-slate-300">
        {(scam?.red_flags || []).map((flag) => <li key={flag}>{flag}</li>)}
      </ul>
      {!scam?.red_flags?.length && <div className="text-sm text-slate-400">No red flags yet.</div>}
    </div>
  )
}

