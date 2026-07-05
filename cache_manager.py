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
        try:
            query = supabase.table("users_diamonds").select("user_id, diamonds")
            res = await db_execute(query)
            if res and res.data:
                self._cache = {int(row["user_id"]): int(row["diamonds"]) for row in res.data}
        except Exception as e:
            print(f"Error refreshing cache: {e}")

    # این متد باید دقیقا همین نام باشد
    def get_balance(self, user_id):
        return self._cache.get(int(user_id), 0)

# ایجاد یک نمونه (Instance) از کلاس
cache = BalanceCache()