from .buckets import ACTION_BUCKETS , LOG_TITLE
import asyncio

class RateLimitedDiscordObject:
    def __init__(self, discord_obj):
        self._target = discord_obj

    def __getattr__(self, name):

        orig_attr = getattr(self._target, name)
        if callable(orig_attr):
            async def wrapper(*args, **kwargs):
                action_name = f"{type(self._target).__name__}.{name}"
                bucket = ACTION_BUCKETS.get(action_name)
                if bucket:
                    return await bucket.enqueue(orig_attr, *args, action_name=action_name, **kwargs)
                else:
                    print(f"[速率管理器] {action_name} 不在 ACTION_BUCKETS 中，未套用限速邏輯。")
                return await orig_attr(*args, **kwargs)
            return wrapper
        return orig_attr