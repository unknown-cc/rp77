from datetime import datetime
import logging
import threading
from discord.ext import commands
from xiancord.logger import terminal
import discord
import asyncio
import os
from keep_alive import keep_alive
# 宣告主體

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='>>', help_command=None, intents=intents)
discord.utils.setup_logging(formatter=logging.WARNING,
                            level=logging.ERROR,
                            root=False)

terminal(f"正在初始化", "啟動")

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
                        await bot.load_extension(f"{parent_fix}.{file[:-3]}")

token = os.environ['TOKEN']

if __name__ == "__main__":
    keep_alive()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(load_extensions())
    loop.run_until_complete(bot.start(token))
