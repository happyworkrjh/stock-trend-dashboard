"""
股票数据获取模块
使用yfinance获取实时和历史股票数据
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StockDataFetcher:
    """股票数据获取器"""
    
    def __init__(self, period: str = '1y', interval: str = '1d'):
        """
        初始化数据获取器
        
        Args:
            period: 数据周期 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: 数据间隔 (1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
        """
        self.period = period
        self.interval = interval
        self.cache = {}
        
    def fetch_historical_data(self, symbol: str, period: Optional[str] = None) -> pd.DataFrame:
        """
        获取历史数据
        
        Args:
            symbol: 股票代码 (如 'AAPL')
            period: 数据周期，默认使用初始化设置
            
        Returns:
            包含OHLCV数据的DataFrame
        """
        try:
            period = period or self.period
            logger.info(f"Fetching historical data for {symbol} ({period})")
            
            data = yf.download(symbol, period=period, interval='1d', progress=False)
            
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            
            # 重命名列为小写
            data.columns = [col.lower() for col in data.columns]
            
            # 添加缓存
            self.cache[f"{symbol}_hist"] = {
                'data': data,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Successfully fetched {len(data)} records for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def fetch_intraday_data(self, symbol: str, interval: str = '1h') -> pd.DataFrame:
        """
        获取日内数据（最近5天）
        
        Args:
            symbol: 股票代码
            interval: 时间间隔 (1m, 5m, 15m, 30m, 60m)
            
        Returns:
            包含OHLCV数据的DataFrame
        """
        try:
            logger.info(f"Fetching intraday data for {symbol} ({interval})")
            
            data = yf.download(symbol, period='5d', interval=interval, progress=False)
            
            if data.empty:
                logger.warning(f"No intraday data found for {symbol}")
                return pd.DataFrame()
            
            data.columns = [col.lower() for col in data.columns]
            
            self.cache[f"{symbol}_intraday"] = {
                'data': data,
                'timestamp': datetime.now()
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def fetch_realtime_price(self, symbol: str) -> Dict:
        """
        获取实时价格数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            包含价格、涨跌幅等信息的字典
        """
        try:
            logger.info(f"Fetching real-time price for {symbol}")
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            
            if data.empty:
                logger.warning(f"No real-time data found for {symbol}")
                return {}
            
            latest = data.iloc[-1]
            info = ticker.info
            
            return {
                'symbol': symbol,
                'price': float(latest['Close']),
                'open': float(latest['Open']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'volume': int(latest['Volume']),
                'previous_close': float(info.get('previousClose', 0)),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', None),
                'dividend_yield': info.get('dividendYield', None),
                'currency': info.get('currency', 'USD'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching real-time price for {symbol}: {str(e)}")
            return {}
    
    def fetch_multiple_stocks(self, symbols: list) -> Dict[str, Dict]:
        """
        批量获取多个股票的实时数据
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            包含各股票数据的字典
        """
        results = {}
        for symbol in symbols:
            results[symbol] = self.fetch_realtime_price(symbol)
        return results
    
    def fetch_stock_info(self, symbol: str) -> Dict:
        """
        获取股票基本信息
        
        Args:
            symbol: 股票代码
            
        Returns:
            包含公司基本信息的字典
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'website': info.get('website', ''),
                'description': info.get('longBusinessSummary', ''),
                'market_cap': info.get('marketCap', 0),
                'employees': info.get('fullTimeEmployees', 0),
                'founded': info.get('founded', ''),
                'exchange': info.get('exchange', ''),
                '52_week_high': info.get('fiftyTwoWeekHigh', None),
                '52_week_low': info.get('fiftyTwoWeekLow', None),
                'dividend_yield': info.get('dividendYield', None),
                'pe_ratio': info.get('trailingPE', None),
                'earnings_date': info.get('nextEarningsDate', None),
            }
            
        except Exception as e:
            logger.error(f"Error fetching stock info for {symbol}: {str(e)}")
            return {}
    
    def is_market_open(self) -> bool:
        """
        检查美股市场是否开盘
        
        Returns:
            市场是否开盘
        """
        now = datetime.now()
        # 美股交易时间: 周一至周五 09:30-16:00 EST
        weekday = now.weekday()
        hour = now.hour
        
        # 检查是否是工作日（周一=0, 周五=4）
        if weekday > 4:
            return False
        
        # EST时间检查（UTC-5）
        # 这里假设服务器在EST时区
        if 9 <= hour < 16:
            return True
        
        return False
    
    def clear_cache(self, symbol: Optional[str] = None):
        """
        清除缓存
        
        Args:
            symbol: 如果指定，只清除该股票的缓存
        """
        if symbol:
            keys_to_delete = [k for k in self.cache.keys() if symbol in k]
            for key in keys_to_delete:
                del self.cache[key]
        else:
            self.cache.clear()


# 全局实例
_fetcher_instance = None

def get_fetcher(period: str = '1y', interval: str = '1d') -> StockDataFetcher:
    """获取全局数据获取器实例"""
    global _fetcher_instance
    if _fetcher_instance is None:
        _fetcher_instance = StockDataFetcher(period, interval)
    return _fetcher_instance
