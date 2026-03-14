import SignalBadge from './SignalBadge.jsx'

export default function TickerCard({ symbol, data, loading, selected, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-4 rounded-xl border transition-all duration-150 cursor-pointer ${
        selected
          ? 'bg-indigo-900/40 border-indigo-500'
          : 'bg-gray-900 border-gray-700 hover:border-gray-500 hover:bg-gray-800'
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="font-bold text-white text-base">{symbol}</span>
        {data && <SignalBadge signal={data.signal} />}
      </div>
      {loading && <div className="text-gray-500 text-xs animate-pulse">Loading…</div>}
      {!loading && data && (
        <div className="space-y-1">
          <div className="text-2xl font-mono text-white">${data.last_price?.toFixed(2) ?? '—'}</div>
          <div className="flex gap-3 text-xs text-gray-400">
            <span>RSI <span className={`font-semibold ${data.rsi >= 70 ? 'text-red-400' : data.rsi <= 30 ? 'text-green-400' : 'text-gray-300'}`}>{data.rsi?.toFixed(1) ?? '—'}</span></span>
            <span>SMA20 <span className="text-gray-300">{data.sma_20?.toFixed(2) ?? '—'}</span></span>
          </div>
        </div>
      )}
      {!loading && !data && (
        <div className="text-gray-600 text-xs">No data</div>
      )}
    </button>
  )
}
