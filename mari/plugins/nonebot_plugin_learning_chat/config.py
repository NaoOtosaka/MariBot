from typing import List, Dict
from pathlib import Path
from pydantic import BaseModel, Field

from nonebot import get_driver, logger
from nonebot.utils import escape_tag
from ruamel.yaml import YAML

yaml = YAML(typ='rt')


CONFIG_PATH = Path() / "data" / "learning_chat" / "learning_chat.yml"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

driver = get_driver()
try:
    SUPERUSERS: List[int] = [int(s) for s in driver.config.superusers]
except Exception:
    SUPERUSERS = []
    logger.warning("请在.env.prod文件中中配置超级用户SUPERUSERS")

try:
    NICKNAME: str = list(driver.config.nickname)[0]
except Exception:
    NICKNAME = "bot"

COMMAND_START = driver.config.command_start.copy()
if "" in COMMAND_START:
    COMMAND_START.remove("")


class ChatGroupConfig(BaseModel):
    enable: bool = Field(default=True, alias="群聊学习开关")
    ban_words: List[str] = Field(default_factory=list, alias="屏蔽词")
    ban_users: List[int] = Field(default_factory=list, alias="屏蔽用户")
    answer_threshold: int = Field(default=4, alias="回复阈值")
    answer_threshold_weights: List[int] = Field(default=[10, 30, 60], alias="回复阈值权重")
    repeat_threshold: int = Field(default=3, alias="复读阈值")
    break_probability: float = Field(default=0.25, alias="打断复读概率")
    speak_enable: bool = Field(default=True, alias="主动发言开关")
    speak_threshold: int = Field(default=5, alias="主动发言阈值")
    speak_min_interval: int = Field(default=300, alias="主动发言最小间隔")
    speak_continuously_probability: float = Field(default=0.5, alias="连续主动发言概率")
    speak_continuously_max_len: int = Field(default=3, alias="最大连续主动发言句数")
    speak_poke_probability: float = Field(default=0.5, alias="主动发言附带戳一戳概率")

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.model_fields:
                self.__setattr__(key, value)


class ChatConfig(BaseModel):
    total_enable: bool = Field(default=True, alias="群聊学习总开关")
    enable_web: bool = Field(default=True, alias="启用后台管理")
    web_username: str = Field(default="chat", alias="后台管理用户名")
    web_password: str = Field(default="admin", alias="后台管理密码")
    web_secret_key: str = Field(
        default="49c294d32f69b732ef6447c18379451ce1738922a75cd1d4812ef150318a2ed0",
        alias="后台管理token密钥",
    )
    ban_words: List[str] = Field(default_factory=list, alias="全局屏蔽词")
    ban_users: List[int] = Field(default_factory=list, alias="全局屏蔽用户")
    KEYWORDS_SIZE: int = Field(default=3, alias="单句关键词分词数量")
    cross_group_threshold: int = Field(default=3, alias="跨群回复阈值")
    learn_max_count: int = Field(default=6, alias="最高学习次数")
    dictionary: List[str] = Field(default_factory=list, alias="自定义词典")
    group_config: Dict[int, ChatGroupConfig] = Field(default_factory=dict, alias="分群配置")

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.model_fields:
                self.__setattr__(key, value)


class ChatConfigManager:
    def __init__(self):
        self.file_path = CONFIG_PATH
        if self.file_path.exists():
            self.config = ChatConfig.model_validate(
                yaml.load(
                    self.file_path.read_text(encoding="utf-8")
                )
            )
        else:
            self.config = ChatConfig()
        self.save()

    def get_group_config(self, group_id: int) -> ChatGroupConfig:
        if group_id not in self.config.group_config:
            self.config.group_config[group_id] = ChatGroupConfig()
            self.save()
        return self.config.group_config[group_id]

    @property
    def config_list(self) -> List[str]:
        return list(self.config.model_dump(by_alias=True).keys())

    def save(self):
        with self.file_path.open("w", encoding="utf-8") as f:
            yaml.dump(
                self.config.model_dump(by_alias=True),
                f
            )


config_manager = ChatConfigManager()


def log_debug(command: str, info: str):
    logger.opt(colors=True).debug(f"<u><y>[{command}]</y></u>{escape_tag(info)}")


def log_info(command: str, info: str):
    logger.opt(colors=True).info(f"<u><y>[{command}]</y></u>{escape_tag(info)}")
