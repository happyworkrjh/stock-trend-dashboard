import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

// 股票数据API
export const fetchStockInfo = (symbol) => api.get(`/stock/${symbol}`)
export const fetchStockHistory = (symbol, period = '1y') => api.get(`/stock/${symbol}/history?period=${period}`)
export const fetchRealtimePrice = (symbol) => api.get(`/stock/${symbol}/realtime`)

// 分析API
export const fetchIndicators = (symbol) => api.get(`/analysis/${symbol}/indicators`)
export const fetchSignals = (symbol) => api.get(`/analysis/${symbol}/signals`)
export const fetchDetailedAnalysis = (symbol) => api.get(`/analysis/${symbol}/detailed`)

// 仪表盘API
export const fetchDashboardSignals = (symbols) => api.post('/dashboard/signals', { symbols })
export const fetchBatchStocks = (symbols) => api.post('/stocks/batch', { symbols })

export default api
