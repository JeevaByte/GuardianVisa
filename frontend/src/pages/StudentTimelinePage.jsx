import TimelineList from '../components/ui/TimelineList'

export default function StudentTimelinePage({ latestState }) {
  return (
    <div className="p-4 rounded-xl border border-slate-800 bg-slate-900">
      <h2 className="text-lg font-semibold text-white mb-3">Student Timeline</h2>
      <TimelineList items={latestState?.timeline || []} />
    </div>
  )
}

