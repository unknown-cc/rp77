from xiancord.core import Cog_Extension
from discord.ext import commands

class command_ping(Cog_Extension):
    @commands.command(name='ping')
    @commands.is_owner()
    async def ping(self, ctx:commands.Context):
        await ctx.channel.send("pong!" , delete_after=10)

async def setup(bot:commands.Bot):
    await bot.add_cog(command_ping(bot))