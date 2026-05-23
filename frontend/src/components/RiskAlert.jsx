import { useState } from 'react'

const RISK_CONFIG = {
  LOW: {
    bg: 'bg-green-900/30',
    border: 'border-green-600',
    badge: 'bg-green-600',
    text: 'text-green-300',
    icon: '✅',
    label: 'LOW RISK',
    pulse: false,
  },
  MEDIUM: {
    bg: 'bg-amber-900/30',
    border: 'border-amber-500',
    badge: 'bg-amber-500',
    text: 'text-amber-300',
    icon: '⚠️',
    label: 'MEDIUM RISK',
    pulse: false,
  },
  HIGH: {
    bg: 'bg-red-900/40',
    border: 'border-red-500',
    badge: 'bg-red-600',
    text: 'text-red-300',
    icon: '🚨',
    label: 'HIGH RISK',
    pulse: true,
  },
  DANGER: {
    bg: 'bg-red-950',
    border: 'border-red-600',
    badge: 'bg-red-700',
    text: 'text-red-200',
    icon: '🔴',
    label: 'DANGER',
    pulse: true,
  },
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600
        text-slate-300 hover:text-white border border-slate-600 transition-all font-medium"
    >
      {copied ? '✓ Copied!' : '📋 Copy Response'}
    </button>
  )
}

function Collapsible({ title, children }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-slate-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 text-sm font-semibold
          text-slate-300 hover:text-white hover:bg-slate-700/50 transition-all"
      >
        {title}
        <span className={`transition-transform ${open ? 'rotate-180' : ''}`}>▾</span>
      </button>
      {open && <div className="px-4 pb-4 pt-1 bg-slate-900/50">{children}</div>}
    </div>
  )
}

