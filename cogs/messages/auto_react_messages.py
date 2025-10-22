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

class auto_react_messages(Cog_Extension):
    def __init__(self, bot:commands.Bot):
        super().__init__(bot)
        self.event = "業務事件"
        self.react_channels = [
            1429801527844933724,
            1429486671291748513,
        ]

    @commands.Cog.listener("on_message")
    async def on_message(self , message:discord.Message):
        if not message.guild: return
        if message.author.bot : return
        channel = message.channel
        try:
            if not channel.id in self.react_channels:return
            await message.add_reaction(emojigot('check4'))
        except :
            traceback.print_exc()
            
            
async def setup(bot:commands.Bot):
    await bot.add_cog(auto_react_messages(bot))