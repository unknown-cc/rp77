from xiancord.core import Cog_Extension
from discord.ext import commands

class clear(Cog_Extension):
    @commands.command(name='clear')
    @commands.has_permissions(administrator = True)
    async def clear(self, ctx:commands.Context, num=999):
        await ctx.channel.purge(limit=num+1)

async def setup(bot:commands.Bot):
    await bot.add_cog(clear(bot))