# coding:utf-8
from enum import Enum, unique


@unique
class KLineInterval(Enum):
    k_1min = '1m'
    k_5min = '5m'
    k_15min = '15m'
    k_30min = '30m'
    k_60min = '60m'
    k_1D = '1D'
    k_1W = '1W'
    k_1M = '1M'


class QuoteOrder(Enum):
    """
    行情排序
    """
    UP = 'UP'           # 涨幅
    DOWN = 'DOWN'       # 跌幅
