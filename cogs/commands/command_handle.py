import sys
import traceback
from xiancord.core import Cog_Extension
from xiancord.logger import terminal
from xiancord.utils import discord_name
import discord
from discord.ext import commands


class command_handle(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.Cog.listener("on_command")
    async def on_command(self , ctx:commands.Context):
        name = discord_name(ctx.author , True)
        terminal(f"{name} 使用了 {ctx.command.name}... " , "指令")
    
    @commands.Cog.listener("on_command_completion")
    async def on_command_completion(self , ctx:commands.Context): 
        name = discord_name(ctx.author , True)
        terminal(f"{name} 使用的指令 {ctx.command.name} : 完成" , "指令")

    @commands.Cog.listener("on_command_error")
    async def on_command_error(self, ctx:commands.Context, error):
        # 這可以防止在 on_command_error 中處理任何帶有本地處理程序的命令。
        if hasattr(ctx.command, 'on_error'):
            return
                
        # 這可以防止在此處處理任何帶有覆蓋的 cog_command_error 的 cog。
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        #忽視找不到指令的錯誤
        ignored = (commands.CommandNotFound, )

        # 允許我們檢查引發並發送到 CommandInvokeError 的原始異常。
        # 如果沒有找到。 我們將異常傳遞給 on_command_error。
        error = getattr(error, 'original', error)

        # 任何被忽略的東西都會返回並阻止任何事情發生。
        if isinstance(error, ignored):
            return

        name = discord_name(ctx.author , True)
        terminal(f"{name} 使用的指令 {ctx.command.name} : 出現錯誤" , "指令")

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} 指令功能已被關閉。')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} 不能被使用在私人訊息中。')
            except discord.HTTPException:
                pass

        else:
            # 所有其他沒有返回的錯誤都在這裡。 我們可以只打印默認的 TraceBack。
            terminal('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


async def setup(bot:commands.Bot):
    await bot.add_cog(command_handle(bot))