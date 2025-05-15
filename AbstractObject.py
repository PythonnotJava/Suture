# 抽象数据结构以及归约

from typing import *
from dataclasses import dataclass

# 气源
# 规定：
# 1. 一个气源可以连接无数个用户
# 2. 一个气源开源连接无数个气源
@dataclass
class GasAgent:
    ID : int
    productor : Callable  # 随时间变换的产气函数
    init : float  # 初始气量
    errorp : float  # 失效率
    targets : list
    price : float  # 储存价格，单位：元/立方米

# 用户
# 规定：
# 1. 一个用户源可以连接无数个气源
# 2. 一个用户源可以连接无数个用户源
# 3. 用户源之间不能互相提供气源
@dataclass
class UserAgent:
    ID : int
    init : float  # 初始气量
    consumer : Callable  # 随时间变换的使用气量的函数
    targets: list
    price : float  # 天然气价格，单位：元/立方米

# 管道
# 一根管道只能连接两个节点（节点指用户源、气源）
@dataclass
class PipeAgent:
    ID : int
    length : float  # 长度
    errorp : float  # 失效率
    targets: list
    price : float  # 输送价格，单位：元/m³·km
