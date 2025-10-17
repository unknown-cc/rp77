from random import sample
import os
import traceback
import discord
from discord.ext import commands
from discord.ui import View , Button , Modal , TextInput , Label
from discord import TextStyle , Embed , ButtonStyle , Interaction , Message
import emoji
from xiancord.core import Cog_Extension
from xiancord.logger import terminal
from xiancord.database import db , db_init
from xiancord.time import now_offset
from xiancord.utils import discord_name , find1 , has_reacted
from xiancord.voice import voice_queue
from xiancord.rate_limiter import global_rate_limiter
from xiancord.emojis import emojigot
import re
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

MAIN_GUILD = 1307808857858244629
SUB_GUILD = 0

MAIN_CHANNEL_ID = 1406370066404216912
SALE_CHANNEL_ID = 1407988870196367391
ORDER_CHANNEL_ID = 1413338432247304353
READY_EMOJI = "<a:load:972447733971550220>"
MAKED_EMOJI = "<a:ding1:1004602332971028581>"
FINISH_EMOJI = "<a:check4:972447733740867654>"
ERROR_EMOJI = "<a:no3:976098818154176553>"
VOICE_CHANNEL_ID1 = 1383475662546931804
# VOICE_CHANNEL_ID2 = 1411635241142980609 # 需不同 guild
DELETE_TIME = 20


def get_rpnick_name(bot : commands.Bot, member : discord.Member):
        main_guild = bot.get_guild(MAIN_GUILD)
        main_member = main_guild.get_member(member.id)
        member_nick = discord_name(member)
        if main_member :
            nick = find1(r'[|｜]\s*([^\s]+)\s*$' , member_nick)
            return nick if nick else member_nick
        else:
            return member_nick
        
async def speak1(voice_text , * , ding = True):
        if ding:
            await voice_queue.add_to_queue(VOICE_CHANNEL_ID1 , "cash-register-kaching-sound-effect-125042.mp3" , type="file" , volume=0.2 , delete_file=False)
        await voice_queue.add_to_queue(VOICE_CHANNEL_ID1 , voice_text , type="text" , volume=1.0 , delete_file= True)

class ServiceBaseView(View):
    def __init__(self, bot : commands.Bot , * ,timeout = None , message : discord.Message = None , staff_id : int = 0 , buyer : discord.Member = None):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.staff_id = staff_id
        self.buyer = buyer
        self.message = message

    async def check_message(self):
        message = self.message
        if not message : return None
        channel = self.bot.get_channel(message.channel.id)
        try:
            message = await channel.fetch_message(message.id)
        except discord.NotFound:
            # terminal(f"找不到訊息 : {self.message.id} ")
            self.message = None ; return None
        if message : 
            self.message = message
            return message
        else:
            self.message = None ; return None

    async def get_staff(self , embed:Embed):
        desc = embed.description
        self.staff_id = 0
        matched = False
        if isinstance(desc , str):
            matched = re.search(r"(\d+)>", desc)
            if matched :
                self.staff_id = int(matched.group(1))

    async def get_origin_message(self , message : Message):
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
            self.buyer = None
            self.message = None
            # 翻找訊息
            async for m in main_channel.history():
                if m.id == origin_message_id:
                    self.buyer = m.author
                    self.message = m
                    break

    async def interaction_check(self, interaction:Interaction):
        if not self.message:
            await self.get_origin_message(interaction.message)
        if not await self.check_message():
            await interaction.response.edit_message(view=BuyerCancelView(self.bot));return
        embeds = interaction.message.embeds
        if not embeds: return True
        embed = embeds[0]
        await self.get_staff(embed)
        if self.staff_id == interaction.user.id:
            return True
        else:
            # await interaction.response.defer()
            return False
class BuyerCancelView(ServiceBaseView):
    def __init__(self, bot, *, timeout=None, message = None, staff_id = 0, buyer = None):
        super().__init__(bot, timeout=timeout, message=message, staff_id=staff_id, buyer=buyer)
    
    @discord.ui.button(label="找不到訂單訊息或買家取消了訂單" , emoji=emojigot("no3") , disabled=True)
    async def NoCallback(self , interaction:Interaction , button : Button):
        pass

