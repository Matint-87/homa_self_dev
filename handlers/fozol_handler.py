from telethon import events
from config import supabase
from utils import db_execute

async def register_fozol_handler(client):
    @client.on(events.NewMessage)
    async def handler(event):
        sender = await event.get_sender()
        if sender:
            # ثبت یا به‌روزرسانی کاربر در دیتابیس
            supabase.table("profile_interactions").upsert({
                "user_id": sender.id,
                "username": sender.username or "No Username",
                "last_seen": "now()"
            }).execute()

    print("Ping handler registered successfully!")

    # دستور اختصاصی برای نمایش لیست (فضول‌ها)
    @client.on(events.NewMessage(pattern=r'\* فضول ها'))
    async def show_activity(event):
        query = supabase.table("profile_interactions")\
            .select("*")\
            .gte("last_seen", "now() - interval '24 hours'")
        
        # اجرای غیرهمزمان
        response = await db_execute(query)

        msg = "لیست افرادی که اخیراً پروفایل شما را چک کرده اند:\n"
        for user in response.data:
            msg += f"- {user['username']} (ID: {user['user_id']})\n"
        
        await event.reply(msg)
