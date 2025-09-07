from random import sample
import os
import discord
import aiohttp
from discord.ext import commands , tasks
from xiancord.core import Cog_Extension
from xiancord.logger import terminal
from xiancord.database import db , db_init
from xiancord.time import now_offset
from xiancord.rate_limiter import global_rate_limiter
from xiancord.utils import find1
from xiancord.voice import voice_queue
import re
import asyncio
import logging
import edge_tts
import librosa
import soundfile as sf
logging.basicConfig(level=logging.INFO)

MAIN_GUILD = 1307808857858244629
# SUB_GUILD = 1383475660646907966
MAIN_CHANNEL_ID = 1393244497525215262
# READY_EMOJI = "<a:load:972447733971550220>"
# MAKED_EMOJI = "<a:ding1:1004602332971028581>"
# FINISH_EMOJI = "<a:check4:972447733740867654>"
VOICE_CHANNEL_ID = 1383475662546931804

class entry_messages(Cog_Extension):
    def __init__(self, bot:commands.Bot):
        super().__init__(bot)
        self.event = "業務事件"
        # self.server_url = "http://103.122.191.68:30120"
        # self.channel_id = 1411423445794689195  # ⚠️ 換成你的 Discord 頻道 ID


    @commands.Cog.listener("on_message")
    async def on_message(self , message:discord.Message):
        # test 用
        # if not message.content == "." : return
        # if not message.channel.id == 1411423445794689195 : return
        # channel = self.bot.get_channel(1393244497525215262)
        # message = [m async for m in channel.history() if m.id == 1413781376892796938][0]
        # 指定頻道 [實踐]
        if not message.channel.id == MAIN_CHANNEL_ID : return
        if not message.author.bot : return
        # 如果沒有 embed
        if not message.embeds : return
        embed = message.embeds[0]
        if not isinstance(embed , discord.Embed) : return
        # 如果標題錯誤
        if not embed.title == "工作狀態更新" : return
        desc = embed.description
        # 過濾警察
        if not "police" in desc : return
        lines = desc.split("\n")
        # 變數
        player_name = None
        status = None
        # 分析每行
        for line in lines:
            if "玩家名稱" in line:
                player_name = find1(r"玩家名稱/職業/標籤：\*\* (.+?) \[" , line).replace(" " , "")
            if "職業狀態" in line:
                status = find1(r"職業狀態：\*\* (.+)" , line)
        if not (player_name and status) : return
        #輸出內容
        if status == "上班":
            text = f'注意：警察{player_name}{status}了'
        else:
            text = f'警察{player_name}{status}了'
        # await voice_queue.add_to_queue(VOICE_CHANNEL_ID , "anime-wow-sound-effect.mp3" , type="file" , volume=0.2 , delete_file=False)
        await voice_queue.add_to_queue(VOICE_CHANNEL_ID , text , type="text" , volume=1.0 , delete_file=True)
        

async def setup(bot:commands.Bot):
    await bot.add_cog(entry_messages(bot))