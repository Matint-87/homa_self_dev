# cache_manager.py
from config import supabase
from utils import db_execute

class BalanceCache:
    _instance = None
    _cache = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BalanceCache, cls).__new__(cls)
        return cls._instance

    async def refresh_cache(self):
        # فقط اکتیو ها را لود کن تا حافظه بیهوده اشغال نشود
        query = supabase.table("users_diamonds").select("user_id, diamonds").eq("is_active", True)
        res = await db_execute(query)
        if res and res.data:
            self._cache = {row["user_id"]: row["diamonds"] for row in res.data}

    def get_balance(self, user_id):
        return self._cache.get(user_id, 0)

cache = BalanceCache()