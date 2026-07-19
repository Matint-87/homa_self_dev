from telethon import events
from telethon.tl.types import User
from datetime import datetime, timedelta
from config import supabase
from utils import db_execute

def register_fozol_handler(client):
    # گرفتن آیدی خودت برای جلوگیری از ثبت فعالیت‌های خودت
    me = None

    @client.on(events.NewMessage)
    async def save_interaction(event):
        nonlocal me
        # مقدار me را یکبار کش می‌کنیم تا هر بار درخواست به تلگرام نزنیم
        if me is None:
            me = await client.get_me()

        sender = await event.get_sender()

        # فیلتر: حتماً کاربر باشد، ربات نباشد، و خودش نباشد
        if not sender or not isinstance(sender, User) or sender.bot or sender.id == me.id:
            return

        # ساخت نام نمایش برای دیتابیس
        display_name = sender.username or f"{sender.first_name or ''} {sender.last_name or ''}".strip() or "No Name"

        query = (
            supabase.table("profile_interactions")
            .upsert(
                {
                    "user_id": sender.id,
                    "username": display_name,
                    "last_seen": datetime.utcnow().isoformat(),
                },
                on_conflict="user_id",
            )
        )
        await db_execute(query)

    # هندلر برای نمایش لیست
    @client.on(events.NewMessage(pattern=r"^\*فضول ها$"))
    async def show_activity(event):
        # بازه ۲۴ ساعت
        since = (datetime.utcnow() - timedelta(hours=24)).isoformat()

        query = (
            supabase.table("profile_interactions")
            .select("*")
            .gte("last_seen", since)
            .order("last_seen", desc=True)
        )

        response = await db_execute(query)

        if not response.data:
            await event.edit("🚫 هیچ موردی در ۲۴ ساعت گذشته ثبت نشده است.")
            return

        msg = "👀 **لیست فعالیت‌های ۲۴ ساعت اخیر:**\n\n"

        for row in response.data:
            # تبدیل زمان دیتابیس به فرمت خوانا
            last_seen = datetime.fromisoformat(row['last_seen']).strftime('%H:%M:%S')
            
            # اگر یوزرنیم داشت با @ نمایش بده، اگر نداشت نامش را بنویس
            name = f"@{row['username']}" if row['username'] != "No Name" and not row['username'].startswith(" ") else row['username']
            
            msg += f"👤 {name}\n🆔 `{row['user_id']}` | 🕒 {last_seen}\n➖➖➖➖➖\n"

        await event.edit(msg)
