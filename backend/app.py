"""
美股趋势分析仪表盘 - Flask应用
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from config import get_config
from data_fetcher import StockDataFetcher
from analyzer import StockAnalyzer
from signals import SignalGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
config = get_config()

# 配置CORS
CORS(app, resources={r"/api/*": {"origins": config.CORS_ORIGINS}})

# 错误处理
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

# ==================== 基础API ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'service': 'stock-trend-dashboard',
        'version': '1.0.0'
    })

# ==================== 股票数据API ====================

@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    """
    获取股票基本信息
    
    Args:
        symbol: 股票代码
    
    Returns:
        股票信息JSON
    """
    try:
        symbol = symbol.upper()
        fetcher = StockDataFetcher()
        info = fetcher.fetch_stock_info(symbol)
        
        if not info:
            return jsonify({'error': f'Stock {symbol} not found'}), 404
        
        # 添加实时价格
        price_data = fetcher.fetch_realtime_price(symbol)
        info.update(price_data)
        
        return jsonify(info)
    except Exception as e:
        logger.error(f"Error fetching stock info for {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<symbol>/realtime', methods=['GET'])
def get_realtime_price(symbol):
    """
    获取实时价格
    
    Args:
        symbol: 股票代码
    
    Returns:
        实时价格JSON
    """
    try:
        symbol = symbol.upper()
        fetcher = StockDataFetcher()
        data = fetcher.fetch_realtime_price(symbol)
        
        if not data:
            return jsonify({'error': f'Stock {symbol} not found'}), 404
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching realtime price for {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<symbol>/history', methods=['GET'])
def get_stock_history(symbol):
    """
    获取历史数据
    
    Args:
        symbol: 股票代码
        period: 数据周期（可选，默认1y）
    
    Returns:
        历史数据JSON
    """
    try:
        symbol = symbol.upper()
        period = request.args.get('period', '1y')
        
        fetcher = StockDataFetcher(period=period)
        data = fetcher.fetch_historical_data(symbol)
        
        if data.empty:
            return jsonify({'error': f'No history data found for {symbol}'}), 404
        
        # 转换为JSON格式
        result = {
            'symbol': symbol,
            'period': period,
            'data': []
        }
        
        for idx, row in data.iterrows():
            result['data'].append({
                'date': idx.strftime('%Y-%m-%d'),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(row['volume'])
            })
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error fetching history for {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== 技术分析API ====================

@app.route('/api/analysis/<symbol>/indicators', methods=['GET'])
def get_indicators(symbol):
    """
    获取技术指标
    
    Args:
        symbol: 股票代码
    
    Returns:
        技术指标JSON
    """
    try:
        symbol = symbol.upper()
        analyzer = StockAnalyzer(symbol)
        
        latest = analyzer.get_latest_indicators()
        
        if not latest:
            return jsonify({'error': f'No data found for {symbol}'}), 404
        
        return jsonify(latest)
    except Exception as e:
        logger.error(f"Error fetching indicators for {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/<symbol>/signals', methods=['GET'])
def get_signals(symbol):
    """
    获取交易信号
    
    Args:
        symbol: 股票代码
    
    Returns:
        交易信号JSON
    """
    try:
        symbol = symbol.upper()
        generator = SignalGenerator(symbol)
        signals = generator.generate_comprehensive_signals()
        
        if 'error' in signals:
            return jsonify(signals), 404
        
        return jsonify(signals)
    except Exception as e:
        logger.error(f"Error generating signals for {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/<symbol>/detailed', methods=['GET'])
def get_detailed_analysis(symbol):
    """
    获取详细分析（包含历史数据、指标和信号）
    
    Args:
        symbol: 股票代码
    
    Returns:
        详细分析JSON
    """
    try:
        symbol = symbol.upper()
        
        # 获取基本信息
        fetcher = StockDataFetcher()
        info = fetcher.fetch_stock_info(symbol)
        price = fetcher.fetch_realtime_price(symbol)
        
        # 获取指标
        analyzer = StockAnalyzer(symbol)
        indicators = analyzer.get_latest_indicators()
        
        # 获取信号
        generator = SignalGenerator(symbol)
        signals = generator.generate_comprehensive_signals()
        
        result = {
            'symbol': symbol,
            'info': info,
            'price': price,
            'indicators': indicators,
            'signals': signals
        }
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error fetching detailed analysis for {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== 批量API ====================

@app.route('/api/stocks/batch', methods=['POST'])
def get_stocks_batch():
    """
    批量获取多个股票的实时数据
    
    Request Body:
        {
            "symbols": ["AAPL", "MSFT", "TSLA"]
        }
    
    Returns:
        多个股票的数据JSON
    """
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': 'symbols list is required'}), 400
        
        fetcher = StockDataFetcher()
        results = {}
        
        for symbol in symbols:
            symbol = symbol.upper()
            results[symbol] = fetcher.fetch_realtime_price(symbol)
        
        return jsonify({'data': results})
    except Exception as e:
        logger.error(f"Error fetching batch stocks: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/signals', methods=['POST'])
def get_dashboard_signals():
    """
    获取仪表盘信号（多个股票）
    
    Request Body:
        {
            "symbols": ["AAPL", "MSFT", "TSLA"]
        }
    
    Returns:
        多个股票的信号JSON
    """
    try:
        data = request.get_json()
        symbols = data.get('symbols', config.STOCKS_WATCH)
        
        results = []
        for symbol in symbols:
            try:
                generator = SignalGenerator(symbol.upper())
                signals = generator.generate_comprehensive_signals()
                if 'error' not in signals:
                    results.append(signals)
            except Exception as e:
                logger.error(f"Error processing {symbol}: {str(e)}")
                continue
        
        return jsonify({
            'timestamp': results[0]['timestamp'] if results else None,
            'stocks': results,
            'count': len(results)
        })
    except Exception as e:
        logger.error(f"Error fetching dashboard signals: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== 配置API ====================

@app.route('/api/config/stocks', methods=['GET'])
def get_watched_stocks():
    """获取监控的股票列表"""
    return jsonify({
        'stocks': config.STOCKS_WATCH,
        'update_interval': config.UPDATE_INTERVAL
    })

@app.route('/api/config/indicators', methods=['GET'])
def get_indicator_config():
    """获取指标配置"""
    return jsonify(config.INDICATORS)

# ==================== 主函数 ====================

if __name__ == '__main__':
    logger.info(f"Starting Stock Trend Dashboard Server")
    logger.info(f"Environment: {config.FLASK_ENV}")
    logger.info(f"Debug Mode: {config.DEBUG}")
    logger.info(f"Watched Stocks: {', '.join(config.STOCKS_WATCH)}")
    
    app.run(
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.DEBUG
    )
