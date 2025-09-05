import discord
from discord.ext import commands
from xiancord import terminal
from typing import Union

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
    
def discord_name(member : discord.Member , return_id : bool = False):
    name = ""
    if member.guild and member.nick:
        name = member.nick
    elif member.display_name:
        name = member.display_name
    elif member.global_name:
        name =  member.global_name
    else: name = member.name
    return f"{name} ( {member.id} )" if return_id else name
