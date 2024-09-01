from nonebot import on_message, get_driver, logger
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.internal.rule import Rule
from nonebot.params import EventPlainText
from nonebot.plugin import PluginMetadata, get_plugin_config
from nonebot.typing import T_State

import random
from pathlib import Path

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="肯定机",
    description="你的发言，值得被肯定",
    usage="想要回复被肯定时，发言时以`.`或`。`结尾即可。（也可以自定义为自己喜欢的）",
    type="application",
    homepage="https://github.com/EuDs63/nonebot-plugin-yesman",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

agree_path = Path(__file__).parent / "agree.txt"
agree_text = agree_path.read_text('utf-8').splitlines()

global_config = get_driver().config
config = get_plugin_config(Config)


# 事件处理器
def yes_rule(state: T_State, message: str = EventPlainText()) -> bool:
    for i in config.yes_man_prefix:
        if message.startswith(i):
            state['yes_man_tigger_prefix'] = i
            return True
    return False


rule = Rule(yes_rule)

generate_agree = on_message(rule=rule)


@generate_agree.handle()
async def agree(state: T_State, event: MessageEvent) -> None:
    logger.debug(event.user_id)
    if config.yes_man_use_whitelist:
        if event.user_id not in config.yes_man_use_whitelist:
            # 使用白名单且用户不在白名单内不做任何事
            await generate_agree.finish()
    # 生成一个介于0到1之间的随机浮点数
    random_probability = random.random()

    if random_probability < config.yes_man_threshold:
        # 如果生成的随机浮点数小于阈值，发送一条肯定的消息
        msg_suffix = event.message.extract_plain_text()
        msg_suffix = msg_suffix.replace(state.get('yes_man_tigger_prefix', ''), '', 1)
        await generate_agree.finish(
            MessageSegment.text(f"{random.choice(agree_text)}，{msg_suffix}")
        )
    else:
        # 高于阈值时结束
        await generate_agree.finish()
