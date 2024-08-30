from nonebot import on_command
from nonebot.internal.params import ArgPlainText
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message


from .runcode import code
from nonebot.typing import T_State
from nonebot import logger

runcode = code()
command = on_command("run", aliases={"code", "运行"}, priority=5, block=False)

success_msg = "太强了，运行成功了！输出为："
failed_msg = "报错啦！真是笨蛋捏"
trigger = "帮帮我"
support_msg = "kotlin/java/lua/nodejs/go/swift/rust/ruby/c#/c++/c/py/php"


@command.handle()
async def main(state: T_State, args: Message = CommandArg()):
    code_info = args.extract_plain_text()
    if not code_info:
        await command.finish(f"请输入运行语言和代码...\n目前支持的语言有:\n{support_msg}")
    split = code_info.split('\n')
    language = split[0].replace('\n', '').replace('\r', '').strip()
    logger.info(split)
    try:
        output, error = await runcode.run(language, split[1])
        state["code_run_status"] = False if error.replace('\n', '') else True
        logger.info(state.get("code_run_status"))
        if not state.get("code_run_status"):
            state["code_run_error"] = error
            await command.skip()
        await command.finish(f'{success_msg} \n {output}')
    except IndexError:
        await command.finish(
            f"不支持的语言\n目前仅支持\n{support_msg}\n请输入全称")


@command.got("trigger_msg", prompt=failed_msg)
async def get_error(state: T_State, trigger_msg: Message = ArgPlainText()):
    status = state.get("code_run_status")
    logger.info(status)
    if (trigger in trigger_msg) and not status:
        await command.finish(f"出现的异常是: \n{'=' * 10}\n{state.get('code_run_error')}\n{'=' * 10}\n下次要注意哦")
    await command.finish('是哪里错了呢？')
