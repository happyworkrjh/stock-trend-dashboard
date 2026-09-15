export default function SignalAlert({ signal, confidence, recommendation }) {
  const signalColors = {
    'STRONG_BUY': 'bg-green-100 border-green-500 text-green-800',
    'BUY': 'bg-green-50 border-green-400 text-green-700',
    'HOLD': 'bg-yellow-50 border-yellow-400 text-yellow-700',
    'SELL': 'bg-red-50 border-red-400 text-red-700',
    'STRONG_SELL': 'bg-red-100 border-red-500 text-red-800',
  }

  const signalIcons = {
    'STRONG_BUY': '🟢🟢',
    'BUY': '🟢',
    'HOLD': '🟡',
    'SELL': '🔴',
    'STRONG_SELL': '🔴🔴',
  }

  return (
    <div className={`border-l-4 p-4 rounded ${signalColors[signal] || 'bg-gray-50'}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{signalIcons[signal]}</span>
          <div>
            <h3 className="font-bold text-lg">{signal}</h3>
            <p className="text-sm opacity-75 mt-1">{recommendation}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm font-semibold">信心度</p>
          <p className="text-xl font-bold">{confidence.toFixed(0)}%</p>
        </div>
      </div>
    </div>
  )
}
