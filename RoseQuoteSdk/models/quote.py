# coding:utf-8
import warnings
from decimal import Decimal

import requests

from RoseQuoteSdk.common.exceptions.business_exception import BusinessException
from RoseQuoteSdk.common.exceptions.common_error import CommonError
from RoseQuoteSdk.common.tool.logger import logger, log
from RoseQuoteSdk.common.tool.object_to_dict import object2dict


class Quote(object):
    """
    实时行情基础类
    https://sites.google.com/site/stock2terms/financial-performance/the-committee 股票参数翻译
    """
    security_code: str = None
    name: str = None
    now: Decimal = None
    pre_close: Decimal = None   # 前收盘价
    close: Decimal = None
    open: Decimal = None
    high: Decimal = None
    low: Decimal = None
    average: Decimal = None     # 均价
    limit_up: Decimal = None    # 涨停价
    limit_down: Decimal = None  # 跌停价
    bid_volume: int = None      # 内盘
    ask_volume: int = None      # 外盘
    volume: int = None      # 成交量(手)
    quantity_relative_ratio: Decimal = None     # 量比
    committee: Decimal = None   # 委比
    amount: Decimal = None  # 成交额
    turnover: int = None    # 成交笔数
    turnover_ratio: Decimal = None    # 换手率
    pe_ttm: Decimal = None      # 市盈率TTM
    pe_dynamic: Decimal = None  # 市盈率(动态)
    pe_static: Decimal = None   # 市盈率(静态)
    circulation_market_value: Decimal = None    # 流通市值
    total_market_value: Decimal = None          # 总市值
    pb: Decimal = None      # 市净率

    bid1: Decimal = None
    bid2: Decimal = None
    bid3: Decimal = None
    bid4: Decimal = None
    bid5: Decimal = None

    bid1_volume: int = None
    bid2_volume: int = None
    bid3_volume: int = None
    bid4_volume: int = None
    bid5_volume: int = None

    ask1: Decimal = None
    ask2: Decimal = None
    ask3: Decimal = None
    ask4: Decimal = None
    ask5: Decimal = None

    ask1_volume: int = None
    ask2_volume: int = None
    ask3_volume: int = None
    ask4_volume: int = None
    ask5_volume: int = None

    datetime = None  # 时间

    # 类中的非基本数据类型，改变值时一定要用改变地址的api，例如 =, +等，不能使用append这种在原地址加减数据的方式（会导致类成员默认值被修改）
    transactions: list = []  # 逐笔成交

    def __init__(self, **args):
        for key in args.keys():
            if hasattr(self, key):
                setattr(self, key, args[key])

    @classmethod
    def get(cls, host: str, security_code: str, app_code: str = None):
        """
        实时市场数据
        :param host:
        :param security_code:
        :param app_code:
        :return:
        """
        path = '/api/v2/quote/real'
        if not security_code:
            raise BusinessException(CommonError.PARAMETER_ERROR)
        _quote = cls()
        _quote.security_code = security_code
        try:
            headers = dict()
            if app_code:
                headers.update({'Authorization': 'APPCODE %s' % app_code})
            resp = requests.get(url='%s%s' % (host, path), headers=headers, params=object2dict(_quote))
            if resp.status_code != 200:
                logger.info('行情服务返回错误: %s' % resp.text)
            resp = resp.json()
        except Exception as e:
            logger.error(e)
            raise BusinessException(error=CommonError.QUOTE_ERROR)
        if resp['code'] != 0:
            logger.error(resp['msg'])
            raise BusinessException(error=CommonError.QUOTE_ERROR)
        quote = cls(**resp['data'][0])
        return quote

    @classmethod
    def gets(cls, host: str, security_codes: str, fields: str = None) -> list:
        """
        批量实时市场数据
        :param host:
        :param security_codes:
        :param fields:
        :return:
        """
        path = '/api/v2/quote/real'
        if not security_codes:
            raise BusinessException(CommonError.PARAMETER_ERROR)
        _quote = cls()
        _quote.security_code = security_codes
        params = object2dict(_quote)
        params['fields'] = fields
        try:
            resp = requests.get(url='%s%s' % (host, path), params=params)
            if resp.status_code != 200:
                logger.info('行情服务返回错误: %s' % resp.text)
            resp = resp.json()
        except Exception as e:
            logger.error(e)
            raise BusinessException(error=CommonError.QUOTE_ERROR)
        if resp['code'] != 0:
            logger.error(resp['msg'])
            raise BusinessException(error=CommonError.QUOTE_ERROR)
        quotes = resp['data']
        return list(map(lambda x: cls(**x), quotes))

    def zip(self) -> str:
        """
        压缩格式，减少数据传输量
        :return:
        """
        return '%s,%s,%s' % (self.security_code, self.now, self.close)
        # return '%s,%s' % (self.security_code, self.now, self.close, self.open, self.high, self.low, self.volume)

    @classmethod
    def unzip(cls, quote_zip: str):
        quote_zip = quote_zip.split(',')
        quote = cls()
        quote.security_code = quote_zip[0]
        quote.now = quote_zip[1]
        quote.close = quote_zip[2]
        return quote


