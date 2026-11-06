import re
from setuptools import setup, find_packages

# 安装时依赖包
with open(file='dependence/requirements.txt', mode='r', encoding='utf-8') as f:
    requirements = f.read().splitlines()
    # 过滤本地包和空行
    requirements = list(filter(lambda x: x and re.search(r'local', x) is None and not x.startswith('#'), requirements))
    # print(requirements)

setup(
    name='rose-quote-sdk',
    version='1.3.0',
    description='阿里云市场行情数据 Python SDK',
    long_description_content_type="text/markdown",
    readme={"content-type": "text/markdown", "file": "README.md"},
    license="LicenseRef-Proprietary",
    license_files=["LICENSE"],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    extras_require={},
    include_package_data=True,
    zip_safe=False,
    keywords='rose,quote,sdk',
    url='https://xx.com'
)
