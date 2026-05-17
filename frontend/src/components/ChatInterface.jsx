import { useState } from 'react'
import axios from 'axios'

const PLACEHOLDERS = {
  visa: 'Paste your manager\'s message here...\n\nE.g. "Hey Priya, can you do an extra 8-hour shift this Saturday? We\'re short-staffed."',
  scam: 'Paste the rental listing or landlord message here...\n\nE.g. "Room available in Fitzroy $180/week. Owner is overseas. Pay 3 months upfront via bank transfer."',
  emergency: 'Describe your situation...\n\nE.g. "I just lost my job at the café and I\'m not sure if that affects my visa. I also have rent due next week."',
}

const ENDPOINTS = {
  visa: '/api/analyse/visa-risk',
  scam: '/api/analyse/scam',
  emergency: '/api/analyse/emergency',
}

const MODE_LABELS = {
  visa: { title: 'Visa Guard', subtitle: 'Check if a work request puts your visa at risk' },
  scam: { title: 'Scam Scanner', subtitle: 'Detect rental and housing scams targeting students' },
  emergency: { title: 'Emergency Plan', subtitle: 'Get a step-by-step action plan for your situation' },
}

export default function ChatInterface({ mode, onResult, onLoading, loading }) {
  const [text, setText] = useState('')
  const [error, setError] = useState(null)

  const handleSubmit = async () => {
    if (!text.trim()) return
    setError(null)
    onLoading(true)
    onResult(null)

    try {
      const payload =
        mode === 'visa'
          ? { message: text, student_id: 'priya_sharma_demo' }
          : mode === 'scam'
          ? { listing_text: text, student_id: 'priya_sharma_demo' }
          : { situation: text, student_id: 'priya_sharma_demo' }

      const { data } = await axios.post(ENDPOINTS[mode], payload)
      onResult(data)
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        'Backend unreachable. Check the server is running on :8000.'
      setError(msg)
    } finally {
      onLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSubmit()
    }
  }

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-5 shadow-xl space-y-4">
      <div>
        <h3 className="font-bold text-white text-base">{MODE_LABELS[mode].title}</h3>
        <p className="text-slate-400 text-sm">{MODE_LABELS[mode].subtitle}</p>
      </div>

      <textarea
        className="w-full bg-slate-900 border border-slate-600 rounded-lg p-4 text-slate-200 text-sm
          placeholder-slate-500 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500
          focus:border-blue-500 transition-all min-h-[120px]"
        placeholder={PLACEHOLDERS[mode]}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={loading}
        rows={5}
      />

      <div className="flex items-center justify-between gap-3">
        <p className="text-xs text-slate-500">⌘ + Enter to analyse</p>
        <button
          onClick={handleSubmit}
          disabled={loading || !text.trim()}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-semibold text-sm transition-all duration-200 ${
            loading || !text.trim()
              ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/40 active:scale-95'
          }`}
        >
          {loading ? (
            <>
              <span className="w-4 h-4 border-2 border-slate-400 border-t-white rounded-full animate-spin" />
              Agent is thinking...
            </>
          ) : (
            <>Analyse Risk →</>
          )}
        </button>
      </div>

      {error && (
        <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg p-3 text-sm flex gap-2">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}
