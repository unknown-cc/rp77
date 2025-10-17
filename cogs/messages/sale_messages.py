from random import sample
import os
import traceback
from typing import Union
import discord
from discord.ext import commands
from xiancord.core import Cog_Extension
from xiancord.logger import terminal
from xiancord.database import db , db_init
from xiancord.time import now_offset
from xiancord.utils import discord_name , find1 , has_reacted , emojiify , chunk_text
from xiancord.emojis import emojigot
from xiancord.rate_limiter import global_rate_limiter
from discord import ButtonStyle , Interaction ,TextStyle , Embed , Colour
from discord.ui import Button , View , Modal , TextInput
import re
import asyncio
import logging
from PIL import Image
from io import BytesIO
import aiohttp
import textwrap
logging.basicConfig(level=logging.INFO)


SALE_CHANNEL_ID = 1425796620754227291
MAX_SIZE = 8 * 1024 * 1024  # 最大附件大小 8MB
SALE_EMBED_TITLE = f"{emojigot('king1')} 銷售回報"
SALE_EMBED_STUFF = f"{emojigot('AnimeDot_cyan')} 銷售人員"
SALE_EMBED_BEFORE = f"{emojigot('AnimeDot_orange')} 存入前"
SALE_EMBED_AMOUNT = f"{emojigot('money1')} 銷售金額"
SALE_EMBED_AFTER = f"{emojigot('AnimeDot_green')} 存入後"
ROLE_ID = 1425797699810361344

# 將 Discord 附件轉成 discord.File，超過大小嘗試壓縮
async def attachment_to_file(att: discord.Attachment) -> discord.File | None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(att.url) as resp:
                if resp.status != 200: return None
                data = await resp.read()
        if len(data) <= MAX_SIZE: return discord.File(BytesIO(data), filename=att.filename)
        try:
            img = Image.open(BytesIO(data))
            output = BytesIO()
            img.save(output, format=img.format, optimize=True, quality=85)
            output.seek(0)
            if output.getbuffer().nbytes > MAX_SIZE: return None
            return discord.File(fp=output, filename=att.filename)
        except: return None
    except: return None

def parse_wan_amount(content:str):
    amount = None
    multiplier = 1
    if not content : return None
    if content.endswith(("w" , "W" ,"萬")) :
        amount = content[:-1]
        multiplier = 10000
    else:
        amount = content
    try:
        amount = float(amount) * multiplier
        return amount
    except ValueError:
        return None

def amount_to_wan(amount : float):
    # 否則，執行萬單位轉換
    return f"{amount / 10000:g}w" if amount != 0 else "0"

class SaleBaseView(View):
    def __init__(self , bot : commands.Bot, *, timeout = None):
        super().__init__(timeout=timeout)
        self.bot = bot
    
    @discord.ui.button(label="上級:簽核" , style=ButtonStyle.grey , emoji=emojigot('king1') , custom_id="SignButton")
    async def SignButtonCallback(self , interaction : Interaction , button : Button):
        if not await self.SignButtonCallback_interaction_check(interaction):return
        channel = interaction.channel
        money = parse_wan_amount(channel.topic)
        if money == None : 
            await interaction.response.defer()
            # topic 並非金額格式
            return
        embed = interaction.message.embeds[0]
        try:
            amount = next(
                field.value for field in embed.fields
                if field.name == SALE_EMBED_AMOUNT
            )
            amount = parse_wan_amount(amount)
            if not amount :
                terminal("amount 是 None")
                #存入金額不正常
                return
        except StopIteration:
            # 未知錯誤
            return
        await channel.edit(topic=amount_to_wan(money + amount))
        await interaction.response.edit_message(view=None)
        await interaction.message.add_reaction(emojigot('AnimeInk_7'))

    async def SignButtonCallback_interaction_check(self , interaction:Interaction):
        member = interaction.user
        if member.guild_permissions.administrator : return True
        for role in member.roles:
            if role.id == ROLE_ID: return True
        else:
            await interaction.response.send_message(f"{emojigot('no3')} 你不是簽核人員" , ephemeral=True)
            return False
        
    @discord.ui.button(label="刪除" , style=ButtonStyle.red , custom_id="delete" , emoji=emojigot('warning2'))
    async def DeleteButtonCallback(self , interaction : Interaction , button : Button):
        origin_message = interaction.message
        embed = origin_message.embeds[0]
        try:
            author_mention = next(
                field.value for field in embed.fields
                if field.name == SALE_EMBED_STUFF
            )
        except StopIteration:pass
        for role in interaction.user.roles:
            if role.id == ROLE_ID:
                break
        else:
            if not interaction.user.guild_permissions.administrator:
                if not interaction.user.mention == author_mention:
                    await interaction.response.send_message(f"{emojigot('no3')} 你不可刪除他人的回報" , ephemeral=True , delete_after= 20)
                    return
        button.label = "執行中"
        button.emoji = emojigot('load')
        button.disabled = True
        for child in self.children:
            if isinstance(child , Button):
                if child.custom_id == "SignButton":
                    self.remove_item(child)
        await interaction.response.edit_message(view=self)
        channel = interaction.channel
        before_message = None
        try:
            before_message = await anext(
                message async for message in channel.history(before=origin_message.created_at , limit=20)
                if message.author.id == self.bot.user.id and message.embeds
            )
        except StopAsyncIteration:
            pass
            # terminal("before_message = None")
        if not before_message:
            money = parse_wan_amount(channel.topic)
        else:
            embed = before_message.embeds[0]
            try:
                value = next(
                    field.value for field in embed.fields
                    if field.name == SALE_EMBED_AFTER
                )
                money = parse_wan_amount(value)
            except StopIteration:pass
        if money == None:
            terminal("money = None")
            return
        async for message in channel.history(limit=9999 , after=origin_message.created_at , oldest_first=True):
            if message.author.id == self.bot.user.id and message.embeds:
                embed = message.embeds[0]
                # new_embed = embed.copy()
                try:
                    value = next(
                        field.value for field in embed.fields
                        if field.name == SALE_EMBED_AMOUNT
                    )
                    amount = parse_wan_amount(value)
                except StopIteration : pass
                for i , field in enumerate(embed.fields):
                    if field.name == SALE_EMBED_BEFORE:
                        embed.set_field_at(i , name=field.name ,value=amount_to_wan(money))
                    if field.name == SALE_EMBED_AFTER:
                        embed.set_field_at(i , name=field.name ,value=amount_to_wan(money+amount))
                safe_message=global_rate_limiter.get(message)
                await safe_message.edit(embed=embed)
                money = money + amount
                
        await interaction.message.delete()

