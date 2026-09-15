import Dashboard from './components/Dashboard'
import './index.css'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <header className="mb-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">📈 美股趋势分析</h1>
          <p className="text-gray-600">实时行情 · 技术分析 · 智能信号</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto">
        <Dashboard />
      </main>

      <footer className="mt-12 text-center text-gray-500 text-sm">
        <p>数据延迟约15-20分钟 | 仅供学习研究使用 | 交易风险自负</p>
      </footer>
    </div>
  )
}

export default App
