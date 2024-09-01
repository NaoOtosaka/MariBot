from sys import prefix

from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    # 设置概率触发的阈值，例如0.5表示50%的概率
    yes_man_threshold: float = 0.3

    # 触发前缀
    yes_man_prefix: list = ['我觉得']

    # 是否使用白名单，不使用时回复全体
    yes_man_use_whitelist: bool = False

    # 包含允许的qq的数组，默认为空
    # 示例 [123456,234567]
    yes_man_whitelist_user: list = []
