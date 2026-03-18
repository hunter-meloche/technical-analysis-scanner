import { useState, useEffect, useCallback } from 'react'
import TickerCard from './components/TickerCard.jsx'
import DetailPanel from './components/DetailPanel.jsx'

const API_BASE = import.meta.env.BASE_URL + 'api'

export default function App() {
  const [tickers, setTickers] = useState([])
  const [tickerData, setTickerData] = useState({})
  const [loadingSet, setLoadingSet] = useState(new Set())
  const [selectedTicker, setSelectedTicker] = useState(null)
  const [filter, setFilter] = useState('all')

  // Derived — never store separately to avoid stale/redundant state
  const selectedData = selectedTicker ? tickerData[selectedTicker] ?? null : null
  const loadingDetail = selectedTicker ? loadingSet.has(selectedTicker) : false

  useEffect(() => {
    fetch(`${API_BASE}/tickers`)
      .then((r) => r.json())
      .then((list) => {
        setTickers(list)
        // Batch all loading states at once — one render, not 20
        setLoadingSet(new Set(list))
        list.forEach((sym) => loadSummary(sym))
      })
      .catch(console.error)
  }, [])

  const loadSummary = useCallback((symbol) => {
    fetch(`${API_BASE}/ticker/${symbol}/indicators`)
      .then((r) => r.ok ? r.json() : null)
      .then((data) => {
        setTickerData((prev) => ({ ...prev, [symbol]: data }))
        setLoadingSet((prev) => { const s = new Set(prev); s.delete(symbol); return s })
      })
      .catch(() => setLoadingSet((prev) => { const s = new Set(prev); s.delete(symbol); return s }))
  }, [])

  const handleSelectTicker = (symbol) => {
    setSelectedTicker(symbol)
    // If not yet loaded and not already in flight, fetch now
    if (!tickerData[symbol] && !loadingSet.has(symbol)) {
      setLoadingSet((prev) => new Set([...prev, symbol]))
      loadSummary(symbol)
    }
  }

  const SIGNALS = ['all', 'overbought', 'oversold', 'trending_up', 'trending_down', 'neutral']

  const filteredTickers = tickers.filter((sym) => {
    if (filter === 'all') return true
    const d = tickerData[sym]
    return d?.signal === filter
  })

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-screen-2xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">
              📈 Technical Analysis Scanner
            </h1>
            <p className="text-xs text-gray-500 mt-0.5">SMA · RSI · MACD · Bollinger Bands</p>
          </div>
          {/* Filter pills */}
          <div className="flex gap-2 flex-wrap">
            {SIGNALS.map((s) => (
              <button
                key={s}
                onClick={() => setFilter(s)}
                className={`text-xs px-3 py-1 rounded-full border transition-colors ${
                  filter === s
                    ? 'bg-indigo-700 border-indigo-500 text-white'
                    : 'bg-gray-900 border-gray-700 text-gray-400 hover:border-gray-500'
                }`}
              >
                {s === 'all' ? 'All' : s.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Body */}
      <div className="flex-1 max-w-screen-2xl mx-auto w-full flex gap-0 overflow-hidden" style={{ height: 'calc(100vh - 72px)' }}>
        {/* Left: Ticker Grid */}
        <div className="w-80 flex-shrink-0 border-r border-gray-800 overflow-y-auto p-4">
          <div className="text-xs text-gray-500 mb-3 uppercase tracking-wide">
            {filteredTickers.length} ticker{filteredTickers.length !== 1 ? 's' : ''}
          </div>
          <div className="space-y-2">
            {filteredTickers.map((sym) => (
              <TickerCard
                key={sym}
                symbol={sym}
                data={tickerData[sym]}
                loading={loadingSet.has(sym)}
                selected={selectedTicker === sym}
                onClick={() => handleSelectTicker(sym)}
              />
            ))}
          </div>
        </div>

        {/* Right: Detail Panel */}
        <div className="flex-1 p-6 overflow-hidden">
          {loadingDetail ? (
            <div className="flex items-center justify-center h-full text-gray-500 animate-pulse text-lg">
              Loading {selectedTicker}…
            </div>
          ) : (
            <DetailPanel symbol={selectedTicker} data={selectedData} />
          )}
        </div>
      </div>
    </div>
  )
}
