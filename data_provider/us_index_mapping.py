# -*- coding: utf-8 -*-
"""
===================================
美股指数与股票代码工具
===================================

提供：
1. 美股指数代码映射（如 SPX -> ^GSPC）
2. 美股股票代码识别（AAPL、TSLA 等）
3. 台股股票代码识别与 Yahoo Finance 转换

美股指数在 Yahoo Finance 中需使用 ^ 前缀，与股票代码不同。
台股在 Yahoo Finance 中需使用 .TW 后缀（如 2330.TW）。
"""

import re

# 美股代码正则：1-5 个大写字母，可选 .X 后缀（如 BRK.B）
_US_STOCK_PATTERN = re.compile(r'^[A-Z]{1,5}(\.[A-Z])?$')

# 台股代码正则：4-6 位数字
_TW_STOCK_PATTERN = re.compile(r'^\d{4,6}$')

# 台股名称映射（代码 -> 中文名称）
TW_STOCK_NAME_MAPPING = {
    # 半导体/电子
    '2330': '台积电',
    '2317': '鸿海',
    '2454': '联发科',
    '3034': '联咏',
    '3711': '日月光投控',
    '5347': '世界先进',
    '5388': '威盛电子',
    '5471': '松翰',
    '6136': '平价',
    
    # 金融
    '2881': '富邦金',
    '2882': '国泰金',
    '2883': '开发金',
    '2884': '玉山金',
    '2885': '元大金',
    '2886': '兆丰金',
    '2887': '台新金',
    '2888': '新光金',
    '2891': '中信金',
    '2892': '第一金',
    
    # 传产/航运
    '2618': '长荣航',
    '2609': '阳明',
    '2207': '和泰车',
    '2002': '中钢',
    
    # ETF
    '0050': '元大台灣50',
    '0051': '元大中型100',
    '0052': '富邦科技',
    '0053': '元大高股息',
    '0054': '元大炬',
    '0055': '元大高股息',
    '0056': '元大高股息低波',
    '0057': '富邦摩台',
    '0058': '富邦发达',
    '0059': '富邦金融',
    '00646': '元大台灣50正2',
    '00647L': '元大高股息100',
    '00690': '中信高股息100',
    
    # 权重股
    '2303': '联电',
    '2308': '台达电',
    '2412': '中华电',
    '2812': '中ky',
    '4904': '远传',
    '8046': '南亚科',
    
    # 其他热门
    '6182': '合晶',
    '3406': '玉晶光',
    '3533': '嘉泽',
    '3661': '世芯-KY',
    '3702': '大立光',
    '6515': '颖崴',
}

# 台股指數映射
TW_INDEX_MAPPING = {
    'TWII': ('^TWII', '加權指數'),
    '^TWII': ('^TWII', '加權指數'),
    'TAIEX': ('^TWII', '加權指數'),
    '加權指數': ('^TWII', '加權指數'),
    '台股': ('^TWII', '加權指數'),
}


# 用户输入 -> (Yahoo Finance 符号, 中文名称)
US_INDEX_MAPPING = {
    # 标普 500
    'SPX': ('^GSPC', '標普500指數'),
    '^GSPC': ('^GSPC', '標普500指數'),
    'GSPC': ('^GSPC', '標普500指數'),
    # 道瓊斯工業平均指數
    'DJI': ('^DJI', '道瓊斯工業指數'),
    '^DJI': ('^DJI', '道瓊斯工業指數'),
    'DJIA': ('^DJI', '道瓊斯工業指數'),
    # 納斯達克綜合指數
    'IXIC': ('^IXIC', '納斯達克綜合指數'),
    '^IXIC': ('^IXIC', '納斯達克綜合指數'),
    'NASDAQ': ('^IXIC', '納斯達克綜合指數'),
    # 纳斯达克 100
    'NDX': ('^NDX', '納斯達克100指數'),
    '^NDX': ('^NDX', '納斯達克100指數'),
    # VIX 波动率指数
    'VIX': ('^VIX', 'VIX恐慌指數'),
    '^VIX': ('^VIX', 'VIX恐慌指數'),
    # 罗素 2000
    'RUT': ('^RUT', '羅素2000指數'),
    '^RUT': ('^RUT', '羅素2000指數'),
}


def is_us_index_code(code: str) -> bool:
    """
    判断代码是否为美股指数符号。

    Args:
        code: 股票/指数代码，如 'SPX', 'DJI'

    Returns:
        True 表示是已知美股指数符号，否则 False

    Examples:
        >>> is_us_index_code('SPX')
        True
        >>> is_us_index_code('AAPL')
        False
    """
    return (code or '').strip().upper() in US_INDEX_MAPPING


def is_us_stock_code(code: str) -> bool:
    """
    判断代码是否为美股股票符号（排除美股指数）。

    美股股票代码为 1-5 个大写字母，可选 .X 后缀如 BRK.B。
    美股指数（SPX、DJI 等）明确排除。

    Args:
        code: 股票代码，如 'AAPL', 'TSLA', 'BRK.B'

    Returns:
        True 表示是美股股票符号，否则 False

    Examples:
        >>> is_us_stock_code('AAPL')
        True
        >>> is_us_stock_code('TSLA')
        True
        >>> is_us_stock_code('BRK.B')
        True
        >>> is_us_stock_code('SPX')
        False
        >>> is_us_stock_code('600519')
        False
    """
    normalized = (code or '').strip().upper()
    # 美股指数不是股票
    if normalized in US_INDEX_MAPPING:
        return False
    return bool(_US_STOCK_PATTERN.match(normalized))


