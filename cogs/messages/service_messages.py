from random import sample
import os
import discord
from discord.ext import commands
from xiancord.core import Cog_Extension
from xiancord.logger import terminal
from xiancord.database import db , db_init
from xiancord.time import now_offset
from xiancord.rate_limiter import global_rate_limiter
import re
import asyncio
import logging
logging.basicConfig(level=logging.INFO)

MAIN_GUILD = 1307808857858244629
SUB_GUILD = 1383475660646907966
MAIN_CHANNEL_ID = 1406370066404216912
SUB_CHANNEL_ID = 1413338432247304353
READY_EMOJI = "<a:load:972447733971550220>"
MAKED_EMOJI = "<a:ding1:1004602332971028581>"
FINISH_EMOJI = "<a:check4:972447733740867654>"

class service_messages(Cog_Extension):
    def __init__(self, bot:commands.Bot):
        super().__init__(bot)
        self.event = "業務事件"
        
    @commands.Cog.listener("on_message")
    async def on_message(self , message:discord.Message):
        try:
            message = global_rate_limiter.get(message)
            member = message.author
            if member.bot : return
            guild = message.guild
            channel = message.channel
            channel = global_rate_limiter.get(channel)
            if not (guild.id == MAIN_GUILD and channel.id == MAIN_CHANNEL_ID) : return
            content = message.content
            if ">>" in content and content[:2] == ">>":
                return
            if not "玩家" in content or not "購買項目" in content or not message.mentions: 
                for role in member.roles:
                    if "九龍堂" in role.name : break
                else:                    
                    if not member.guild_permissions.administrator :
                        if not member.id == 1004239226688241676:
                            embed = discord.Embed(description=f"❌ 未依格式填寫或標註成員" , colour=discord.Colour.red())
                            await channel.send(content=f"-# <t:{int(now_offset(seconds=30).timestamp())}:R>自動刪除此訊息" , embed=embed , delete_after=30 ,reference=message)
                            await message.add_reaction("❌")
                            return
            if not ("玩家" in content and "購買項目" in content): return
            content = f"<@&1413338884800249936> [業務連結]({message.jump_url})\n" + content + f"\n-# {READY_EMOJI}﹡接單 \n-# {MAKED_EMOJI}﹡通知客人領取\n-# {FINISH_EMOJI}﹡完成業務\n "
            sub_channel = self.bot.get_channel(SUB_CHANNEL_ID)
            msg = await sub_channel.send(content=content)
            await msg.add_reaction(READY_EMOJI)
        except Exception as e:
            terminal(e)

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self , payload : discord.RawReactionActionEvent):
        try:
            # 參數
            message = None
            channel = self.bot.get_channel(payload.channel_id) # 業務通知的頻道
            safe_channel = global_rate_limiter.get(channel)
            guild = channel.guild
            staff = payload.member
            # 機器人點按鈕 返回
            if not channel.id == SUB_CHANNEL_ID: return
            if staff.bot : return
            # 查找添加反應的訊息
            async for m in channel.history():
                if m.id == payload.message_id and m.author.bot:
                    message = m
                    break
            # 抓取內容
            content = message.content
            # 分析各行
            lines = content.split("\n")
            origin_message_id = 0
            for line in lines:
                # 查找業務訊息ID
                if "http" in line:
                    matched = re.search(r"/(\d+)$", line[:-1])
                    if matched : 
                        origin_message_id = int(matched.group(1))
            # 抓取業務訊息物件
            main_channel = self.bot.get_channel(MAIN_CHANNEL_ID)
            origin_message = None
            # 翻找訊息
            async for m in main_channel.history():
                if m.id == origin_message_id:
                    origin_message = global_rate_limiter.get(m)
            safe_main_channel = global_rate_limiter.get(main_channel)
            
            if str(payload.emoji) == READY_EMOJI:
                for reaction in message.reactions:
                    if reaction.emoji == READY_EMOJI:
                        async for user in reaction.users():
                            if user.id == self.bot.user.id:
                                break
                        else:
                            await message.remove_reaction(payload.emoji , staff)
                            return
                embed = discord.Embed(description=f"接單人員：{staff.mention}" , colour=discord.Colour.blue())
                await message.edit(embed=embed)
                embed = discord.Embed(description=f"{staff.mention} 已接單，製作完成將會通知您到據點領取，請稍後..." , colour=discord.Colour.orange())
                await safe_main_channel.send(embed=embed , reference=origin_message)
                await message.clear_reaction(READY_EMOJI)            
                await message.add_reaction(MAKED_EMOJI)
                await message.add_reaction(FINISH_EMOJI)
                embed = discord.Embed(description=f"{READY_EMOJI} 避免搶單提醒：{staff.mention} 正在處理此業務...." , colour=discord.Colour.orange())
                await safe_channel.send(content=f"-# <t:{int(now_offset(seconds=60).timestamp())}:R>自動刪除此訊息" , embed=embed , delete_after=60,reference=message)
            if not message.embeds:
                return
            desc = message.embeds[0].description
            staff_id = 0
            matched = False
            if isinstance(desc , str):
                matched = re.search(r"(\d+)>", desc)
                if matched :
                    staff_id = int(matched.group(1))
            if str(payload.emoji) == MAKED_EMOJI:
                if matched:
                    if not staff.id == staff_id:
                        await message.remove_reaction(payload.emoji , staff)
                        return
                embed = discord.Embed(description=f"{MAKED_EMOJI} 貨物已製作完成，{origin_message.author.mention} 請至據點領取" , colour=discord.Colour.yellow())
                await message.remove_reaction(MAKED_EMOJI , staff)
                await safe_main_channel.send(embed=embed , reference=origin_message)
            
            if str(payload.emoji) == FINISH_EMOJI:
                if matched:
                    if not staff.id == staff_id:
                        await message.remove_reaction(payload.emoji , staff)
                        return
                await message.clear_reaction(MAKED_EMOJI)
                await message.remove_reaction(FINISH_EMOJI , self.bot.user)
                async for m in main_channel.history():
                    if not m.reference: continue
                    if m.reference.message_id == origin_message.id:
                        if m.author.id ==self.bot.user.id:
                            await m.delete()
                embed = discord.Embed(description=f"{FINISH_EMOJI} 交易已完成" , colour=discord.Colour.green())
                await safe_main_channel.send(content=f"-# <t:{int(now_offset(seconds=10).timestamp())}:R>自動刪除此訊息" , embed=embed , delete_after=10 , reference=origin_message)
                await origin_message.add_reaction(FINISH_EMOJI)
        except Exception as e:
            terminal(e)

async def setup(bot:commands.Bot):
    await bot.add_cog(service_messages(bot))