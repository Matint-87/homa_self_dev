from telethon import events
from telethon.tl.types import User
from datetime import datetime, timedelta
from config import supabase
from utils import db_execute

def register_fozol_handler(client):

    @client.on(events.NewMessage)
    async def save_interaction(event):
        # دریافت فرستنده پیام
        sender = await event.get_sender()

        # بررسی اینکه فرستنده وجود داشته باشد و حتماً کاربر (User) باشد
        # کانال‌ها و گروه‌ها دارای ویژگی .bot نیستند، پس حتماً باید نوع sender را چک کنیم
        if not sender or not isinstance(sender, User) or sender.bot:
            return

        # ذخیره یا به‌روزرسانی تعامل کاربر در Supabase
        query = (
            supabase.table("profile_interactions")
            .upsert(
                {
                    "user_id": sender.id,
                    "username": sender.username or "No Username",
                    "last_seen": datetime.utcnow().isoformat(),
                },
                on_conflict="user_id",
            )
        )

        await db_execute(query)

    print("✅ Fozol handler registered successfully!")

    # هندلر برای نمایش لیست فضول‌ها با دستور "* فضول ها"
    @client.on(events.NewMessage(pattern=r"^\*فضول ها$"))
    async def show_activity(event):
        # محاسبه بازه زمانی ۲۴ ساعت گذشته
        since = (datetime.utcnow() - timedelta(hours=24)).isoformat()

        query = (
            supabase.table("profile_interactions")
            .select("*")
            .gte("last_seen", since)
            .order("last_seen", desc=True)
        )

        response = await db_execute(query)

        if not response.data:
            await event.reply("هیچ موردی در ۲۴ ساعت گذشته ثبت نشده است.")
            return

        msg = "👀 لیست کاربرانی که اخیراً پیام داده‌اند:\n\n"

        for row in response.data:
            # نمایش نام کاربری و آیدی
            msg += f"• @{row['username']}\n🆔 `{row['user_id']}`\n\n"

        await event.reply(msg)