export default function RiskAlert({ data, mode }) {
  if (!data) return null

  const riskLevel = data.risk_level || 'LOW'
  const cfg = RISK_CONFIG[riskLevel] || RISK_CONFIG.LOW
  const isViolation = data.violation === true || riskLevel === 'HIGH' || riskLevel === 'DANGER'

  return (
    <div className={`rounded-xl border-2 ${cfg.bg} ${cfg.border} overflow-hidden shadow-2xl ${cfg.pulse ? 'animate-pulse' : ''}`}>
      {/* Banner */}
      <div className={`px-5 py-4 ${cfg.pulse ? 'animate-none' : ''}`}
        style={cfg.pulse ? { animation: 'none' } : {}}>
        <div className="flex items-center gap-3">
          <span className="text-3xl">{cfg.icon}</span>
          <div className="flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${cfg.badge} text-white tracking-widest uppercase`}>
                {cfg.label}
              </span>
              {isViolation && (
                <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-red-800 text-red-200 uppercase tracking-widest border border-red-600">
                  ⚠️ VISA RISK ALERT
                </span>
              )}
            </div>
            <h2 className={`mt-1 text-xl font-extrabold tracking-tight ${cfg.text}`}>
              {isViolation
                ? 'This request would violate your visa conditions'
                : riskLevel === 'LOW'
                ? "✅ You're Safe"
                : 'Potential visa risk detected'}
            </h2>
          </div>
        </div>
      </div>

      {/* Solid body — no pulse on content */}
      <div className="bg-slate-800 px-5 py-5 space-y-5">
        {/* Hours Math */}
        {(data.current_hours != null) && (
          <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-2">
              Hours Calculation
            </p>
            <div className="text-2xl font-extrabold text-white font-mono tracking-tight">
              {data.current_hours} hrs this week
              {data.proposed_hours != null && (
                <>
                  <span className="text-slate-400 mx-2">+</span>
                  <span className="text-amber-400">{data.proposed_hours} proposed</span>
                  <span className="text-slate-400 mx-2">=</span>
                  <span className={isViolation ? 'text-red-400' : 'text-green-400'}>
                    {(data.current_hours || 0) + (data.proposed_hours || 0)} hrs
                  </span>
                </>
              )}
            </div>
            <p className="text-slate-400 text-sm mt-1">
              Legal limit:{' '}
              <span className="font-bold text-white">{data.limit} hrs/week</span>
              {isViolation && data.proposed_hours != null && (
                <span className="ml-2 text-red-400 font-bold">
                  ({((data.current_hours || 0) + (data.proposed_hours || 0)) - data.limit} hrs over limit!)
                </span>
              )}
            </p>
          </div>
        )}

        {/* Consequence */}
        {data.consequence && (
          <div className="bg-red-950/50 border border-red-900 rounded-lg p-4">
            <p className="text-xs text-red-400 uppercase tracking-wider font-semibold mb-1">
              Potential Consequence
            </p>
            <p className="text-red-300 font-bold text-sm leading-relaxed">{data.consequence}</p>
          </div>
        )}

        {/* Explanation */}
        {data.explanation && !data.consequence && (
          <div className="bg-slate-900/60 border border-slate-700 rounded-lg p-4">
            <p className="text-slate-300 text-sm leading-relaxed">{data.explanation}</p>
          </div>
        )}

        {/* Safe Response */}
        {data.safe_response_draft && (
          <div className="bg-green-950/40 border border-green-800 rounded-lg p-4 space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-xs text-green-400 uppercase tracking-wider font-semibold">
                ✉️ Safe Response Drafted
              </p>
              <CopyButton text={data.safe_response_draft} />
            </div>
            <p className="text-slate-200 text-sm leading-relaxed bg-slate-900/50 rounded-lg p-3 border border-slate-700 italic">
              "{data.safe_response_draft}"
            </p>
          </div>
        )}

        {/* Draft Email (emergency mode) */}
        {data.draft_email && (
          <div className="bg-green-950/40 border border-green-800 rounded-lg p-4 space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-xs text-green-400 uppercase tracking-wider font-semibold">
                ✉️ Draft Email
              </p>
              <CopyButton text={data.draft_email} />
            </div>
            <p className="text-slate-200 text-sm leading-relaxed bg-slate-900/50 rounded-lg p-3 border border-slate-700 italic whitespace-pre-wrap">
              {data.draft_email}
            </p>
          </div>
        )}

        {/* Safe Alternatives */}
        {data.alternatives && data.alternatives.length > 0 && (
          <Collapsible title={`💡 Safe Alternatives (${data.alternatives.length})`}>
            <ul className="space-y-2 mt-2">
              {data.alternatives.map((alt, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                  <span className="text-green-400 mt-0.5 shrink-0">→</span>
                  <span>{alt}</span>
                </li>
              ))}
            </ul>
          </Collapsible>
        )}

        {/* Emergency steps */}
        {data.action_plan_7_days && data.action_plan_7_days.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
              Action Steps
            </p>
            <ol className="space-y-2">
              {data.action_plan_7_days.map((step, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-slate-300 bg-slate-900/50 rounded-lg p-3 border border-slate-700">
                  <span className="w-6 h-6 rounded-full bg-blue-700 flex items-center justify-center text-xs font-bold text-white shrink-0 mt-0.5">
                    {step.day || i + 1}
                  </span>
                  <div className="flex-1">
                    <span>{step.action}</span>
                    {step.priority && (
                      <span className={`ml-2 text-xs font-bold px-2 py-0.5 rounded ${
                        step.priority === 'URGENT' ? 'bg-red-800 text-red-200' :
                        step.priority === 'HIGH' ? 'bg-amber-800 text-amber-200' :
                        'bg-blue-800 text-blue-200'
                      }`}>
                        {step.priority}
                      </span>
                    )}
                  </div>
                </li>
              ))}
            </ol>
          </div>
        )}

        {/* Resources */}
        {data.resources && data.resources.length > 0 && (
          <Collapsible title="📚 Resources & Support">
            <ul className="space-y-1.5 mt-2">
              {data.resources.map((r, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300">
                  <span className="text-slate-500">•</span>
                  {r.url ? (
                    <a href={r.url} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2">
                      {r.name || r}
                    </a>
                  ) : (
                    <span className="text-slate-300">{r}</span>
                  )}
                </li>
              ))}
            </ul>
          </Collapsible>
        )}
      </div>
    </div>
  )
}
