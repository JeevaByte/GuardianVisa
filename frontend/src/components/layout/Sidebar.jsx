const ITEMS = [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'visa-risk-center', label: 'Visa Risk Center' },
  { key: 'scam-scanner', label: 'Scam Scanner' },
  { key: 'emergency-recovery', label: 'Emergency Recovery' },
  { key: 'activity-monitor', label: 'AI Activity Monitor' },
  { key: 'student-timeline', label: 'Student Timeline' },
  { key: 'alerts-center', label: 'Alerts Center' },
]

export default function Sidebar({ page, onPageChange }) {
  return (
    <aside className="w-full lg:w-64 bg-slate-900 border-r border-slate-800 lg:min-h-screen">
      <div className="px-5 py-5 border-b border-slate-800">
        <div className="text-xl font-bold text-white">GuardianVisa</div>
        <div className="text-xs text-slate-400 tracking-widest uppercase">AI Operations</div>
      </div>
      <nav className="p-3 space-y-1">
        {ITEMS.map((item) => (
          <button
            key={item.key}
            onClick={() => onPageChange(item.key)}
            className={`w-full text-left px-3 py-2 rounded-lg text-sm transition ${
              page === item.key
                ? 'bg-blue-600 text-white'
                : 'text-slate-300 hover:text-white hover:bg-slate-800'
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>
    </aside>
  )
}

