import discord
from discord.ext import commands
from xiancord import terminal
from typing import Union
import re


def find1(pattern: str, text: str) -> Union[str , None]:
    matches = re.findall(pattern, text)
    if len(matches) == 1:
        return matches[0]  # 只有一個匹配 → 回傳那個值
    return None

async def fetch_message(channel:Union[discord.TextChannel , discord.VoiceChannel , discord.Thread] ,
                      message_id:Union[str , int]) -> Union[discord.Message , None]:
    event = "utils.fetch_message"
    try:
        return await channel.fetch_message(int(message_id))
    except discord.NotFound as e:
        terminal(f"找不到訊息 ID : {message_id}" , event)
        return None

# 抓第一條訊息    
async def first_message(channel:Union[discord.TextChannel , discord.VoiceChannel , discord.Thread])-> Union[discord.Message , None]:
    messages = [m async for m in channel.history(limit=1 , after=channel.created_at , oldest_first=True)]
    return messages[0] if messages else None

# 抓最後訊息
async def last_message(channel:Union[discord.TextChannel , discord.VoiceChannel , discord.Thread])-> Union[discord.Message , None]:
    messages = [m async for m in channel.history(limit=1 , oldest_first=False)]
    return messages[0] if messages else None
    
def discord_name(member : Union[discord.User , discord.Member] , return_id : bool = False):
    name = ""
    if not member :
        terminal("member 是 None" , "discord_name")
        return
    if isinstance(member , discord.Member):
        if member.guild and member.nick:
            name = member.nick
    if name == "":
        if member.display_name:
            name = member.display_name
        elif member.global_name:
            name =  member.global_name
        else: name = member.name
    return f"{name} ( {member.id} )" if return_id else name
