from telethon import events
from datetime import datetime, timedelta
from config import supabase
from utils import db_execute


def register_fozol_handler(client):

    @client.on(events.NewMessage)
    async def save_interaction(event):
        sender = await event.get_sender()

        if not sender or sender.bot:
            return

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

    @client.on(events.NewMessage(pattern=r"^\* فضول ها$"))
    async def show_activity(event):

        since = (datetime.utcnow() - timedelta(hours=24)).isoformat()

        query = (
            supabase.table("profile_interactions")
            .select("*")
            .gte("last_seen", since)
            .order("last_seen", desc=True)
        )

        response = await db_execute(query)

        if not response.data:
            await event.reply("هیچ موردی ثبت نشده است.")
            return

        msg = "👀 کاربران ثبت‌شده:\n\n"

        for row in response.data:
            msg += f"• @{row['username']}\n🆔 `{row['user_id']}`\n\n"

        await event.reply(msg)