class AcceptOrderView(ServiceBaseView):
    def __init__(self, bot, *, timeout=None, message = None, staff_id = 0, buyer = None):
        super().__init__(bot, timeout=timeout, message=message, staff_id=staff_id, buyer=buyer)

    @discord.ui.button(label="接單" , emoji=emojigot("AnimeDot_yellow") ,
                       style=ButtonStyle.grey , custom_id="AcceptOrderButton") 
    async def AcceptOrderButtonCallback(self, interaction : Interaction , button : Button):
        button.disabled = True
        button.label = "處理中..."
        button.emoji = emojigot("load")
        await interaction.response.edit_message(view=self)
        buyer = self.buyer
        # if not origin_message :
        #     await interaction.message.edit(view=BuyerCancelView(self.bot));return
        # origin_message = self.message
        staff = interaction.user
        staff_name = get_rpnick_name(self.bot , staff)
        embed = Embed(description=f"接單人員：{staff.mention}" , colour=discord.Colour.blue())
        await interaction.message.edit(embed=embed , view=OrderProccessingView(bot = self.bot , message=self.message , buyer=self.buyer , staff_id=self.staff_id))
        buyer_name = get_rpnick_name(self.bot , buyer)
        voice_text = f"{staff_name} 正在處理 {buyer_name} 的業務"
        await asyncio.create_task(speak1(voice_text , ding=False))
        self.staff_id = interaction.user.id
        # 獲取成員的 vc 狀態
        if buyer.voice :
            if buyer.voice.channel.guild.id == MAIN_GUILD:
                # 語音提示 -> 客人
                voice_text = f"{str(buyer_name)} 您好，您的訂單正在處理當中，製作完畢會再次通知您。請稍候..."
                await asyncio.create_task(voice_queue.add_to_queue(buyer.voice.channel.id , voice_text ,type="text" , volume=1.0 , leave=True , delete_file=True , member=buyer))
    
class OrderProccessingView(ServiceBaseView):
    def __init__(self, bot, *, timeout=None, message = None, staff_id = 0, buyer = None):
        super().__init__(bot, timeout=timeout, message=message, staff_id=staff_id, buyer=buyer)
    
    @discord.ui.button(label="通知客戶來據點取貨" , emoji=emojigot("AnimeDot_orange") ,
                       style=ButtonStyle.grey , custom_id="NotifyButton")
    async def NotifyButtonCallback(self , interaction : Interaction , button : Button):
        origin_message = self.message
        # if not origin_message :
        #     await interaction.message.edit(view=BuyerCancelView(self.bot));return
        buyer = self.buyer
        embed = Embed(description=f"{emojigot('ding1')} 已通知客戶前來取貨！" , colour=discord.Colour.green())
        await interaction.response.send_message(embed=embed , ephemeral=True , delete_after=DELETE_TIME)
        staff = interaction.user
        staff_name = get_rpnick_name(self.bot , staff)
        buyer_name = get_rpnick_name(self.bot , buyer)
        main_channel = self.bot.get_channel(MAIN_CHANNEL_ID)
        safe_main_channel = global_rate_limiter.get(main_channel)
        embed = discord.Embed(description=f"{MAKED_EMOJI} {origin_message.author.mention} 您的訂單已製作完成。\n請您至地圖440，右手邊斜坡上方－九龍堂的據點領取" , colour=discord.Colour.yellow())
        await asyncio.create_task(safe_main_channel.send(embed=embed , reference=origin_message))
        # 獲取成員的 vc 狀態
        if buyer.voice:
            if buyer.voice.channel.guild.id == MAIN_GUILD:
                voice_text = f"{str(buyer_name)} 您好，您的訂單已製作完畢，請您至地圖440，右手邊斜坡上方－九龍堂的據點領取！"
                await asyncio.create_task(voice_queue.add_to_queue(buyer.voice.channel.id , voice_text ,type="text" , volume=1.0 , leave=True , delete_file=True , member=buyer))
        voice_text = f"{staff_name} 已通知 {buyer_name} 前來取貨"
        await asyncio.create_task(speak1(voice_text , ding=False))
        
    
    @discord.ui.button(label="完成訂單" , emoji=emojigot("AnimeDot_green") ,
                       style=ButtonStyle.grey , custom_id="FinishButton")
    async def FinishButtonCallback(self , interaction : Interaction , button : Button):
        await interaction.response.edit_message(view=None)
        origin_message = self.message
        buyer = self.buyer
        staff = interaction.user
        staff_name = get_rpnick_name(self.bot , staff)
        buyer_name = get_rpnick_name(self.bot , buyer)
        main_channel = self.bot.get_channel(MAIN_CHANNEL_ID)
        safe_main_channel = global_rate_limiter.get(main_channel)
        async for m in main_channel.history():
            if not m.reference: continue
            if m.reference.message_id == origin_message.id:
                if m.author.id ==self.bot.user.id:
                    try:
                        await m.delete()
                    except : pass
        embed = discord.Embed(description=f"{FINISH_EMOJI} 交易已完成" , colour=discord.Colour.green())
        await safe_main_channel.send(content=f"-# <t:{int(now_offset(seconds=DELETE_TIME).timestamp())}:R>自動刪除此訊息" , embed=embed , delete_after=DELETE_TIME , reference=origin_message)
        try:
            await origin_message.add_reaction(FINISH_EMOJI)
        except Exception as e:
            traceback.print_exc()
        voice_text = f"{staff_name} 已將 {buyer_name} 的訂單處理完畢"
        await speak1(voice_text , ding=False)
        try:
            await interaction.message.add_reaction(FINISH_EMOJI)
        except:
            traceback.print_exc()

        # # 銷售回報
        # sale_channel = self.bot.get_channel(SALE_CHANNEL_ID)
        # safe_sale_channel = global_rate_limiter.get(sale_channel)
        # embed = Embed(title="銷售回報")
        # await sale_channel.send()
        
