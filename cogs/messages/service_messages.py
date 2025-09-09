from random import sample
import os
import traceback
import discord
from discord.ext import commands
import emoji
from xiancord.core import Cog_Extension
from xiancord.logger import terminal
from xiancord.database import db , db_init
from xiancord.time import now_offset
from xiancord.utils import discord_name , find1
from xiancord.voice import voice_queue
from xiancord.rate_limiter import global_rate_limiter
import re
import asyncio
import logging
logging.basicConfig(level=logging.INFO)

MAIN_GUILD = 1307808857858244629
SUB_GUILD = 0
MAIN_CHANNEL_ID = 1406370066404216912
SUB_CHANNEL_ID = 1413338432247304353
READY_EMOJI = "<a:load:972447733971550220>"
MAKED_EMOJI = "<a:ding1:1004602332971028581>"
FINISH_EMOJI = "<a:check4:972447733740867654>"
ERROR_EMOJI = "<a:no2:972097574343430174>"
VOICE_CHANNEL_ID1 = 1383475662546931804
# VOICE_CHANNEL_ID2 = 1411635241142980609 # 需不同 guild

class service_messages(Cog_Extension):
    def __init__(self, bot:commands.Bot):
        super().__init__(bot)
        self.event = "業務事件"

    async def speak1(self , voice_text , * , ding = True):
        if ding:
            await voice_queue.add_to_queue(VOICE_CHANNEL_ID1 , "cash-register-kaching-sound-effect-125042" , type="file" , volume=0.2 , delete_file=False)
        await voice_queue.add_to_queue(VOICE_CHANNEL_ID1 , voice_text , type="text" , volume=1.0 , delete_file= True)
    
    def get_rpnick_name(self , member : discord.Member):
        main_guild = self.bot.get_guild(MAIN_GUILD)
        main_member = main_guild.get_member(member.id)
        member_nick = discord_name(member)
        if main_member :
            return find1(r'[|｜]\s*([^\s]+)\s*$' , member_nick)
        else:
            return member_nick

    @commands.Cog.listener("on_message")
    async def on_message(self , message:discord.Message):
        try:
            # test
            # guild = self.bot.get_guild(1307808857858244629)
            # channel = self.bot.get_channel(1406370066404216912)
            # author = message.author
            # if  author.id == 1004239226688241676 :
            #     async for m in channel.history():
            #         if m.id == 1414760762211303496:
            #             message = m
            #     terminal(message.content)
            #     terminal(message.mentions)
            #     terminal(message.role_mentions)

            # 
            
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
            if not "玩家" in content or not "購買項目" in content : 
                for role in member.roles:
                    if "九龍堂" in role.name : return                        
                else:                    
                    if not member.guild_permissions.administrator :
                        if not member.id == 1004239226688241676:
                            embed = discord.Embed(description=f"{ERROR_EMOJI} 未依格式填寫或標註成員" , colour=discord.Colour.red())
                            await channel.send(content=f"-# <t:{int(now_offset(seconds=30).timestamp())}:R>自動刪除此訊息" , embed=embed , delete_after=30 ,reference=message)
                            await message.add_reaction(ERROR_EMOJI)
                            return
            if not (message.mentions or message.role_mentions)  : return
            if not ("玩家" in content and "購買項目" in content): return
            if message.mentions:
                for member in message.mentions:
                    content = content.replace(member.mention , f"@{member.nick} ({member.id})")
            elif message.role_mentions:
                for role in message.role_mentions:
                    content = content.replace(role.mention , f"@{role.name} ({role.id})")

            content = f"<@&1413338884800249936> [業務連結]({message.jump_url})\n" + content + f"\n-# {READY_EMOJI}﹡接單 \n-# {MAKED_EMOJI}﹡通知客人領取\n-# {FINISH_EMOJI}﹡完成業務\n "
            sub_channel = self.bot.get_channel(SUB_CHANNEL_ID)
            await sub_channel.send(content=content)
            # 子群：綁定接單人員
            
            # main_guild = self.bot.get_guild(MAIN_GUILD)            
            # staff = main_guild.get_member(828496960625442836)

            # embed = discord.Embed(description=f"接單人員：{staff.mention}" , colour=discord.Colour.blue())
            # await msg.edit(embed=embed)
            # if member.voice :
            #     if member.voice.channel.guild.id == MAIN_GUILD:
            #         # 語音提示 -> 客人
            #         voice_text = f"{str(member_name)} 您好，您的訂單正在處理當中，製作完畢會再次通知您。請稍候..."
            #         await voice_queue.add_to_queue(member.voice.channel.id , voice_text ,type="text" , volume=1.0 , leave=True , delete_file=True)
            # 大群：通知已接單
            # embed = discord.Embed(description=f"{staff.mention} 已接單\n製作完成將會通知您到據點領取\n\n如果您在任意市民的語音頻道中，\n我們會用語音呼叫您，請稍候..." , colour=discord.Colour.orange())
            # async def reaction():
            #     # await message.channel.send(embed=embed , reference=message)
            #     await message.clear_reaction(READY_EMOJI)
            #     await message.add_reaction(MAKED_EMOJI)
            #     await message.add_reaction(FINISH_EMOJI)
            # asyncio.create_task(reaction())

            # await msg.add_reaction(READY_EMOJI)
            # 語音提示
            voice_text = "業，務，有，單，誰要接呢？"
            await self.speak1(voice_text)
        except Exception as e:
            terminal(e)

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self , payload : discord.RawReactionActionEvent):
        try:
            # 參數
            message = None
            channel = self.bot.get_channel(payload.channel_id) # 業務通知的頻道
            safe_channel = global_rate_limiter.get(channel)
            # 子群
            guild = channel.guild
            # 處理員工
            staff = payload.member
            # 機器人點按鈕 返回
            if not channel.id == SUB_CHANNEL_ID: return
            if staff.bot : return
            # 接單人員
            # terminal(staff)
            staff_name = self.get_rpnick_name(staff)
            staff_name = ''.join(c for c in staff_name if not emoji.is_emoji(c))

            # terminal(staff_name)
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
            # 買家
            member = origin_message.author
            member_name = self.get_rpnick_name(member)
            member_name = ''.join(c for c in member_name if not emoji.is_emoji(c))
            
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
                # 子群：綁定接單人員
                embed = discord.Embed(description=f"接單人員：{staff.mention}" , colour=discord.Colour.blue())
                await message.edit(embed=embed)
                # 獲取成員的 vc 狀態
                if member.voice :
                    if member.voice.channel.guild.id == MAIN_GUILD:
                        # 語音提示 -> 客人
                        voice_text = f"{str(member_name)} 您好，您的訂單正在處理當中，製作完畢會再次通知您。請稍候..."
                        await voice_queue.add_to_queue(member.voice.channel.id , voice_text ,type="text" , volume=1.0 , leave=True , delete_file=True)
                # 大群：通知已接單
                embed = discord.Embed(description=f"{staff.mention} 已接單\n製作完成將會通知您到據點領取\n\n如果您在任意市民的語音頻道中，\n我們會用語音呼叫您，請稍候..." , colour=discord.Colour.orange())
                async def reaction():
                    await safe_main_channel.send(embed=embed , reference=origin_message)
                    await message.clear_reaction(READY_EMOJI)
                    await message.add_reaction(MAKED_EMOJI)
                    await message.add_reaction(FINISH_EMOJI)
                asyncio.create_task(reaction())
                # 子群：避免搶單
                # embed = discord.Embed(description=f"{READY_EMOJI} 避免搶單提醒：{staff.mention} 正在處理此業務...." , colour=discord.Colour.orange())
                # await safe_channel.send(content=f"-# <t:{int(now_offset(seconds=60).timestamp())}:R>自動刪除此訊息" , embed=embed , delete_after=60,reference=message)
                voice_text = f"{staff_name} 正在處理 {member_name} 的業務"
                await self.speak1(voice_text , ding=False)

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
                embed = discord.Embed(description=f"{MAKED_EMOJI} {origin_message.author.mention} 您的訂單已製作完成。\n請您至地圖440，右手邊斜坡上方－九龍堂的據點領取" , colour=discord.Colour.yellow())
                await message.remove_reaction(MAKED_EMOJI , staff)
                await safe_main_channel.send(embed=embed , reference=origin_message)
                # 獲取成員的 vc 狀態
                if member.voice:
                    if member.voice.channel.guild.id == MAIN_GUILD:
                        voice_text = f"{str(member_name)} 您好，您的訂單已製作完畢，請您至地圖440，右手邊斜坡上方－九龍堂的據點領取！"
                        await voice_queue.add_to_queue(member.voice.channel.id , voice_text ,type="text" , volume=1.0 , leave=True , delete_file=True)
                voice_text = f"{staff_name} 已通知 {member_name} 前來取貨"
                await self.speak1(voice_text , ding=False)
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

                voice_text = f"{staff_name} 已將 {member_name} 的訂單處理完畢"
                await self.speak1(voice_text , ding=False)
        except Exception as e:
            terminal(e)
            traceback.print_exc()

async def setup(bot:commands.Bot):
    await bot.add_cog(service_messages(bot))