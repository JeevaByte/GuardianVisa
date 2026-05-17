import { useState } from 'react'

const SCORE_CONFIG = {
  LOW: { bg: 'bg-green-900/30', border: 'border-green-600', badge: 'bg-green-600', text: 'text-green-300', label: 'LOW', icon: '✅' },
  MEDIUM: { bg: 'bg-amber-900/30', border: 'border-amber-500', badge: 'bg-amber-500', text: 'text-amber-300', label: 'MEDIUM', icon: '⚠️' },
  HIGH: { bg: 'bg-red-900/40', border: 'border-red-500', badge: 'bg-red-600', text: 'text-red-300', label: 'HIGH', icon: '🚨' },
  DANGER: { bg: 'bg-red-950', border: 'border-red-600', badge: 'bg-red-700', text: 'text-red-200', label: 'DANGER', icon: '🔴' },
}

const SCAM_PATTERNS = [
  { key: 'upfront_payment', label: 'Large upfront payment requested' },
  { key: 'owner_overseas', label: 'Owner claims to be overseas' },
  { key: 'price_too_low', label: 'Price suspiciously below market rate' },
  { key: 'no_inspection', label: 'Cannot inspect property in person' },
  { key: 'urgency', label: 'Urgency / "act fast" pressure tactics' },
  { key: 'wire_transfer', label: 'Asks for bank transfer or gift cards' },
  { key: 'no_contract', label: 'No formal lease agreement offered' },
]

export default function ScamScanner({ data }) {
  const [reportSent, setReportSent] = useState(false)

  if (!data) return null

  const riskLevel = data.risk_level || 'LOW'
  const cfg = SCORE_CONFIG[riskLevel] || SCORE_CONFIG.LOW
  const isHighRisk = riskLevel === 'HIGH' || riskLevel === 'DANGER'

  const flags = data.red_flags || []
  const patterns = data.matched_patterns || []
  const advice = data.advice || ''
  const score = data.scam_score ?? null

  return (
    <div className={`rounded-xl border-2 ${cfg.bg} ${cfg.border} overflow-hidden shadow-2xl ${isHighRisk ? 'animate-pulse' : ''}`}>
      {/* Header */}
      <div className="px-5 py-4">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{cfg.icon}</span>
            <div>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-bold px-3 py-1 rounded-full ${cfg.badge} text-white tracking-widest uppercase`}>
                  SCAM RISK: {cfg.label}
                </span>
                {score !== null && (
                  <span className="text-xs text-slate-400 font-mono">
                    Score: {score}/100
                  </span>
                )}
              </div>
              <h2 className={`mt-1 text-xl font-extrabold ${cfg.text}`}>
                {isHighRisk
                  ? '🚨 This listing shows scam warning signs'
                  : riskLevel === 'MEDIUM'
                  ? '⚠️ Proceed with caution'
                  : '✅ No major red flags detected'}
              </h2>
            </div>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="bg-slate-800 px-5 py-5 space-y-5">
        {/* Score Bar */}
        {score !== null && (
          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Safe</span>
              <span>Scam Risk Score: {score}/100</span>
              <span>Scam</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-700 ${
                  score < 40 ? 'bg-green-500' : score < 70 ? 'bg-amber-500' : 'bg-red-600'
                }`}
                style={{ width: `${score}%` }}
              />
            </div>
          </div>
        )}

        {/* Red Flags */}
        {flags.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs text-red-400 uppercase tracking-wider font-bold">
              🚩 Red Flags Detected ({flags.length})
            </p>
            <ul className="space-y-2">
              {flags.map((flag, i) => (
                <li
                  key={i}
                  className="flex items-start gap-2.5 bg-red-950/40 border border-red-900 rounded-lg px-3 py-2.5 text-sm"
                >
                  <span className="text-red-400 shrink-0 mt-0.5">⚠️</span>
                  <span className="text-red-200 font-medium">{flag}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Matched Patterns */}
        {patterns.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs text-amber-400 uppercase tracking-wider font-bold">
              🔍 Matched Scam Patterns
            </p>
            <div className="flex flex-wrap gap-2">
              {patterns.map((pattern, i) => {
                const known = SCAM_PATTERNS.find((p) => p.key === pattern)
                return (
                  <span
                    key={i}
                    className="text-xs font-medium px-2.5 py-1 rounded-full bg-amber-900/50 border border-amber-700 text-amber-300"
                  >
                    {known ? known.label : pattern}
                  </span>
                )
              })}
            </div>
          </div>
        )}

        {/* Advice */}
        {advice && (
          <div className="bg-slate-900/60 border border-slate-700 rounded-lg p-4">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-2">
              💬 Advice
            </p>
            <p className="text-slate-300 text-sm leading-relaxed">{advice}</p>
          </div>
        )}

        {/* Safe Alternatives */}
        {data.safe_alternatives && data.safe_alternatives.length > 0 && (
          <div className="bg-green-950/30 border border-green-900 rounded-lg p-4">
            <p className="text-xs text-green-400 uppercase tracking-wider font-semibold mb-2">
              ✅ Safer Alternatives
            </p>
            <ul className="space-y-1.5">
              {data.safe_alternatives.map((alt, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-green-300">
                  <span className="shrink-0 mt-0.5">→</span>
                  <span>{alt}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* CTA */}
        <div className="flex flex-wrap gap-3 pt-2 border-t border-slate-700">
          <button
            onClick={() => setReportSent(true)}
            disabled={reportSent}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all ${
              reportSent
                ? 'bg-slate-700 text-slate-400 cursor-default'
                : 'bg-red-700 hover:bg-red-600 text-white shadow-lg shadow-red-900/40 active:scale-95'
            }`}
          >
            {reportSent ? '✓ Reported to University Housing' : '🏠 Report to University Housing'}
          </button>
          <button
            onClick={() => navigator.clipboard.writeText(JSON.stringify(data, null, 2))}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold bg-slate-700
              hover:bg-slate-600 text-slate-300 hover:text-white border border-slate-600 transition-all"
          >
            📋 Copy Report
          </button>
        </div>
      </div>
    </div>
  )
}
