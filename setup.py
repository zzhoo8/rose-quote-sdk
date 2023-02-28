# -*- coding: utf-8 -*-
import re

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

# 安装时依赖包
with open('app/requirements.txt') as f:
    requirements = f.read().splitlines()
    # 过滤本地包和空行
    requirements = list(filter(lambda x: x and re.search(r'local', x) is None and not x.startswith('#'), requirements))
    # print(requirements)

# 参考https://docs.python.org/2/distutils/setupscript.html
setup(
    name='rose-quote-sdk',
    version='1.0.0',
    description='',
    long_description='',
    author="xx",
    author_email='',
    url='https://xx.com',
    packages=find_packages(),
    # package_dir={'common': 'common'},
    include_package_data=True,
    # 安装时的依赖包，若环境中没有，则会从pypi中下载安装
    install_requires=requirements,
    # install_requires 在安装模块时会自动安装依赖包
    # 而 extras_require 不会，这里仅表示该模块会依赖这些包
    # 但是这些包通常不会使用到，只有当你深度使用模块时，才会用到，这里需要你手动安装
    extras_require={},
    # 指定依赖包的下载地址
    dependency_links=[],
    license="ISCL",
    zip_safe=False,
    keywords='server',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    # 仅在测试时需要使用的依赖，在正常发布的代码中是没有用的。
    tests_require=[]
)
