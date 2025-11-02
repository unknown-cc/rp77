from datetime import datetime
import logging
import threading
from discord.ext import commands
from discord import app_commands
from xiancord.logger import terminal
import discord
import asyncio
import os
from xiancord.database import db_init
from keep_alive import keep_alive
# 宣告主體
# 翻譯器
class CasinoTranslator(app_commands.Translator):
    async def translate(self, string, locale, context : app_commands.AppCommandContext):
        if locale == discord.Locale.taiwan_chinese:
            # 從 locale_str 的 extras 字典中取出你定義的繁中翻譯
            return string.extras.get("zh_TW")
        return None

class Bot_Extension(commands.Bot):            
    async def setup_hook(self):
        await load_database()
        await load_extensions()
        # 賭場
        await bot.tree.set_translator(CasinoTranslator())


intents = discord.Intents.all()
intents.members = True
bot = Bot_Extension(command_prefix='>>', help_command=None, intents=intents)
discord.utils.setup_logging(formatter=logging.WARNING,
                            level=logging.ERROR,
                            root=False)

terminal(f"正在初始化", "啟動")
async def load_database():
    await db_init()
    
async def load_extensions():
        # 載入 cogs
        for parent , dirs , files in os.walk("./cogs"):
            if "__" in parent:
                continue    
            else:
                white_list = [
                    "login_event",
                ]
                for file in files:
                    if file.endswith(".py"):
                        if file[:-3] not in white_list:
                            continue
                        parent_fix = parent[2:].replace("\\",".").replace("/",".")
                        terminal(f"{parent_fix}:{file[:-3]} >> 已載入 <<", "插件")
                        try:
                            await bot.load_extension(f"{parent_fix}.{file[:-3]}")
                        except:pass

token = os.environ['TOKEN']

if __name__ == "__main__":
    keep_alive()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(load_extensions())
    loop.run_until_complete(bot.start(token))
