import { useState, useEffect } from 'react'
import { fetchDashboardSignals, fetchBatchStocks } from '../services/api'
import MetricsCard from './MetricsCard'
import SignalAlert from './SignalAlert'

const WATCH_STOCKS = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN']

export default function Dashboard() {
  const [stocks, setStocks] = useState({})
  const [signals, setSignals] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 60000) // 每分钟刷新
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [stocksRes, signalsRes] = await Promise.all([
        fetchBatchStocks(WATCH_STOCKS),
        fetchDashboardSignals(WATCH_STOCKS)
      ])
      
      setStocks(stocksRes.data.data || {})
      setSignals(signalsRes.data.stocks || [])
      setError(null)
    } catch (err) {
      setError('数据加载失败: ' + err.message)
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">📊</div>
          <p className="text-gray-500">正在加载数据...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded text-red-700">
        {error}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 股票价格卡片网格 */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {WATCH_STOCKS.map(symbol => {
          const stock = stocks[symbol]
          if (!stock) return null
          
          const trend = ((stock.price - stock.previous_close) / stock.previous_close) * 100
          
          return (
            <MetricsCard
              key={symbol}
              title={symbol}
              value={stock.price?.toFixed(2)}
              unit="USD"
              trend={trend}
              color={trend > 0 ? 'green' : trend < 0 ? 'red' : 'blue'}
            />
          )
        })}
      </div>

      {/* 交易信号部分 */}
      <div className="space-y-3">
        <h2 className="text-2xl font-bold text-gray-800">交易信号</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {signals.map(signal => (
            <SignalAlert
              key={signal.symbol}
              signal={signal.overall_signal}
              confidence={signal.confidence}
              recommendation={signal.recommendation}
            />
          ))}
        </div>
      </div>

      {/* 指标详情表格 */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 border-b">
            <tr>
              <th className="px-4 py-2 text-left">股票</th>
              <th className="px-4 py-2 text-right">价格</th>
              <th className="px-4 py-2 text-right">RSI</th>
              <th className="px-4 py-2 text-right">MACD</th>
              <th className="px-4 py-2 text-right">信号</th>
            </tr>
          </thead>
          <tbody>
            {signals.map(signal => (
              <tr key={signal.symbol} className="border-b hover:bg-gray-50">
                <td className="px-4 py-2 font-semibold">{signal.symbol}</td>
                <td className="px-4 py-2 text-right">${signal.current_price?.toFixed(2)}</td>
                <td className="px-4 py-2 text-right">
                  {signal.indicators?.rsi?.toFixed(2) || '-'}
                </td>
                <td className="px-4 py-2 text-right">
                  {signal.indicators?.macd?.toFixed(4) || '-'}
                </td>
                <td className={`px-4 py-2 text-right font-bold ${
                  signal.overall_signal.includes('BUY') ? 'text-green-600' :
                  signal.overall_signal.includes('SELL') ? 'text-red-600' :
                  'text-yellow-600'
                }`}>
                  {signal.overall_signal}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
