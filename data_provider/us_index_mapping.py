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


# 用户输入 -> (Yahoo Finance 符号, 中文名称)
US_INDEX_MAPPING = {
    # 标普 500
    'SPX': ('^GSPC', '标普500指数'),
    '^GSPC': ('^GSPC', '标普500指数'),
    'GSPC': ('^GSPC', '标普500指数'),
    # 道琼斯工业平均指数
    'DJI': ('^DJI', '道琼斯工业指数'),
    '^DJI': ('^DJI', '道琼斯工业指数'),
    'DJIA': ('^DJI', '道琼斯工业指数'),
    # 纳斯达克综合指数
    'IXIC': ('^IXIC', '纳斯达克综合指数'),
    '^IXIC': ('^IXIC', '纳斯达克综合指数'),
    'NASDAQ': ('^IXIC', '纳斯达克综合指数'),
    # 纳斯达克 100
    'NDX': ('^NDX', '纳斯达克100指数'),
    '^NDX': ('^NDX', '纳斯达克100指数'),
    # VIX 波动率指数
    'VIX': ('^VIX', 'VIX恐慌指数'),
    '^VIX': ('^VIX', 'VIX恐慌指数'),
    # 罗素 2000
    'RUT': ('^RUT', '罗素2000指数'),
    '^RUT': ('^RUT', '罗素2000指数'),
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
    
    return (f"{normalized}.TW", None)


def get_us_index_yf_symbol(code: str) -> tuple:
    """
    获取美股指数的 Yahoo Finance 符号与中文名称。

    Args:
        code: 用户输入，如 'SPX', '^GSPC', 'DJI'

    Returns:
        (yf_symbol, chinese_name) 元组，未找到时返回 (None, None)。

    Examples:
        >>> get_us_index_yf_symbol('SPX')
        ('^GSPC', '标普500指数')
        >>> get_us_index_yf_symbol('AAPL')
        (None, None)
    """
    normalized = (code or '').strip().upper()
    return US_INDEX_MAPPING.get(normalized, (None, None))
