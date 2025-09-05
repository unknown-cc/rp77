import discord
from xiancord.core import Cog_Extension
from discord.ext import commands

class commandEmojiID(Cog_Extension):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

    @commands.command(name='emojiid' , aliases=["ei"])
    @commands.is_owner()
    async def EmojiID(self, ctx:commands.Context , emoji_name:str):
        guilds = self.bot.guilds
        for guild in guilds:
            emoji = [emoji.id for emoji in guild.emojis if emoji.name == emoji_name]
            if len(emoji) > 0:
                await ctx.send(str(emoji))
            
async def setup(bot:commands.Bot):
    cog = commandEmojiID(bot)
    await bot.add_cog(cog)