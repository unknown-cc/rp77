from discord.ext import commands
from .VoiceManager import VoiceQueue
voice_queue = VoiceQueue()

async def init_voice_queue(bot:commands.Bot):
    voice_queue.bot = bot