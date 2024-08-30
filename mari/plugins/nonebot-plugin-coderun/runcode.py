from typing import Tuple

import httpx
import re

from nonebot.drivers.websockets import logger


class code():
    def __init__(self):
        self.codeIds = {
            "kotlin": 2960,
            "java": 10,
            "lua": 66,
            "nodejs": 22,
            "go": 21,
            "swift": 20,
            "rust": 19,
            "ruby": 13,
            "c#": 14,
            "c++": 12,
            "c": 11,
            "python": 9,
            "php": 1
        }
        self.otherName = {
            "kotlin": "kt",
            "java": "java",
            "lua": "lua",
            "nodejs": "node.js",
            "go": "go",
            "swift": "swift",
            "rust": "rs",
            "ruby": "rb",
            "c#": "cs",
            "c++": "cpp",
            "c": "c",
            "python": "py3",
            "php": "php"
        }

    async def run(self, language, code) -> Tuple[str, str]:
        try:
            codeId = self.codeIds[language]
        except KeyError:
            raise IndexError
        token = await self.getToken(codeId)
        result = await self.getResult(token, code, language)
        return result

    async def getToken(self, codeId) -> str:
        url = f"https://www.jyshare.com/compile/{codeId}/"
        async with httpx.AsyncClient(verify=False, timeout=60, follow_redirects=True) as client:
            data = await client.get(url)
            result = data.text
        token = re.findall("token = '(.+)';", result)[0]
        return token

    async def getResult(self, token, code, language) -> Tuple[str, str]:
        language = self.otherName[language]
        data = {
            "code": code,
            "token": token,
            "stdin": '',
            "language": 7,
            "fileext": language
        }
        async with httpx.AsyncClient(verify=False, timeout=60, follow_redirects=True) as client:
            data = await client.post("https://www.runoob.com/try/compile2.php", data=data)
            logger.info(data.json())
            result = data.json()['output']
            error = data.json()['errors']
        return result, error
