from discord.ext import commands
from .wrapper import RateLimitedDiscordObject
from typing import TypeVar, cast
from ..logger import terminal
import traceback
T = TypeVar("T")  # 泛型變數

class GlobalRateLimiter:
    def __init__(self):
        self._channel_buckets = {}
        self._member_buckets = {}
        self._guild_buckets = {}
        self._message_buckets = {}

    def get(self, obj: T) -> T:
        if hasattr(obj, 'id'):
            if hasattr(obj, 'send') and callable(obj.send):
                return cast(T, self._wrap(self._channel_buckets, obj))
            elif hasattr(obj, 'add_roles') and callable(obj.add_roles):
                return cast(T, self._wrap(self._member_buckets, obj))
            elif hasattr(obj, 'name') and hasattr(obj, 'channels'):
                return cast(T, self._wrap(self._guild_buckets, obj))
            elif hasattr(obj, 'add_reaction') and callable(obj.add_reaction):
                return cast(T, self._wrap(self._message_buckets, obj))
        terminal(f"{obj} 沒有找到支援的類型","GlobalRateLimiter")
        return obj  # 不支援的類型，原樣返回

    def _wrap(self, pool, obj):
        if obj.id not in pool:
            pool[obj.id] = RateLimitedDiscordObject(obj)
        else:
            # ★ 每次 get 時刷新 target，避免卡在第一次的舊實例
            pool[obj.id]._target = obj
        return pool[obj.id]

# 建立單例
global_rate_limiter = GlobalRateLimiter()
