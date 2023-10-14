import redis
from redis import ConnectionPool
from config import redis_config

redis_pool = ConnectionPool(
    host=redis_config.get("host"),
    port=redis_config.get('port'),
    db=redis_config.get('db'),
    password=redis_config.get('password'),
    max_connections=redis_config.get('max_connections')
)
# 从连接池中获取 Redis 连接
redis_conn = redis.Redis(connection_pool=redis_pool)

print(f'redis是否连接:{redis_conn.ping()}')
