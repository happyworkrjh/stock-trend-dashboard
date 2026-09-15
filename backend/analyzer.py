"""
技术分析模块
计算各种技术指标：MA、RSI、MACD、布林带等
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging
from data_fetcher import StockDataFetcher
from config import get_config

logger = logging.getLogger(__name__)
config = get_config()

class StockAnalyzer:
    """股票技术分析器"""
    
    def __init__(self, symbol: str):
        """
        初始化分析器
        
        Args:
            symbol: 股票代码
        """
        self.symbol = symbol
        self.fetcher = StockDataFetcher(config.CHART_PERIOD)
        self.data = None
        self.indicators = {}
        
    def load_data(self) -> pd.DataFrame:
        """加载股票历史数据"""
        self.data = self.fetcher.fetch_historical_data(self.symbol)
        return self.data
    
    def calculate_moving_averages(self) -> Dict[str, pd.Series]:
        """
        计算移动平均线
        
        Returns:
            包含SMA和EMA的字典
        """
        if self.data is None or self.data.empty:
            self.load_data()
        
        close = self.data['close']
        
        indicators = {
            'sma_20': close.rolling(window=20).mean(),
            'sma_50': close.rolling(window=50).mean(),
            'sma_200': close.rolling(window=200).mean(),
            'ema_12': close.ewm(span=12, adjust=False).mean(),
            'ema_26': close.ewm(span=26, adjust=False).mean(),
        }
        
        self.indicators['moving_averages'] = indicators
        logger.info(f"Calculated moving averages for {self.symbol}")
        
        return indicators
    
    def calculate_rsi(self, period: int = 14) -> pd.Series:
        """
        计算RSI（相对强弱指数）
        
        Args:
            period: 周期，默认14
            
        Returns:
            RSI序列
        """
        if self.data is None or self.data.empty:
            self.load_data()
        
        close = self.data['close']
        delta = close.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        self.indicators['rsi'] = rsi
        logger.info(f"Calculated RSI for {self.symbol}")
        
        return rsi
    
    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """
        计算MACD（异同移动平均线）
        
        Args:
            fast: 快线周期，默认12
            slow: 慢线周期，默认26
            signal: 信号线周期，默认9
            
        Returns:
            包含MACD、信号线和直方图的字典
        """
        if self.data is None or self.data.empty:
            self.load_data()
        
        close = self.data['close']
        
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        indicators = {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
        
        self.indicators['macd'] = indicators
        logger.info(f"Calculated MACD for {self.symbol}")
        
        return indicators
    
    def calculate_bollinger_bands(self, period: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """
        计算布林带
        
        Args:
            period: 周期，默认20
            std_dev: 标准差倍数，默认2
            
        Returns:
            包含上轨、中轨、下轨的字典
        """
        if self.data is None or self.data.empty:
            self.load_data()
        
        close = self.data['close']
        
        sma = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        
        indicators = {
            'middle': sma,
            'upper': sma + (std * std_dev),
            'lower': sma - (std * std_dev),
            'bandwidth': (2 * std * std_dev) / sma,  # 带宽百分比
        }
        
        self.indicators['bollinger_bands'] = indicators
        logger.info(f"Calculated Bollinger Bands for {self.symbol}")
        
        return indicators
    
    def detect_peaks_and_valleys(self, window: int = 5) -> Dict[str, list]:
        """
        检测峰值和低谷
        
        Args:
            window: 窗口大小，默认5
            
        Returns:
            包含峰值和低谷位置及价格的字典
        """
        if self.data is None or self.data.empty:
            self.load_data()
        
        close = self.data['close'].values
        
        peaks = []
        valleys = []
        
        for i in range(window, len(close) - window):
            # 检测峰值
            if close[i] == max(close[i-window:i+window+1]):
                peaks.append({
                    'index': i,
                    'date': str(self.data.index[i].date()),
                    'price': float(close[i])
                })
            
            # 检测低谷
            if close[i] == min(close[i-window:i+window+1]):
                valleys.append({
                    'index': i,
                    'date': str(self.data.index[i].date()),
                    'price': float(close[i])
                })
        
        # 只保留最近的10个峰值和低谷
        peaks = peaks[-10:] if peaks else []
        valleys = valleys[-10:] if valleys else []
        
        indicators = {
            'peaks': peaks,
            'valleys': valleys,
            'recent_high': float(close[-20:].max()) if len(close) > 20 else float(close[-1]),
            'recent_low': float(close[-20:].min()) if len(close) > 20 else float(close[-1]),
        }
        
        self.indicators['peaks_valleys'] = indicators
        logger.info(f"Detected peaks and valleys for {self.symbol}")
        
        return indicators
    
    def calculate_all_indicators(self) -> Dict:
        """
        计算所有技术指标
        
        Returns:
            包含所有指标的字典
        """
        if self.data is None:
            self.load_data()
        
        if self.data.empty:
            logger.error(f"No data available for {self.symbol}")
            return {}
        
        self.calculate_moving_averages()
        self.calculate_rsi()
        self.calculate_macd()
        self.calculate_bollinger_bands()
        self.detect_peaks_and_valleys()
        
        logger.info(f"Calculated all indicators for {self.symbol}")
        
        return self.indicators
    
    def get_latest_indicators(self) -> Dict:
        """
        获取最新的指标值
        
        Returns:
            包含各指标最新值的字典
        """
        if not self.indicators:
            self.calculate_all_indicators()
        
        if self.data is None or self.data.empty:
            return {}
        
        latest_idx = -1
        close = self.data['close'].iloc[latest_idx]
        
        result = {
            'symbol': self.symbol,
            'date': str(self.data.index[latest_idx].date()),
            'price': float(close),
            'open': float(self.data['open'].iloc[latest_idx]),
            'high': float(self.data['high'].iloc[latest_idx]),
            'low': float(self.data['low'].iloc[latest_idx]),
            'volume': int(self.data['volume'].iloc[latest_idx]),
        }
        
        # 添加移动平均线
        if 'moving_averages' in self.indicators:
            mas = self.indicators['moving_averages']
            result['sma_20'] = float(mas['sma_20'].iloc[latest_idx]) if not pd.isna(mas['sma_20'].iloc[latest_idx]) else None
            result['sma_50'] = float(mas['sma_50'].iloc[latest_idx]) if not pd.isna(mas['sma_50'].iloc[latest_idx]) else None
            result['sma_200'] = float(mas['sma_200'].iloc[latest_idx]) if not pd.isna(mas['sma_200'].iloc[latest_idx]) else None
        
        # 添加RSI
        if 'rsi' in self.indicators:
            rsi_val = self.indicators['rsi'].iloc[latest_idx]
            result['rsi'] = float(rsi_val) if not pd.isna(rsi_val) else None
        
        # 添加MACD
        if 'macd' in self.indicators:
            macd = self.indicators['macd']
            result['macd'] = float(macd['macd'].iloc[latest_idx]) if not pd.isna(macd['macd'].iloc[latest_idx]) else None
            result['macd_signal'] = float(macd['signal'].iloc[latest_idx]) if not pd.isna(macd['signal'].iloc[latest_idx]) else None
            result['macd_histogram'] = float(macd['histogram'].iloc[latest_idx]) if not pd.isna(macd['histogram'].iloc[latest_idx]) else None
        
        # 添加布林带
        if 'bollinger_bands' in self.indicators:
            bb = self.indicators['bollinger_bands']
            result['bb_upper'] = float(bb['upper'].iloc[latest_idx]) if not pd.isna(bb['upper'].iloc[latest_idx]) else None
            result['bb_middle'] = float(bb['middle'].iloc[latest_idx]) if not pd.isna(bb['middle'].iloc[latest_idx]) else None
            result['bb_lower'] = float(bb['lower'].iloc[latest_idx]) if not pd.isna(bb['lower'].iloc[latest_idx]) else None
        
        # 添加峰值/低谷
        if 'peaks_valleys' in self.indicators:
            pv = self.indicators['peaks_valleys']
            result['recent_high'] = pv['recent_high']
            result['recent_low'] = pv['recent_low']
        
        return result
