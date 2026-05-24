import { useEffect, useMemo, useState } from 'react'
import Sidebar from './components/layout/Sidebar'
import Topbar from './components/layout/Topbar'
import DashboardPage from './pages/DashboardPage'
import VisaRiskCenterPage from './pages/VisaRiskCenterPage'
import ScamScannerPage from './pages/ScamScannerPage'
import EmergencyRecoveryPage from './pages/EmergencyRecoveryPage'
import ActivityMonitorPage from './pages/ActivityMonitorPage'
import StudentTimelinePage from './pages/StudentTimelinePage'
import AlertsCenterPage from './pages/AlertsCenterPage'
import { analyzeRisk, getAlerts } from './api/client'
import { useActivityStream } from './hooks/useActivityStream'

function PlannerConsole({ onAnalyzed, loading, setLoading }) {
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const submit = async () => {
    if (!message.trim()) return
    setLoading(true)
    setError('')
    try {
      const response = await analyzeRisk({ userId: 'priya_sharma_demo', message })
      onAnalyzed(response?.planner_state || null)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to run planner analysis.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4 rounded-xl border border-slate-800 bg-slate-900 space-y-3">
      <div className="text-sm font-semibold text-white">Planner Console</div>
      <textarea
        className="w-full min-h-[100px] rounded-lg border border-slate-700 bg-slate-950 text-slate-200 p-3 text-sm"
        placeholder="Describe your visa/scam/emergency situation for autonomous analysis..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <div className="flex items-center gap-3">
        <button
          onClick={submit}
          disabled={loading || !message.trim()}
          className={`px-4 py-2 rounded-lg text-sm font-semibold ${
            loading || !message.trim() ? 'bg-slate-700 text-slate-400' : 'bg-blue-600 text-white hover:bg-blue-500'
          }`}
        >
          {loading ? 'Analyzing...' : 'Run Planner'}
        </button>
        {error && <span className="text-sm text-red-300">{error}</span>}
      </div>
    </div>
  )
}

export default function App() {
  const [page, setPage] = useState('dashboard')
  const [latestState, setLatestState] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(false)
  const { events, connected } = useActivityStream()

  useEffect(() => {
    getAlerts('priya_sharma_demo').then(setAlerts).catch(() => setAlerts([]))
  }, [latestState])

  const pageNode = useMemo(() => {
    if (page === 'dashboard') return <DashboardPage latestState={latestState} />
    if (page === 'visa-risk-center') return <VisaRiskCenterPage latestState={latestState} />
    if (page === 'scam-scanner') return <ScamScannerPage latestState={latestState} />
    if (page === 'emergency-recovery') return <EmergencyRecoveryPage latestState={latestState} />
    if (page === 'activity-monitor') return <ActivityMonitorPage events={events} />
    if (page === 'student-timeline') return <StudentTimelinePage latestState={latestState} />
    if (page === 'alerts-center') return <AlertsCenterPage alerts={alerts} />
    return <DashboardPage latestState={latestState} />
  }, [alerts, events, latestState, page])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 lg:flex">
      <Sidebar page={page} onPageChange={setPage} />
      <div className="flex-1">
        <Topbar connected={connected} />
        <main className="p-6 space-y-4">
          <PlannerConsole onAnalyzed={setLatestState} loading={loading} setLoading={setLoading} />
          {pageNode}
        </main>
      </div>
    </div>
  )
}
