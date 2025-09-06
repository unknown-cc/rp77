import discord
from discord.ext import commands
from xiancord import terminal
from typing import Union
import asyncio
import edge_tts
import os
import uuid

class VoiceQueue:
    def __init__(self):
        self.bot : commands.Bot = None
        self.queue_dict : dict[int, asyncio.Queue] = {}     # guild_id -> Queue
        self.task_dict : dict[int, asyncio.Task] = {}       # guild_id -> Task

    async def bot_in_voice_channel(self, voice_channel_id:int) -> Union[discord.VoiceClient, None]:
        if not self.bot:
            terminal("未設置 bot" , "bot_in_voice_channel")
            return
        bot = self.bot
        voice_channel = bot.get_channel(voice_channel_id)
        if not voice_channel:
            terminal(f"找不到頻道 {voice_channel_id}","語音播放")
            return

        # guild_id = voice_channel.guild.id
        # terminal("guild_id" + str(guild_id) , "bot_in_voice_channel")
        # terminal(f"guild_id : {guild_id}")
        vc = discord.utils.get(self.bot.voice_clients , guild = voice_channel.guild)
        # terminal(f"vc1:{vc}")
        if vc:
            terminal(vc.channel)
            if vc.channel.id != voice_channel.id:
                await vc.disconnect()
                await voice_channel.connect()
        else:
            vc = await voice_channel.connect()
        # terminal("vc :" + str(vc) , "bot_in_voice_channel")
        return vc

    async def add_to_queue(self, voice_channel_id, content, type="text", volume=0.5, leave=False, delete_file=False):
        guild_id = self.bot.get_channel(voice_channel_id).guild.id
        queue = self.queue_dict.setdefault(guild_id, asyncio.Queue())
        await queue.put((voice_channel_id, content, type, volume, leave, delete_file))

        if guild_id not in self.task_dict or self.task_dict[guild_id].done():
            self.task_dict[guild_id] = asyncio.create_task(self._player_loop(guild_id))

    async def _player_loop(self, guild_id:int):
        queue = self.queue_dict[guild_id]
        while True:
            voice_channel_id, content, type, volume, leave, delete_file = await queue.get()
            # terminal("開始", "_play_next")

            if type == "text":
                file = await self.text_speak(content)
            elif type == "file":
                file = content

            # terminal(file, "_play_next")

            if queue.qsize() > 3:
                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(file, options='-filter:a "atempo=1.5"'),
                    volume=volume
                )
            else:
                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(file),
                    volume=volume
                )

            while not os.path.exists(file):
                await asyncio.sleep(0.1)
            # terminal("exist" , "_play_next")
            vc = await self.bot_in_voice_channel(voice_channel_id)
            # terminal(vc , "_play_next")
            if not vc:
                terminal("no vc" , "_play_next")
                continue

            vc.play(source)
            while vc.is_playing():
                await asyncio.sleep(0.1)

            if delete_file:
                os.remove(file)

            if queue.empty() and leave:
                await vc.disconnect()

            # terminal("結束", "_play_next")

    async def text_speak(self, text:str):
        file = f"speak_{uuid.uuid4().hex}.mp3"
        voice = "zh-TW-HsiaoChenNeural"  # 甜美女聲
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(file)
        return file
