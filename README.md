# rose-quote-sdk

> 开放SDK

## 打包

```bash
python setup.py sdist
```

## 安装

```bash
pip install -U rose-quote-sdk-1.0.0.tar.gz
```

## 使用

```python
from RoseQuoteSdk.models.quote import Quote
quote = Quote.get(host='https://xhuabu.market.alicloudapi.com', security_code='SZ.000011', app_code='00a5cf10087b438ba39f694354b7730b')
print(quote.name)
```