def is_tw_stock_code(code: str) -> bool:
    """
    判断代码是否为台股股票符号（排除 A股和港股）。

    台股代码为 4-6 位数字，但需要排除：
    - A股 6位（上海 0 开头，深圳 1/2/3 开头）
    - 港股 5位

    Args:
        code: 股票代码，如 '2330', '0050', 'tw2330'

    Returns:
        True 表示是台股股票符号，否则 False

    Examples:
        >>> is_tw_stock_code('2330')
        True
        >>> is_tw_stock_code('0050')
        True
        >>> is_tw_stock_code('tw2330')
        True
        >>> is_tw_stock_code('600519')
        False  # A股
        >>> is_tw_stock_code('00700')
        False  # 港股
        >>> is_tw_stock_code('AAPL')
        False  # 美股
    """
    normalized = (code or '').strip().lower()
    
    # 移除 tw 前缀
    if normalized.startswith('tw'):
        normalized = normalized[2:]
    
    # 必须是数字
    if not normalized.isdigit():
        return False
    
    # 长度 4-6 位
    if len(normalized) < 4 or len(normalized) > 6:
        return False
    
    # 排除 A股：6位且上海(0)/深圳(1-3)开头
    if len(normalized) == 6:
        if normalized[0] == '0':  # 上海A股
            return False
        if normalized[0] in '123':  # 深圳A股
            return False
    
    # 排除港股：5位（港股代码）
    if len(normalized) == 5:
        return False
    
    return True


def is_tw_index_code(code: str) -> bool:
    """
    判断代码是否为台股指数符号。

    Args:
        code: 指数代码，如 'TWII', 'TAIEX', '^TWII'

    Returns:
        True 表示是已知台股指数符号，否则 False

    Examples:
        >>> is_tw_index_code('TWII')
        True
        >>> is_tw_index_code('^TWII')
        True
        >>> is_tw_index_code('0050')
        False
    """
    return (code or '').strip().upper() in TW_INDEX_MAPPING


def get_tw_stock_name(code: str) -> str:
    """
    获取台股的中文名称。

    Args:
        code: 台股代码，如 '2330', '0050'

    Returns:
        中文名称，未找到时返回 None

    Examples:
        >>> get_tw_stock_name('2330')
        '台积电'
        >>> get_tw_stock_name('0050')
        '元大台灣50'
    """
    normalized = (code or '').strip()
    
    # 移除 tw 前缀
    if normalized.lower().startswith('tw'):
        normalized = normalized[2:]
    
    return TW_STOCK_NAME_MAPPING.get(normalized)


def get_tw_stock_yf_symbol(code: str) -> tuple:
    """
    获取台股的 Yahoo Finance 符号与中文名称。

    Args:
        code: 用户输入，如 '2330', '0050', 'tw2330'

    Returns:
        (yf_symbol, chinese_name) 元组，未找到时返回 (None, None)。

    Examples:
        >>> get_tw_stock_yf_symbol('2330')
        ('2330.TW', '台积电')
        >>> get_tw_stock_yf_symbol('0050')
        ('0050.TW', '元大台灣50')
        >>> get_tw_stock_yf_symbol('AAPL')
        (None, None)
    """
    normalized = (code or '').strip().lower()
    
    # 移除 tw 前缀
    if normalized.startswith('tw'):
        normalized = normalized[2:]
    
    if not is_tw_stock_code(code):
        return (None, None)
    
    chinese_name = get_tw_stock_name(normalized)
    return (f"{normalized}.TW", chinese_name)


def get_tw_index_yf_symbol(code: str) -> tuple:
    """
    获取台股指数的 Yahoo Finance 符号与中文名称。

    Args:
        code: 用户输入，如 'TWII', 'TAIEX', '^TWII'

    Returns:
        (yf_symbol, chinese_name) 元组，未找到时返回 (None, None)。

    Examples:
        >>> get_tw_index_yf_symbol('TWII')
        ('^TWII', '加權指數')
        >>> get_tw_index_yf_symbol('0050')
        (None, None)
    """
    normalized = (code or '').strip().upper()
    return TW_INDEX_MAPPING.get(normalized, (None, None))


def get_us_index_yf_symbol(code: str) -> tuple:
    """
    获取美股指数的 Yahoo Finance 符号与中文名称。

    Args:
        code: 用户输入，如 'SPX', '^GSPC', 'DJI'

    Returns:
        (yf_symbol, chinese_name) 元组，未找到时返回 (None, None)。

    Examples:
        >>> get_us_index_yf_symbol('SPX')
        ('^GSPC', '標普500指數')
        >>> get_us_index_yf_symbol('AAPL')
        (None, None)
    """
    normalized = (code or '').strip().upper()
    return US_INDEX_MAPPING.get(normalized, (None, None))
