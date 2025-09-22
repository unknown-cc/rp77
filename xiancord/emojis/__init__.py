from discord import PartialEmoji
from discord.ext import commands
from ..logger import terminal

__all__ = ["emojis_init" , "emojigot"]

EMOJI_MAP = {}

def emojis_init(bot : commands.Bot):
    # terminal(bot.emojis)
    terminal("正在加載 emoji......" , "xiancord.emojis")
    global EMOJI_MAP
    if not bot.emojis : 
        terminal(f"bot.emojis 為 None" , "xiancord.emojis")
        terminal(f"emojis 加載失敗" , "xiancord.emojis") ; return
    EMOJI_MAP = {}
    for emoji in bot.emojis:
        if emoji.name in EMOJI_MAP : terminal(f"表情 : {emoji.name} －存在重複名稱於 {emoji.guild.name}" , "xiancord.emoji") ; continue
        EMOJI_MAP[emoji.name] = {"id" : emoji.id , "a" : emoji.animated} 
    terminal("emoji 加載完畢" , "xiancord.emojis")
    # terminal(EMOJI_MAP)

def emojigot(name:str):
    global EMOJI_MAP
    # terminal(EMOJI_MAP , "xiancord.emojis.emojigot")
    data = EMOJI_MAP.get(name , None)
    if not data : return None
    return PartialEmoji(name=name , id=data["id"] , animated=data["a"])