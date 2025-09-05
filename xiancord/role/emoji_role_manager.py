import ast
from xiancord import terminal
from xiancord.utils import fetch_message
from discord import RawReactionActionEvent
from discord.ext import commands
from typing import Union
import discord
class Emoji_Role:
    def __init__(self, bot : commands.Bot):
        self.event = "class:Emoji_Role"
        self.bot = bot
        self.__ermap__ : dict[int , dict[str , int]]= {}
        self.__mcmap__ : dict[int , Union[discord.abc.MessageableChannel]]= {}

    async def init(self, data_list: list[dict[str , str]]):
        if not len(data_list):
            return terminal("尚未找到任何資料", self.event)

        for data in data_list:

            channel_id = data.get("channel_id")
            message_id = data.get("message_id")
            er_map = data.get("emoji_role")
            try:
                er_map = ast.literal_eval(er_map)  # 轉換字串為 Python 資料型態
            except (ValueError, SyntaxError) as e:
                return terminal(f"資料轉型錯誤，錯誤訊息: {str(e)}", self.event)
            if not isinstance(er_map, dict):
                return terminal(f"資料無法轉型成 dict , 轉型結果 : {er_map}", self.event)

            channel = self.bot.get_channel(int(channel_id))
            if not isinstance(channel, discord.abc.GuildChannel):
                return terminal(f"頻道id : {channel_id} 無法獲取 channel 類型, 結果 : {channel}", self.event)

            message = await fetch_message(channel, message_id)
            if not isinstance(message, discord.Message):
                return terminal(f"訊息id : {message_id} 無法獲取 message 類型, 結果 : {message}", self.event)
            self.__ermap__.setdefault(message.id , {})
            for emoji , role_id in er_map.items():
                self.__ermap__[message.id][emoji] = role_id
            self.__mcmap__[message.id] = channel
            
    async def verify_action(self, payload :RawReactionActionEvent):
        if not payload.message_id in self.__mcmap__.keys() :
            return terminal(f"message_id : {payload.message_id} 不在 self.__cmsmap__.keys()", self.event)
        guild = self.__mcmap__[payload.message_id].guild
        er_map = self.__ermap__[payload.message_id]
        emoji = payload.emoji
        emoji_str = emoji.name if emoji.is_unicode_emoji() else str(emoji)
        if not emoji_str in er_map.keys():
            return terminal(f"emoji_str : {emoji_str} 不在 er_map.keys()", self.event)
        
        role = guild.get_role(er_map[emoji_str])
        member = payload.member
        member_rolesid = [role.id for role in member.roles]
        if payload.event_type == "REACTION_ADD":
            await member.add_roles(role)
        elif payload.event_type == "REACTION_REMOVE":
            await member.remove_roles(role)

        