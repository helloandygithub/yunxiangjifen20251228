import redis
from typing import Optional
from config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def set_sms_code(phone: str, code: str, expire: int = 300) -> None:
    """设置短信验证码，默认5分钟过期"""
    redis_client.setex(f"sms_code:{phone}", expire, code)


def get_sms_code(phone: str) -> Optional[str]:
    """获取短信验证码"""
    return redis_client.get(f"sms_code:{phone}")


def delete_sms_code(phone: str) -> None:
    """删除短信验证码"""
    redis_client.delete(f"sms_code:{phone}")


def check_rate_limit(key: str, limit: int, window: int = 60) -> bool:
    """检查频率限制
    
    Args:
        key: 限制的key
        limit: 时间窗口内最大次数
        window: 时间窗口（秒）
    
    Returns:
        True if within limit, False if exceeded
    """
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, window)
    return current <= limit


def check_sms_limit(phone: str, limit: int = 5, window: int = 3600) -> bool:
    """检查短信发送频率限制"""
    return check_rate_limit(f"sms_limit:{phone}", limit, window)


def cache_activity(activity_id: int, data: dict, expire: int = 300) -> None:
    """缓存活动数据"""
    import json
    redis_client.setex(f"activity:{activity_id}", expire, json.dumps(data, ensure_ascii=False))


def get_cached_activity(activity_id: int) -> Optional[dict]:
    """获取缓存的活动数据"""
    import json
    data = redis_client.get(f"activity:{activity_id}")
    return json.loads(data) if data else None


def clear_activity_cache(activity_id: int = None) -> None:
    """清除活动缓存"""
    if activity_id:
        redis_client.delete(f"activity:{activity_id}")
    else:
        for key in redis_client.scan_iter("activity:*"):
            redis_client.delete(key)
