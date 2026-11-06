"""get_quote 真实环境测试"""

import unittest

from rose_quote_sdk import RoseQuoteSdk
from rose_quote_sdk.main.common.exception.business_exception import BusinessException

HOST = 'https://xhuabu.market.alicloudapi.com'
APP_CODE = 'your-app-code'


class TestGetQuote(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rose_quote_sdk = RoseQuoteSdk(host=HOST, app_code=APP_CODE)

    def test_get_quote(self):
        quote = self.rose_quote_sdk.get_quote('SH.600000')
        print(quote.model_dump_json(indent=2))
        self.assertEqual(quote.security_code, 'SH.600000')
        self.assertIsNotNone(quote.name)
        self.assertIsNotNone(quote.now)
        self.assertIsNotNone(quote.bid1)
        self.assertIsNotNone(quote.ask1)

    def test_get_quote_empty_code_raises(self):
        with self.assertRaises(BusinessException):
            self.rose_quote_sdk.get_quote('')


if __name__ == '__main__':
    unittest.main()
