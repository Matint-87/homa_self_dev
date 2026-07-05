from functools import wraps
from cache_manager import cache

def require_balance(func):
    @wraps(func)
    async def wrapper(event, *args, **kwargs):
        user_id = event.sender_id
        # چک سریع از کش
        if cache.get_balance(user_id) > 0:
            return await func(event, *args, **kwargs)
        else:
            await event.reply("❌ موجودی شما تمام شده است.")
            return
    return wrapper