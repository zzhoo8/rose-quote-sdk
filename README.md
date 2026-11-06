# rose-quote-sdk

> [阿里云市场行情API](https://market.aliyun.com/products/57000002/cmapi023895.html) 对应的 Python SDK

## 安装

```bash
pip install rose-quote-sdk
```

## 使用

```python
from rose_quote_sdk import RoseQuoteSdk

# 单例初始化（全局唯一）
sdk = RoseQuoteSdk(
    host='https://xhuabu.market.alicloudapi.com',
    app_code='your_app_code',
)

# 获取实时行情
quote = sdk.get_quote('600000.SH')
print(quote.name, quote.now)
```

或直接调用模型类：

```python
from rose_quote_sdk.main.model.quote import Quote

quote = Quote.get(
    host='https://xhuabu.market.alicloudapi.com',
    security_code='600000.SH',
    app_code='your_app_code',
)
```
