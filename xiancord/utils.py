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

def emojiify(bot:commands.Bot, content: str) -> str:
    """$emoji_name$ → 伺服器表情，重複名稱取第一個，其餘 terminal 提示"""
    if "$" not in content: return content
    for placeholder in re.findall(r"\$.+?\$", content):
        name, found = placeholder[1:-1], None
        for g in bot.guilds:
            for e in g.emojis:
                if e.name == name:
                    if not found: found = e
                    else: terminal(f"emoji '{name}' 也存在於 {g.name}({g.id})", "解析表情")
        if found:
            fmt = "a" if found.animated else ""
            content = content.replace(placeholder, f"<{fmt}:{found.name}:{found.id}>")
    return content

def chunk_text(text: str, limit: int = 2000):
    """將文字切成不超過 limit，多段 yield，保護 Discord emoji 不被切斷"""
    tokens = re.split(r'(<a?:\w+:\d+>)', text)  # 分割文字與 emoji
    buf = ""
    for t in tokens:
        if len(t) > limit:  # 單個 token 超長（理論上不會是 emoji）
            while len(t) > limit:
                yield t[:limit]
                t = t[limit:]
        if len(buf) + len(t) > limit:
            yield buf
            buf = ""
        buf += t
    if buf:
        yield buf

async def list_emojis(bot: commands.Bot, ctx: commands.Context):
    """列出機器人所有 guild 的表情，長文字自動分段發送"""
    text = ""
    for g in bot.guilds:
        text += f"**{g.name} ({g.id})**\n"
        if not g.emojis : text += "-# (沒有表情)\n"
        else:
            for e in g.emojis:
                text += f"<{'a' if e.animated else ''}:{e.name}:{e.id}> → {e.name} ({e.id})\n"
        text += "\n"  # guild 分隔空行

    for chunk in chunk_text(text):
        await ctx.send(chunk)


async def has_reacted(message:discord.Message, emoji:Union[str,discord.Emoji], user:discord.User) -> bool:
    for r in message.reactions:
        if str(r.emoji) == emoji:
            async for u in r.users():  # async generator
                if u.id == user.id:
                    return True
    return False