class service_messages(Cog_Extension):
    def __init__(self, bot:commands.Bot):
        super().__init__(bot)
        self.event = "業務事件"

    @commands.Cog.listener("on_message")
    async def on_message(self , message:discord.Message):
        try:
            safe_message = global_rate_limiter.get(message)
            member = message.author
            member_name = get_rpnick_name(self.bot , member)
            if member.bot : return
            guild = message.guild
            channel = message.channel
            channel = global_rate_limiter.get(channel)
            if not (guild.id == MAIN_GUILD and channel.id == MAIN_CHANNEL_ID) : return
            content = message.content
            # 命令返回
            if ">>" in content and content[:2] == ">>" : return
            if not ("玩家" in content and  "購買項目" in content) : return
            if not (message.mentions or message.role_mentions) : 
                for role in member.roles:
                    if "九龍堂" in role.name : return
                else:                    
                    if not member.id == 1004239226688241676 or True:
                        embed = discord.Embed(description=f"{ERROR_EMOJI} 請標註成員或身分組" , colour=discord.Colour.red())
                        await channel.send(content=f"-# <t:{int(now_offset(seconds=DELETE_TIME).timestamp())}:R>自動刪除此訊息" , embed=embed , delete_after=DELETE_TIME ,reference=message)
                        await safe_message.add_reaction(ERROR_EMOJI)
                        return
            if message.mentions:
                for member in message.mentions:
                    content = content.replace(member.mention , f"@{get_rpnick_name(self.bot , member)} ({member.id})")
            elif message.role_mentions:
                for role in message.role_mentions:
                    content = content.replace(role.mention , f"@{role.name} ({role.id})")

            content = f"<@&1413338884800249936> [業務連結]({message.jump_url})\n" + content
            sub_channel = self.bot.get_channel(ORDER_CHANNEL_ID)
            await sub_channel.send(content=content , view=AcceptOrderView(bot = self.bot , message=message , buyer=message.author))
            text = "已收到您的訂單，請耐心等候業務人員接單！"
            embed = Embed(description=f"{emojigot('butterfly1')} {text}" , colour=discord.Colour.green())
            await asyncio.create_task(channel.send(content=f"-# <t:{int(now_offset(seconds=DELETE_TIME).timestamp())}:R>自動刪除此訊息" , embed=embed , delete_after=DELETE_TIME ,reference=message))
            # 獲取成員的 vc 狀態
            if member.voice:
                if member.voice.channel.guild.id == MAIN_GUILD:
                    voice_text = f"{str(member_name)} 您好，{text}"
                    await asyncio.create_task(voice_queue.add_to_queue(member.voice.channel.id , voice_text ,type="text" , volume=1.0 , leave=True , delete_file=True , member=member))
            voice_text = "業，務，有，單，誰要接呢？"
            await asyncio.create_task(speak1(voice_text))
        except Exception as e:
            traceback.print_exc()
            terminal(e)

async def setup(bot:commands.Bot):
    await bot.add_cog(service_messages(bot))
    bot.add_view(AcceptOrderView(bot=bot))
    bot.add_view(OrderProccessingView(bot=bot))

