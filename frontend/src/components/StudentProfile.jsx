function getDaysUntil(dateStr) {
  const today = new Date()
  const target = new Date(dateStr)
  return Math.ceil((target - today) / (1000 * 60 * 60 * 24))
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-AU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export default function StudentProfile({ student }) {
  const {
    name,
    university,
    visaType,
    visaExpiry,
    currentHours,
    hoursLimit,
    termStart,
    termEnd,
  } = student

  const daysToExpiry = getDaysUntil(visaExpiry)
  const monthsToExpiry = daysToExpiry / 30

  const visaColor =
    monthsToExpiry > 6
      ? 'text-green-400'
      : monthsToExpiry > 3
      ? 'text-amber-400'
      : 'text-red-400'

  const visaBadgeBg =
    monthsToExpiry > 6
      ? 'bg-green-900/40 border-green-700'
      : monthsToExpiry > 3
      ? 'bg-amber-900/40 border-amber-700'
      : 'bg-red-900/40 border-red-700'

  const hoursPercent = Math.min((currentHours / hoursLimit) * 100, 100)
  const hoursBarColor =
    hoursPercent < 60
      ? 'bg-green-500'
      : hoursPercent < 85
      ? 'bg-amber-500'
      : 'bg-red-500'

  const hoursTextColor =
    hoursPercent < 60
      ? 'text-green-400'
      : hoursPercent < 85
      ? 'text-amber-400'
      : 'text-red-400'

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-5 shadow-xl">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-lg font-bold shadow-lg">
            {name.charAt(0)}
          </div>
          <div>
            <h2 className="font-bold text-white text-lg leading-tight">{name}</h2>
            <p className="text-slate-400 text-sm">{university}</p>
          </div>
        </div>
        <span className="text-xs bg-slate-700 text-slate-300 px-2.5 py-1 rounded-full border border-slate-600 font-medium">
          {visaType}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Visa Expiry */}
        <div className={`rounded-lg border p-3 ${visaBadgeBg}`}>
          <p className="text-xs text-slate-400 uppercase tracking-wider font-medium mb-1">
            Visa Expiry
          </p>
          <p className={`font-bold text-base ${visaColor}`}>{formatDate(visaExpiry)}</p>
          <p className={`text-xs mt-0.5 ${visaColor}`}>
            {daysToExpiry > 0 ? `${daysToExpiry} days remaining` : 'EXPIRED'}
          </p>
        </div>

        {/* Work Hours */}
        <div className="rounded-lg border border-slate-700 bg-slate-900/50 p-3 sm:col-span-1">
          <div className="flex items-center justify-between mb-1">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-medium">
              Work Hours
            </p>
            <span className={`text-xs font-bold ${hoursTextColor}`}>
              {currentHours}/{hoursLimit} hrs
            </span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2.5 mt-2">
            <div
              className={`h-2.5 rounded-full transition-all duration-500 ${hoursBarColor} ${
                hoursPercent >= 85 ? 'animate-pulse' : ''
              }`}
              style={{ width: `${hoursPercent}%` }}
            />
          </div>
          <p className={`text-xs mt-1.5 font-medium ${hoursTextColor}`}>
            {hoursLimit - currentHours > 0
              ? `${hoursLimit - currentHours} hrs remaining this week`
              : '⚠️ Limit reached!'}
          </p>
        </div>

        {/* Term Dates */}
        <div className="rounded-lg border border-slate-700 bg-slate-900/50 p-3">
          <p className="text-xs text-slate-400 uppercase tracking-wider font-medium mb-1">
            Term Dates
          </p>
          <p className="text-slate-300 text-sm font-medium">{formatDate(termStart)}</p>
          <p className="text-slate-500 text-xs">→</p>
          <p className="text-slate-300 text-sm font-medium">{formatDate(termEnd)}</p>
        </div>
      </div>
    </div>
  )
}
