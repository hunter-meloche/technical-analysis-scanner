import {
  ResponsiveContainer,
  ComposedChart,
  LineChart,
  BarChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
} from 'recharts'
import SignalBadge from './SignalBadge.jsx'

const fmt = (v) => (v == null ? '—' : Number(v).toFixed(2))

const GRID = { strokeDasharray: '3 3', stroke: '#374151' }
const X_TICK = { fontSize: 10, fill: '#9ca3af' }
const Y_TICK = { fontSize: 10, fill: '#9ca3af' }
const TOOLTIP_STYLE = { backgroundColor: '#1f2937', border: '1px solid #374151', fontSize: 12 }
const fmtDate = (d) => d?.slice(5)

function ChartSection({ title, height, children }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-2">{title}</h3>
      <div className="bg-gray-900 rounded-xl border border-gray-700 p-3">
        <ResponsiveContainer width="100%" height={height}>
          {children}
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default function DetailPanel({ symbol, data }) {
  if (!data) {
    return (
      <div className="flex items-center justify-center h-full text-gray-600 text-lg">
        Select a ticker to view details
      </div>
    )
  }

  const history = data.history || []

  return (
    <div className="space-y-6 overflow-y-auto h-full pr-2">
      {/* Header */}
      <div className="flex items-center gap-4">
        <h2 className="text-3xl font-bold text-white">{symbol}</h2>
        <span className="text-3xl font-mono text-indigo-300">${fmt(data.last_price)}</span>
        <SignalBadge signal={data.signal} />
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: 'RSI (14)', value: fmt(data.rsi) },
          { label: 'SMA 20', value: fmt(data.sma_20) },
          { label: 'SMA 50', value: fmt(data.sma_50) },
          { label: 'MACD', value: fmt(data.macd) },
          { label: 'BB Upper', value: fmt(data.bb_upper) },
          { label: 'BB Lower', value: fmt(data.bb_lower) },
          { label: 'MACD Signal', value: fmt(data.macd_signal) },
          { label: 'BB Width', value: data.bb_upper && data.bb_lower ? fmt(data.bb_upper - data.bb_lower) : '—' },
        ].map(({ label, value }) => (
          <div key={label} className="bg-gray-900 rounded-lg p-3 border border-gray-700">
            <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</div>
            <div className="font-mono text-sm text-gray-200">{value}</div>
          </div>
        ))}
      </div>

      <ChartSection title="Price + Moving Averages" height={220}>
        <ComposedChart data={history}>
          <CartesianGrid {...GRID} />
          <XAxis dataKey="date" tick={X_TICK} tickFormatter={fmtDate} interval="preserveStartEnd" />
          <YAxis tick={Y_TICK} domain={['auto', 'auto']} />
          <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v) => v?.toFixed(2)} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Line type="monotone" dataKey="close" stroke="#818cf8" dot={false} strokeWidth={2} name="Close" />
          <Line type="monotone" dataKey="sma_20" stroke="#34d399" dot={false} strokeWidth={1.5} strokeDasharray="4 2" name="SMA 20" />
          <Line type="monotone" dataKey="sma_50" stroke="#f59e0b" dot={false} strokeWidth={1.5} strokeDasharray="4 2" name="SMA 50" />
          <Line type="monotone" dataKey="bb_upper" stroke="#6b7280" dot={false} strokeWidth={1} name="BB Upper" />
          <Line type="monotone" dataKey="bb_lower" stroke="#6b7280" dot={false} strokeWidth={1} name="BB Lower" />
        </ComposedChart>
      </ChartSection>

      <ChartSection title="RSI (14)" height={140}>
        <LineChart data={history}>
          <CartesianGrid {...GRID} />
          <XAxis dataKey="date" tick={X_TICK} tickFormatter={fmtDate} interval="preserveStartEnd" />
          <YAxis domain={[0, 100]} tick={Y_TICK} ticks={[0, 30, 50, 70, 100]} />
          <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v) => v?.toFixed(1)} />
          <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="4 2" label={{ value: '70', fill: '#ef4444', fontSize: 10 }} />
          <ReferenceLine y={30} stroke="#22c55e" strokeDasharray="4 2" label={{ value: '30', fill: '#22c55e', fontSize: 10 }} />
          <Line type="monotone" dataKey="rsi" stroke="#a78bfa" dot={false} strokeWidth={2} name="RSI" />
        </LineChart>
      </ChartSection>

      <ChartSection title="MACD" height={140}>
        <ComposedChart data={history}>
          <CartesianGrid {...GRID} />
          <XAxis dataKey="date" tick={X_TICK} tickFormatter={fmtDate} interval="preserveStartEnd" />
          <YAxis tick={Y_TICK} domain={['auto', 'auto']} />
          <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v) => v?.toFixed(4)} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <ReferenceLine y={0} stroke="#4b5563" />
          <Bar dataKey="macd" fill="#374151" name="Histogram" opacity={0.6} />
          <Line type="monotone" dataKey="macd" stroke="#60a5fa" dot={false} strokeWidth={2} name="MACD" />
          <Line type="monotone" dataKey="macd_signal" stroke="#f97316" dot={false} strokeWidth={2} name="Signal" />
        </ComposedChart>
      </ChartSection>

      <ChartSection title="Volume" height={100}>
        <BarChart data={history}>
          <CartesianGrid {...GRID} />
          <XAxis dataKey="date" tick={X_TICK} tickFormatter={fmtDate} interval="preserveStartEnd" />
          <YAxis tick={Y_TICK} tickFormatter={(v) => `${(v / 1e6).toFixed(0)}M`} />
          <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v) => `${(v / 1e6).toFixed(1)}M`} />
          <Bar dataKey="volume" fill="#4b5563" name="Volume" />
        </BarChart>
      </ChartSection>
    </div>
  )
}
