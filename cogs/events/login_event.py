import os
from discord.ext import commands
from xiancord.core import Cog_Extension
from discord.ext import commands
from xiancord.logger import terminal
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo
from xiancord.time import now_str
class login_event(Cog_Extension):
    def __init__(self, bot:commands.Bot):
        super().__init__(bot)
        self.event = "登入事件"
    async def load_extensions(self , bot:commands.Bot):
        # 載入 cogs
        for parent , dirs , files in os.walk("./cogs"):
            if "__" in parent:
                continue    
            else:
                black_list = [
                    ]
                white_list = [

                ]
                for file in files:
                    if file.endswith(".py"):
                        if file[:-3] in self.bot.cogs.keys():
                            continue
                        if len(white_list):
                            if file[:-3] not in white_list:
                                continue
                        if file[:-3] in black_list:
                            continue
                        parent_fix = parent[2:].replace("\\",".").replace("/",".")
                        terminal(f"{parent_fix}:{file[:-3]} >> 已載入 <<" , "插件")
                        await bot.load_extension(f"{parent_fix}.{file[:-3]}")

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        terminal(f"機器人 >> 已載入 << " , "啟動")
        # 插件
        terminal("正在載入...","插件")
        await self.load_extensions(self.bot)
        terminal("載入完畢"  , "插件")
        # 登入
        login_string = f"機器人：{self.bot.user}\n"
        login_string += f"ID：{self.bot.user.id}"

        await self.bot.wait_until_ready()
        # await self.bot.change_presence(activity=discord.Game(name = "✨寶島2.0✨" , large_image_text="logo"))



async def setup(bot:commands.Bot):

    await bot.add_cog(login_event(bot))