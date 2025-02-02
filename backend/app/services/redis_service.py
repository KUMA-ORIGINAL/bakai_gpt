import redis.asyncio as redis
from broadcaster import Broadcast

from config import settings

redis_pool = redis.ConnectionPool(host=settings.redis.REDIS_HOST,
                                  port=settings.redis.REDIS_PORT,
                                  db=settings.redis.REDIS_DB)
redis_client = redis.Redis(connection_pool=redis_pool)
pubsub = redis_client.pubsub()

broadcast = Broadcast(f"redis://{settings.redis.REDIS_HOST}:{settings.redis.REDIS_PORT}/{settings.redis.REDIS_DB}")

async def listen_redis(manager):
    await pubsub.subscribe("chat")
    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True)
        if message:
            data = message["data"].decode("utf-8")
            await manager.broadcast(data)
