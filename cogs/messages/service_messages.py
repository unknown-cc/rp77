from random import sample
import os
import discord
from discord.ext import commands
from xiancord.core import Cog_Extension
from xiancord.logger import terminal
from xiancord.database import db , db_init
from xiancord.time import now_offset
import asyncio
import logging
logging.basicConfig(level=logging.INFO)

MAIN_GUILD = 1128943925516828672
SUB_GUILD = 0
MAIN_CHANNEL_ID = 1411423445794689195
SUB_CHANNEL_ID = 1411423445794689195
READY_EMOJI = "🔄"
FINISH_EMOJI = "✅"

class service_messages(Cog_Extension):
    def __init__(self, bot:commands.Bot):
        super().__init__(bot)
        self.event = "業務事件"
        
    @commands.Cog.listener("on_message")
    async def on_message(self , message:discord.Message):
        try:
            if message.author.bot : return
            guild = message.guild
            channel = message.channel
            if not (guild.id == MAIN_GUILD and channel.id == MAIN_CHANNEL_ID) : return
            content = message.content
            if ">>" in content and content[:2] == ">>":
                terminal()
                return

            if not "玩家" in content or not "購買項目" in content or not message.mentions: 
                await channel.send("❌未依格式填寫" , delete_after=30)
                await message.add_reaction("❌")
                return
            if not ("玩家" in content and "購買項目" in content): return
            content = ">@&1413338884800249936>\n" + content + "\n-# 接單中◞請按🔄\n-# 完成◞請按✅"
            sub_channel = self.bot.get_channel(SUB_CHANNEL_ID)
            msg = await sub_channel.send(content=content)
            await msg.add_reaction(READY_EMOJI)
        except Exception as e:
            terminal(e)

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self , payload : discord.RawReactionActionEvent):
        try:
            message = None
            channel = self.bot.get_channel(payload.channel_id)
            guild = channel.guild
            member = payload.member
            if member.bot : return
            async for m in channel.history():
                if m.id == payload.message_id and m.author.bot:
                    message = m
                    break
            if payload.emoji.name == READY_EMOJI:
                for reaction in message.reactions:
                    if reaction.emoji == READY_EMOJI:
                        await message.clear_reaction(READY_EMOJI)
                        break
                await message.add_reaction(FINISH_EMOJI)
                embed = discord.Embed(description=f"避免搶單提醒：{member.mention} 正在處理此業務...." , colour=discord.Colour.green())
                await channel.send(content=f"-# <t:{int(now_offset(seconds=600).timestamp())}:R>自動刪除此訊息" , embed=embed , delete_after=600,reference=message)
            if payload.emoji.name == FINISH_EMOJI:
                await message.remove_reaction(FINISH_EMOJI , self.bot.user)
        except Exception as e:
            terminal(e)


async def setup(bot:commands.Bot):
    await bot.add_cog(service_messages(bot))