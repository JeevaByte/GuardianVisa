import { useState } from 'react'
import StudentProfile from './components/StudentProfile.jsx'
import ChatInterface from './components/ChatInterface.jsx'
import RiskAlert from './components/RiskAlert.jsx'
import ScamScanner from './components/ScamScanner.jsx'

const MOCK_STUDENT = {
  name: 'Priya Sharma',
  university: 'University of Melbourne',
  visaType: 'Student Visa (Subclass 500)',
  visaExpiry: '2025-11-14',
  currentHours: 18,
  hoursLimit: 20,
  termStart: '2025-02-24',
  termEnd: '2025-06-20',
}

const TABS = [
  { id: 'visa', label: '🛡️ Visa Guard' },
  { id: 'scam', label: '🔍 Scam Scanner' },
  { id: 'emergency', label: '🚨 Emergency Plan' },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('visa')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleTabChange = (tabId) => {
    setActiveTab(tabId)
    setResult(null)
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      {/* Header */}
      <header className="bg-navy-900 border-b border-slate-700 shadow-lg"
        style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)' }}>
        <div className="max-w-4xl mx-auto px-4 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-4xl select-none">🛡️</span>
            <div>
              <h1 className="text-2xl font-extrabold tracking-tight text-white">
                GuardianVisa
              </h1>
              <p className="text-xs text-slate-400 font-medium tracking-widest uppercase mt-0.5">
                Not a chatbot. A guardian.
              </p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-2 bg-slate-800 rounded-full px-4 py-1.5 border border-slate-700">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
            <span className="text-xs text-slate-300 font-medium">AI Agents Active</span>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Student Profile */}
        <StudentProfile student={MOCK_STUDENT} />

        {/* Tab Navigation */}
        <div className="flex gap-2 bg-slate-800 p-1.5 rounded-xl border border-slate-700">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={`flex-1 py-2.5 px-3 rounded-lg text-sm font-semibold transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Chat Interface */}
        <ChatInterface
          mode={activeTab}
          onResult={setResult}
          onLoading={setLoading}
          loading={loading}
        />

        {/* Result Display */}
        {result && !loading && (
          <div className="animate-fade-in">
            {activeTab === 'scam' ? (
              <ScamScanner data={result} />
            ) : (
              <RiskAlert data={result} mode={activeTab} />
            )}
          </div>
        )}
      </main>

      <footer className="max-w-4xl mx-auto px-4 py-8 text-center text-xs text-slate-600 border-t border-slate-800 mt-8">
        GuardianVisa · Hackathon Demo · AI outputs are guidance only, not legal advice.
      </footer>
    </div>
  )
}
