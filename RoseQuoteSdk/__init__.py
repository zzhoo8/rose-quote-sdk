# coding:utf-8
from RoseQuoteSdk.common.tool.logger import init_logger
from RoseQuoteSdk.models.quote import Quote


class RoseQuoteSdk(object):

    host: str = None
    app_code: str = None

    def __init__(self, host: str, app_code: str):
        """
        初始化rose-quote-sdk
        :param host: 阿里云市场API Host
        :param app_code 阿里云市场AppCode
        """
        RoseQuoteSdk.host = host
        RoseQuoteSdk.app_code = app_code
        # 日志初始化
        init_logger(debug=True, package=__package__)

    def get_quote(self, security_code: str) -> Quote:
        """
        获取实时行情数据
        :return:
        """
        quote = Quote.get(host=self.host, security_code=security_code)
        return quote
