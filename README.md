# 🚀 美股趋势分析仪表盘

一个功能完整的美股趋势分析和交易建议系统，提供实时数据、技术指标、峰值/低谷预判和简洁的Web仪表盘。

## ✨ 功能特性

- 📊 **实时股票数据** - 自动获取美股最新价格
- 📈 **技术指标分析** - MACD、RSI、移动平均线、布林带等
- 🎯 **峰值/低谷检测** - 自动识别关键支撑位和阻力位
- 💡 **购买建议** - 基于多个指标的智能交易信号
- 🎨 **简洁仪表盘UI** - 实时图表、指标卡片、信号提示
- 🔄 **自动更新** - 每日/每小时自动刷新数据

## 🛠️ 技术栈

### 后端
- **Python 3.9+**
- **Flask** - Web框架
- **pandas** - 数据处理
- **numpy** - 数值计算
- **yfinance** - 股票数据获取
- **ta-lib** 或 **TA** - 技术指标计算

### 前端
- **React 18+** - UI框架
- **Chart.js** 或 **Plotly.js** - 图表库
- **Tailwind CSS** - 样式框架
- **Axios** - HTTP请求

## 📁 项目结构

```
stock-trend-dashboard/
├── backend/
│   ├── app.py                 # Flask应用主入口
│   ├── config.py              # 配置文件
│   ├── data_fetcher.py        # 数据获取模块
│   ├── analyzer.py            # 技术分析模块
│   ├── signals.py             # 交易信号生成
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🚀 快速开始

### 后端安装

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

### 前端安装

```bash
cd frontend
npm install
npm run dev
```

## 📊 技术指标

| 指标 | 说明 |
|------|------|
| **MA** | 移动平均线 |
| **RSI** | 相对强弱指数 |
| **MACD** | 异同移动平均线 |
| **BB** | 布林带 |

## 📄 许可证

MIT License

---

**免责声明**: 本项目仅供学习和研究使用，不构成投资建议。
