# buckets.py

import asyncio
import time
from collections import deque

LOG_TITLE = "速率管理器"

class RateLimitBucket:
    def __init__(self, rate: int, per: float, min_delay: float = 0.3):
        self.rate = rate
        self.per = per
        self.min_delay = min_delay  # 最小延遲，預設為 0.1 秒
        self.timestamps = deque()
        self.lock = asyncio.Lock()
        
        # 計算每個請求的平均間隔，並確保不小於最小延遲
        self.interval = max(self.per / self.rate, self.min_delay)

    async def enqueue(self, func, *args, action_name=None, **kwargs):
        async with self.lock:
            now = time.monotonic()
            
            while self.timestamps and now - self.timestamps[0] > self.per:
                self.timestamps.popleft()

            next_available_time = now
            if self.timestamps:
                next_available_time = self.timestamps[-1] + self.interval

            if next_available_time > now:
                delay = next_available_time - now
                print(f"[ {LOG_TITLE} ] 排隊中：動作: {action_name} | 等待 {delay:.2f}s")
                await asyncio.sleep(delay)

            self.timestamps.append(time.monotonic())

        return await func(*args, **kwargs)

# 預設行為速率表（可擴充）
ACTION_BUCKETS = {
    # 這裡可以為每個動作設定 min_delay
    "Thread.send": RateLimitBucket(rate=5, per=5),
    "Thread.delete": RateLimitBucket(rate=5, per=5),
    "Thread.edit": RateLimitBucket(rate=5, per=5),
    "TextChannel.send": RateLimitBucket(rate=5, per=5),
    "TextChannel.delete": RateLimitBucket(rate=5, per=5),
    "TextChannel.create_thread": RateLimitBucket(rate=1, per=10),
    "TextChannel.delete_messages": RateLimitBucket(rate=1, per=2),
    "TextChannel.purge": RateLimitBucket(rate=1, per=2),
    "CategoryChannel.delete": RateLimitBucket(rate=5, per=5),
    "VoiceChannel.delete": RateLimitBucket(rate=5, per=5),
    "Member.add_roles": RateLimitBucket(rate=2, per=10),
    "Member.remove_roles": RateLimitBucket(rate=2, per=10),
    "Guild.create_text_channel": RateLimitBucket(rate=1, per=10),
    "Guild.delete_channel": RateLimitBucket(rate=1, per=10),
    "Message.edit": RateLimitBucket(rate=5, per=5, min_delay=0.1),
    "Message.delete": RateLimitBucket(rate=5, per=5),
    "Message.forward": RateLimitBucket(rate=5, per=5),
    "Message.clear_reaction": RateLimitBucket(rate=3, per=1),
    "Message.add_reaction": RateLimitBucket(rate=1, per=1),
    "Message.remove_reaction": RateLimitBucket(rate=1, per=1),
}