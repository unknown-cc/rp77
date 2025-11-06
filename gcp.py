import os
from datetime import datetime
import logging
from discord.ext import commands
from discord import app_commands
from xiancord.logger import terminal
from xiancord.database import db_init_local
import discord
import asyncio
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

# 宣告主體

intents = discord.Intents.all()
intents.members = True
bot = Bot_Extension(command_prefix='>>' , help_command=None , intents=intents)
discord.utils.setup_logging(formatter=logging.WARNING ,level=logging.ERROR, root=False)

# 讀取 config
with open('config.json' , 'r' , encoding='utf-8') as file:
    import json
    config = json.load(file)


terminal(f"正在初始化" , "啟動")
token = config["token2"]
async def load_database():
    await db_init_local()

async def load_extensions():
        
        # 載入 cogs
        for parent , dirs , files in os.walk("./cogs"):
            if "__" in parent:
                continue    
            else:
                white_list = [
                    "debug_event",
                ]
                for file in files:
                    if file.endswith(".py"):
                        if file[:-3] not in white_list:
                            continue
                        parent_fix = parent[2:].replace("\\",".").replace("/",".")
                        terminal(f"{parent_fix}:{file[:-3]} >> 已載入 <<" , "準備")
                        try:
                            await bot.load_extension(f"{parent_fix}.{file[:-3]}")
                        except Exception as e:
                            terminal(e)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(bot.start(token))