class sale_messages(Cog_Extension):
    def __init__(self, bot:commands.Bot):
        super().__init__(bot)
        self.event = "銷售頻道"

    # 監聽訊息，建立公告預覽
    @commands.Cog.listener("on_message")
    async def on_message(self , message:discord.Message):
        author = message.author
        # 忽綠 bot 訊息
        if author.bot : return
        # 忽略私人訊息
        guild = message.guild
        if not guild : return
        # 指定頻道 ID
        channel = message.channel
        if not channel.id == SALE_CHANNEL_ID: return
        # 內容
        content = message.content
        # 辨別訊息夾帶檔案
        attachments = message.attachments
        # 忽略未夾帶檔案
        if not attachments : return
        files = []
        for attachmnent in attachments:
            file = await attachment_to_file(attachmnent)
            if file : files.append(file)
        # 變數 : 目前公款
        amount = parse_wan_amount(content)
        if not amount:
            # 輸入的訊息不是金額格式
            return
        # 取出 topic
        # money = parse_wan_amount(channel.topic)
        # if not money :
        #     # 頻道 topic 不是金額格式
        #     return
        try:
            last_bot_message = await anext(
                message async for message in channel.history(limit=20)
                if message.author.id == self.bot.user.id and message.embeds
            )
        except StopAsyncIteration:
            last_bot_message = None

        if not last_bot_message:
            topic = channel.topic
            money = parse_wan_amount(topic)
            if money==None :
                await message.channel.send(f"{emojigot('no3')} 頻道主題未被正確設置" , delete_after=20);return
        else:
            embed = last_bot_message.embeds[0]
            try:
                money = next(
                    field.value for field in embed.fields
                    if field.name == SALE_EMBED_AFTER
                )
            except StopIteration:
                #無法取得上次金額
                pass
            money = parse_wan_amount(money)
        if money == None:
            terminal("money 是 None")
            return
        embed = Embed(title=SALE_EMBED_TITLE , colour=Colour.yellow())
        embed.add_field(name=SALE_EMBED_STUFF , value=f"{author.mention}" , inline=False)
        embed.add_field(name=SALE_EMBED_BEFORE , value=amount_to_wan(money))
        embed.add_field(name=SALE_EMBED_AMOUNT , value=amount_to_wan(amount))
        embed.add_field(name=SALE_EMBED_AFTER , value=amount_to_wan(money + amount))
        embed.set_thumbnail(url=author.avatar.url)
        
        await message.delete()
        await channel.send(embed=embed , view=SaleBaseView(bot=self.bot) , files=files)

# Cog 註冊
async def setup(bot:commands.Bot):
    await bot.add_cog(sale_messages(bot))
    bot.add_view(SaleBaseView(bot=bot))