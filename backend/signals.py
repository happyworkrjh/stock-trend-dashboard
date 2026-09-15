"""
交易信号生成模块
基于技术指标生成买入/卖出信号
"""

from analyzer import StockAnalyzer
from config import get_config
from typing import Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
config = get_config()

class SignalGenerator:
    """交易信号生成器"""
    
    def __init__(self, symbol: str):
        """
        初始化信号生成器
        
        Args:
            symbol: 股票代码
        """
        self.symbol = symbol
        self.analyzer = StockAnalyzer(symbol)
        self.config = config.SIGNAL_CONFIG
        
    def check_rsi_signal(self) -> Dict:
        """
        检查RSI信号
        
        Returns:
            包含RSI信号的字典
        """
        try:
            indicators = self.analyzer.calculate_rsi()
            rsi_value = indicators.iloc[-1]
            
            if rsi_value < self.config['RSI_OVERSOLD']:
                return {
                    'indicator': 'RSI',
                    'signal': 'BUY',
                    'value': float(rsi_value),
                    'strength': 'STRONG' if rsi_value < 20 else 'MEDIUM',
                    'description': f'RSI已进入超卖区域 ({rsi_value:.2f})'
                }
            elif rsi_value > self.config['RSI_OVERBOUGHT']:
                return {
                    'indicator': 'RSI',
                    'signal': 'SELL',
                    'value': float(rsi_value),
                    'strength': 'STRONG' if rsi_value > 80 else 'MEDIUM',
                    'description': f'RSI已进入超买区域 ({rsi_value:.2f})'
                }
            else:
                return {
                    'indicator': 'RSI',
                    'signal': 'NEUTRAL',
                    'value': float(rsi_value),
                    'strength': 'WEAK',
                    'description': f'RSI处于中性区域 ({rsi_value:.2f})'
                }
        except Exception as e:
            logger.error(f"Error checking RSI signal for {self.symbol}: {str(e)}")
            return {}
    
    def check_macd_signal(self) -> Dict:
        """
        检查MACD信号
        
        Returns:
            包含MACD信号的字典
        """
        try:
            macd_data = self.analyzer.calculate_macd()
            
            macd_val = macd_data['macd'].iloc[-1]
            signal_val = macd_data['signal'].iloc[-1]
            histogram = macd_data['histogram'].iloc[-1]
            
            # 检查上一根K线
            prev_histogram = macd_data['histogram'].iloc[-2] if len(macd_data['histogram']) > 1 else histogram
            
            # MACD金叉（买入信号）
            if prev_histogram < 0 and histogram > 0:
                return {
                    'indicator': 'MACD',
                    'signal': 'BUY',
                    'value': float(macd_val),
                    'strength': 'STRONG',
                    'description': f'MACD出现金叉信号'
                }
            # MACD死叉（卖出信号）
            elif prev_histogram > 0 and histogram < 0:
                return {
                    'indicator': 'MACD',
                    'signal': 'SELL',
                    'value': float(macd_val),
                    'strength': 'STRONG',
                    'description': f'MACD出现死叉信号'
                }
            else:
                return {
                    'indicator': 'MACD',
                    'signal': 'NEUTRAL',
                    'value': float(macd_val),
                    'strength': 'WEAK',
                    'description': f'MACD未出现明确信号'
                }
        except Exception as e:
            logger.error(f"Error checking MACD signal for {self.symbol}: {str(e)}")
            return {}
    
    def check_ma_signal(self) -> Dict:
        """
        检查移动平均线信号
        
        Returns:
            包含MA信号的字典
        """
        try:
            mas = self.analyzer.calculate_moving_averages()
            close = self.analyzer.data['close'].iloc[-1]
            
            sma_20 = mas['sma_20'].iloc[-1]
            sma_50 = mas['sma_50'].iloc[-1]
            sma_200 = mas['sma_200'].iloc[-1]
            
            # 黄金交叉（20日线穿过50日线）
            prev_sma_20 = mas['sma_20'].iloc[-2] if len(mas['sma_20']) > 1 else sma_20
            prev_sma_50 = mas['sma_50'].iloc[-2] if len(mas['sma_50']) > 1 else sma_50
            
            if prev_sma_20 < prev_sma_50 and sma_20 > sma_50:
                return {
                    'indicator': 'MA_CROSS',
                    'signal': 'BUY',
                    'value': float(close),
                    'strength': 'STRONG',
                    'description': f'20日线穿过50日线（黄金交叉）'
                }
            # 死亡交叉（20日线穿过50日线向下）
            elif prev_sma_20 > prev_sma_50 and sma_20 < sma_50:
                return {
                    'indicator': 'MA_CROSS',
                    'signal': 'SELL',
                    'value': float(close),
                    'strength': 'STRONG',
                    'description': f'20日线穿过50日线向下（死亡交叉）'
                }
            # 上升趋势（价格在所有MA之上）
            elif close > sma_20 > sma_50 > sma_200:
                return {
                    'indicator': 'MA_TREND',
                    'signal': 'BUY',
                    'value': float(close),
                    'strength': 'MEDIUM',
                    'description': f'价格处于上升趋势（所有MA向上排列）'
                }
            # 下降趋势（价格在所有MA之下）
            elif close < sma_20 < sma_50 < sma_200:
                return {
                    'indicator': 'MA_TREND',
                    'signal': 'SELL',
                    'value': float(close),
                    'strength': 'MEDIUM',
                    'description': f'价格处于下降趋势（所有MA向下排列）'
                }
            else:
                return {
                    'indicator': 'MA_TREND',
                    'signal': 'NEUTRAL',
                    'value': float(close),
                    'strength': 'WEAK',
                    'description': f'移动平均线未显示明确趋势'
                }
        except Exception as e:
            logger.error(f"Error checking MA signal for {self.symbol}: {str(e)}")
            return {}
    
    def check_bollinger_signal(self) -> Dict:
        """
        检查布林带信号
        
        Returns:
            包含布林带信号的字典
        """
        try:
            bb = self.analyzer.calculate_bollinger_bands()
            close = self.analyzer.data['close'].iloc[-1]
            
            upper = bb['upper'].iloc[-1]
            middle = bb['middle'].iloc[-1]
            lower = bb['lower'].iloc[-1]
            
            if close < lower:
                return {
                    'indicator': 'BOLLINGER',
                    'signal': 'BUY',
                    'value': float(close),
                    'strength': 'STRONG',
                    'description': f'价格突破布林带下轨（超卖）'
                }
            elif close > upper:
                return {
                    'indicator': 'BOLLINGER',
                    'signal': 'SELL',
                    'value': float(close),
                    'strength': 'STRONG',
                    'description': f'价格突破布林带上轨（超买）'
                }
            elif close < middle:
                return {
                    'indicator': 'BOLLINGER',
                    'signal': 'BUY',
                    'value': float(close),
                    'strength': 'MEDIUM',
                    'description': f'价格触及布林带中轨附近'
                }
            else:
                return {
                    'indicator': 'BOLLINGER',
                    'signal': 'NEUTRAL',
                    'value': float(close),
                    'strength': 'WEAK',
                    'description': f'价格处于布林带正常区间'
                }
        except Exception as e:
            logger.error(f"Error checking Bollinger signal for {self.symbol}: {str(e)}")
            return {}
    
    def generate_comprehensive_signals(self) -> Dict:
        """
        生成综合信号
        
        Returns:
            包含所有信号和综合建议的字典
        """
        # 加载数据
        if self.analyzer.data is None:
            self.analyzer.load_data()
        
        if self.analyzer.data.empty:
            logger.error(f"No data available for {self.symbol}")
            return {'error': 'No data available'}
        
        # 获取各个信号
        signals = [
            self.check_rsi_signal(),
            self.check_macd_signal(),
            self.check_ma_signal(),
            self.check_bollinger_signal()
        ]
        
        # 过滤空结果
        signals = [s for s in signals if s]
        
        # 统计信号
        buy_signals = [s for s in signals if s.get('signal') == 'BUY']
        sell_signals = [s for s in signals if s.get('signal') == 'SELL']
        
        # 生成综合建议
        if len(buy_signals) >= self.config['MIN_SIGNALS_FOR_ACTION']:
            overall_signal = 'STRONG_BUY'
            confidence = len(buy_signals) / len(signals) * 100
        elif len(buy_signals) > 0:
            overall_signal = 'BUY'
            confidence = len(buy_signals) / len(signals) * 100
        elif len(sell_signals) >= self.config['MIN_SIGNALS_FOR_ACTION']:
            overall_signal = 'STRONG_SELL'
            confidence = len(sell_signals) / len(signals) * 100
        elif len(sell_signals) > 0:
            overall_signal = 'SELL'
            confidence = len(sell_signals) / len(signals) * 100
        else:
            overall_signal = 'HOLD'
            confidence = 0
        
        # 获取最新价格信息
        latest = self.analyzer.get_latest_indicators()
        
        return {
            'symbol': self.symbol,
            'timestamp': datetime.now().isoformat(),
            'current_price': latest.get('price'),
            'overall_signal': overall_signal,
            'confidence': float(confidence),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'total_signals': len(signals),
            'signals': signals,
            'indicators': latest,
            'recommendation': self._get_recommendation(overall_signal, confidence)
        }
    
    def _get_recommendation(self, signal: str, confidence: float) -> str:
        """
        生成文字建议
        
        Args:
            signal: 综合信号
            confidence: 信心程度
            
        Returns:
            建议文字
        """
        if signal == 'STRONG_BUY':
            return f'强烈建议买入（信心度：{confidence:.0f}%），多个指标显示超卖'
        elif signal == 'BUY':
            return f'建议买入（信心度：{confidence:.0f}%），存在买入机会'
        elif signal == 'STRONG_SELL':
            return f'强烈建议卖出（信心度：{confidence:.0f}%），多个指标显示超买'
        elif signal == 'SELL':
            return f'建议卖出（信心度：{confidence:.0f}%），存在卖出机会'
        else:
            return f'建议观望（信心度：{confidence:.0f}%），暂无明确信号，等待更好机会'
