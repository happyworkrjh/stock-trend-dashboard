import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """基础配置"""
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # API配置
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:3000']
    
    # 股票配置
    STOCKS_WATCH = os.getenv('STOCKS_WATCH', 'AAPL,MSFT,TSLA,GOOGL,AMZN').split(',')
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 3600))
    CHART_PERIOD = os.getenv('CHART_PERIOD', '1y')
    INTRADAY_PERIOD = os.getenv('INTRADAY_PERIOD', '5d')
    
    # 缓存配置
    CACHE_TIMEOUT = 300  # 5分钟
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 技术指标配置
    INDICATORS = {
        'SMA_SHORT': 20,      # 短期移动平均线
        'SMA_LONG': 50,       # 长期移动平均线
        'RSI_PERIOD': 14,
        'MACD_FAST': 12,
        'MACD_SLOW': 26,
        'MACD_SIGNAL': 9,
        'BB_PERIOD': 20,
        'BB_STD': 2,
    }
    
    # 信号配置
    SIGNAL_CONFIG = {
        'RSI_OVERSOLD': 30,
        'RSI_OVERBOUGHT': 70,
        'MIN_SIGNALS_FOR_ACTION': 3,  # 至少3个指标确认
    }

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    CORS_ORIGINS = ['https://yourdomain.com']

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    DATABASE = 'sqlite:///:memory:'

def get_config():
    """根据环境返回相应的配置"""
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()
