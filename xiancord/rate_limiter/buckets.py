import asyncio
import time
from collections import deque

LOG_TITLE = "速率管理器"

class RateLimitBucket:
    def __init__(self, rate: int, per: float):
        self.rate = rate
        self.per = per
        self.queue = deque()
        self.timestamps = deque()
        self.lock = asyncio.Lock()

    async def enqueue(self, func, *args, action_name=None, **kwargs):
        async with self.lock:
            now = time.monotonic()
            while self.timestamps and now - self.timestamps[0] > self.per:
                self.timestamps.popleft()

            if len(self.timestamps) >= self.rate:
                delay = self.per - (now - self.timestamps[0])
                print(f"[ {LOG_TITLE} ] 排隊中：動作: {action_name} | 等待 {delay:.2f}s")
                await asyncio.sleep(delay)

            self.timestamps.append(time.monotonic())

        return await func(*args, **kwargs)

# 預設行為速率表（可擴充）
ACTION_BUCKETS = {
    "Thread.send": RateLimitBucket(rate=5, per=5),
    "Thread.delete": RateLimitBucket(rate=5, per=5),
    "Thread.edit": RateLimitBucket(rate=5, per=5),
    "TextChannel.send": RateLimitBucket(rate=5, per=5),
    "TextChannel.create_thread": RateLimitBucket(rate=1, per=10),
    "TextChannel.delete_messages": RateLimitBucket(rate=1, per=2),
    "TextChannel.purge": RateLimitBucket(rate=1, per=2),
    "Member.add_roles": RateLimitBucket(rate=2, per=10),
    "Member.remove_roles": RateLimitBucket(rate=2, per=10),
    "Guild.create_text_channel": RateLimitBucket(rate=1, per=10),
    "Guild.delete_channel": RateLimitBucket(rate=1, per=10),
    "Message.edit": RateLimitBucket(rate=5, per=5),
    "Message.delete": RateLimitBucket(rate=5, per=5),
    "Message.forward": RateLimitBucket(rate=5, per=5),
}