class QuoteOld(Quote):
    warnings.warn("some_old_function is deprecated", DeprecationWarning)

    # 兼容阿里云市场的老接口格式
    securityCode: str = None

    # 兼容阿里云市场的老接口格式
    bid1Volume: int = None
    bid2Volume: int = None
    bid3Volume: int = None
    bid4Volume: int = None
    bid5Volume: int = None

    # 兼容阿里云市场的老接口格式
    ask1Volume: int = None
    ask2Volume: int = None
    ask3Volume: int = None
    ask4Volume: int = None
    ask5Volume: int = None

    def __init__(self, **args):
        for key in args.keys():
            if hasattr(self, key):
                setattr(self, key, args[key])
        super().__init__()

    @classmethod
    def adapter(cls, quote: Quote):
        """
        实时市场数据适配: Decimal => int
        适配老接口数据
        :return: QuoteBaseOld
        """
        if not quote:
            raise BusinessException(CommonError.PARAMETER_ERROR)
        quote_old = cls(**quote.__dict__)
        quote_old.securityCode = quote.security_code
        quote_old.now = int(Decimal(quote.now) * 1000)
        quote_old.open = int(Decimal(quote.open) * 1000)
        quote_old.close = int(Decimal(quote.close) * 1000)
        quote_old.high = int(Decimal(quote.high) * 1000)
        quote_old.low = int(Decimal(quote_old.low) * 1000)

        quote_old.ask1 = int(Decimal(quote_old.ask1) * 1000) if quote_old.ask1 else None
        quote_old.ask2 = int(Decimal(quote_old.ask2) * 1000) if quote_old.ask2 else None
        quote_old.ask3 = int(Decimal(quote_old.ask3) * 1000) if quote_old.ask3 else None
        quote_old.ask4 = int(Decimal(quote_old.ask4) * 1000) if quote_old.ask4 else None
        quote_old.ask5 = int(Decimal(quote_old.ask5) * 1000) if quote_old.ask5 else None
        quote_old.bid1 = int(Decimal(quote_old.bid1) * 1000) if quote_old.bid1 else None
        quote_old.bid2 = int(Decimal(quote_old.bid2) * 1000) if quote_old.bid2 else None
        quote_old.bid3 = int(Decimal(quote_old.bid3) * 1000) if quote_old.bid3 else None
        quote_old.bid4 = int(Decimal(quote_old.bid4) * 1000) if quote_old.bid4 else None
        quote_old.bid5 = int(Decimal(quote_old.bid5) * 1000) if quote_old.bid5 else None

        quote_old.bid1Volume = quote_old.bid1_volume
        quote_old.bid2Volume = quote_old.bid2_volume
        quote_old.bid3Volume = quote_old.bid3_volume
        quote_old.bid4Volume = quote_old.bid4_volume
        quote_old.bid5Volume = quote_old.bid5_volume

        quote_old.ask1Volume = quote_old.ask1_volume
        quote_old.ask2Volume = quote_old.ask2_volume
        quote_old.ask3Volume = quote_old.ask3_volume
        quote_old.ask4Volume = quote_old.ask4_volume
        quote_old.ask5Volume = quote_old.ask5_volume

        transactions = list()
        for transaction in quote_old.transactions:
            transaction = Transaction(**transaction)
            transaction.price = int(Decimal(transaction.price) * 1000) if transaction.price else None
            transaction.amount = int(Decimal(transaction.amount) * 1000) if transaction.amount else None
            transactions.append(transaction)
        quote_old.transactions = transactions
        return quote_old


class Transaction(object):
    """
        实时行情逐笔成交记录
    """
    time = None  # 时间: 分、秒
    price = None  # 价格
    volume = None  # 成交量
    action = None  # 方向
    amount = None  # 金额

    def __init__(self, **args):
        for key in args.keys():
            if hasattr(self, key):
                setattr(self, key, args[key])


class Timeline(object):
    """
    分时图
    """
    id: str = None
    security_code: str = None
    open: Decimal = None
    close: Decimal = None
    low: Decimal = None
    high: Decimal = None
    # now = None
    volume = None
    # 以结束时间作为打点
    datetime = None

    def __init__(self, **args):
        for key in args.keys():
            if hasattr(self, key):
                setattr(self, key, args[key])

    @classmethod
    def gets(cls, kids: str = None) -> list:
        """
        批量未打点分时数据
        :param cls:
        :param kids:
        :return:
        """
        pass

    @classmethod
    @log
    def get(cls, kid: str):
        """
        未打点分时数据
        :param kid:
        :return:
        """
        pass


class KLine(Timeline):
    """
    分时图和1分钟k线数据可以合并，这样只需要计算一次
    """
    # id = None
    average: Decimal = None

    # volume: int = None

    ma5: Decimal = None
    ma10: Decimal = None
    ma20: Decimal = None
    ma30: Decimal = None

    # 兼容日k、周k等
    date = None
    # 以结束时间作为打点
    # datetime = None

    def __init__(self, **args):
        super().__init__(**args)
        for key in args.keys():
            if hasattr(self, key):
                setattr(self, key, args[key])


class AStockSituation(object):
    """
    A股概况
    """
    ups: int = 0     # 上涨数
    downs: int = 0   # 下跌数
    evens: int = 0      # 平数
    stop_ups: int = 0    # 涨停数
    stop_downs: int = 0  # 跌停数
    _10_8: int = 0  # < -8%
    _8_6: int = 0   # -8% < x < -6%
    _6_4: int = 0   # -6% < x < -4%
    _4_2: int = 0   # -4% < x < -2%
    _2_0: int = 0   # -2% < x < 0%
    _0_2: int = 0   # 0% < x < +2%
    _2_4: int = 0   # +2% < x < +4%
    _4_6: int = 0   # +4% < x < +6%
    _6_8: int = 0   # +6% < x < +8%
    _8_10: int = 0  # > +8%

    def __init__(self, **args):
        for key in args.keys():
            if hasattr(self, key):
                setattr(self, key, args[key])
