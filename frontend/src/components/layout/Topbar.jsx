export default function Topbar({ connected }) {
  return (
    <header className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/80 backdrop-blur">
      <div>
        <h1 className="text-lg font-semibold text-white">International Student Protection Platform</h1>
        <p className="text-xs text-slate-400">Planner · Memory · Risk Engine · Monitoring</p>
      </div>
      <div className="flex items-center gap-2 text-xs rounded-full px-3 py-1 border border-slate-700 bg-slate-900">
        <span className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400' : 'bg-amber-400'}`} />
        <span className="text-slate-300">{connected ? 'Live stream connected' : 'Reconnecting stream'}</span>
      </div>
    </header>
  )
}

