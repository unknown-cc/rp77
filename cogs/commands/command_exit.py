from xiancord.core import Cog_Extension
from discord.ext import commands
from xiancord.logger import terminal
import asyncio

class command_exit(Cog_Extension):
    @commands.command(name='exit')
    @commands.is_owner()
    async def exit(self, ctx:commands.Context):
        terminal("機器人已關閉" , "EXIT")
        await self.bot.close()   # 正常關閉 Discord bot
        await asyncio.sleep(1)

async def setup(bot:commands.Bot):
    await bot.add_cog(command_exit(bot))