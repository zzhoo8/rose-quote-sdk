#!/usr/bin/env bash

# 打包
rm dist/*.tar.gz
python setup.py sdist

# 丢弃工作区 和 暂存区 中的文件变更
git restore "*.py"
