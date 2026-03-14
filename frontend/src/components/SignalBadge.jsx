export default function SignalBadge({ signal }) {
  const config = {
    overbought:    { label: 'OVERBOUGHT',    bg: 'bg-red-900',    text: 'text-red-300',    border: 'border-red-700' },
    oversold:      { label: 'OVERSOLD',      bg: 'bg-green-900',  text: 'text-green-300',  border: 'border-green-700' },
    trending_up:   { label: 'TRENDING ↑',    bg: 'bg-blue-900',   text: 'text-blue-300',   border: 'border-blue-700' },
    trending_down: { label: 'TRENDING ↓',    bg: 'bg-orange-900', text: 'text-orange-300', border: 'border-orange-700' },
    neutral:       { label: 'NEUTRAL',       bg: 'bg-gray-800',   text: 'text-gray-300',   border: 'border-gray-600' },
  }
  const c = config[signal] || config.neutral
  return (
    <span className={`text-xs font-bold px-2 py-0.5 rounded border ${c.bg} ${c.text} ${c.border}`}>
      {c.label}
    </span>
  )
}
