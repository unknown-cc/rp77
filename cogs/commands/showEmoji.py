import discord

from xiancord.core import Cog_Extension
from discord.ext import commands

class commandShowEmoji(Cog_Extension):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.counter = 0
    
    @commands.command(name='showEmoji' , aliases=["se"])    
    @commands.is_owner()
    async def showEmoji(self, ctx:commands.Context ):
        # if not ctx.author == ctx.guild.owner : return
        guilds = self.bot.guilds
        content = ""
        for guild in guilds:
            # if not guild.owner.id == 1128796864930656297 : continue
            content += f"伺服器：{guild.name}\n"
            emojis = guild.emojis
            if not emojis : continue
            for emoji in emojis:
                emoji_str = "<a:" if  emoji.animated else "<:"
                emoji_str += f"{emoji.name}:{emoji.id}>"
                new_content = f"\t{emoji_str} : {emoji.name} - {emoji.id}\n"
                if len(content + new_content) > 2000:
                    await ctx.send(content=content)
                    content = f"伺服器：{guild.name}\n"
                content = content + new_content
        await ctx.send(content=content)

async def setup(bot:commands.Bot):
    await bot.add_cog(commandShowEmoji(bot))