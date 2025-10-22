import discord
from discord.ext import commands
from xiancord import terminal
from typing import Union
import asyncio
import edge_tts
import os
import uuid
import traceback
class VoiceQueue:
    def __init__(self):
        self.bot : commands.Bot = None
        self.queue_guild : dict[int, asyncio.Queue] = {}     # guild_id -> Queue
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
        vc = discord.utils.get(self.bot.voice_clients , guild = voice_channel.guild)
        if vc:
            # terminal(vc.channel)
            if vc.channel.id != voice_channel.id:
                await vc.disconnect()
                vc = await voice_channel.connect()
        else:
            vc = await voice_channel.connect()
        return vc

    async def add_to_queue(self, voice_channel_id, content, type="text", volume=0.5, leave=False, delete_file=False , member : discord.Member = None):
        guild_id = self.bot.get_channel(voice_channel_id).guild.id
        queue = self.queue_guild.setdefault(guild_id, asyncio.Queue())
        await queue.put((voice_channel_id, content, type, volume, leave, delete_file , member))

        if guild_id not in self.task_dict or self.task_dict[guild_id].done():
            self.task_dict[guild_id] = asyncio.create_task(self._voice_loop(guild_id))
        
    async def _voice_loop(self, guild_id:int):
        queue = self.queue_guild[guild_id]
        while True:
            voice_channel_id, content, type, volume, leave, delete_file , member = await queue.get()
            # terminal("開始", "_play_next")

            if type == "text":
                file = await self.text_speak(content)
            elif type == "file":
                file = content

            # terminal(file, "_play_next")

            if queue.qsize() > 5:
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

            if isinstance(member, discord.Member):
                if member.voice:
                    voice_channel_id = member.voice.channel.id
            try:
                vc = await self.bot_in_voice_channel(voice_channel_id)
                # terminal(vc , "_play_next")
                if not vc:
                    terminal("no vc" , "_play_next")
                    continue

                vc.play(source)
                while vc.is_playing():
                    await asyncio.sleep(0.1)

            except Exception as e:
                traceback.print_exc()
                terminal(e)

            if delete_file:
                os.remove(file)

            if queue.empty() and leave:
                await vc.disconnect()
                break
                # terminal(f"queue.empyty : {str(queue.empty())}" )
                # terminal(f"leave : {str(leave)}")
            # terminal("結束", "_play_next")

    async def text_speak(self, text:str):
        file = f"speak_{uuid.uuid4().hex}.wav"

        try:
            voice = "zh-TW-HsiaoChenNeural"  # 甜美女聲
            terminal(text)
            communicate = edge_tts.Communicate(text, voice=voice)
            await communicate.save(file)
        except :
            traceback.print_exc()
        return file
