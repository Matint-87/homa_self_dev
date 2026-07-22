import asyncio
from telethon import events, TelegramClient
from utils import db_execute
from config import supabase

# دیکشنری نگهداری تسک‌های فعال تبچی برای کاربران (در حافظه رم)
active_tabchis = {}

def register_tabchi_handler(client: TelegramClient):
    
    # --- ۱. تنظیم بنر ---
    @client.on(events.NewMessage(pattern=r'^\*تنظیم بنر (.+)$'))
    async def set_banner(event):
        user_id = event.sender_id
        banner_name = event.pattern_match.group(1).strip()
        
        if not event.is_reply:
            return await event.edit("❌ لطفاً روی یک پیام (بنر) ریپلای کنید!")
        
        reply_msg = await event.get_reply_message()
        banner_content = reply_msg.text or reply_msg.caption or ""
        
        # بررسی سقف ۱۰ بنر از طریق thread pool
        res = await db_execute(supabase.table("banners").select("id", count="exact").eq("user_id", user_id))
        if res.count >= 10:
            return await event.edit("❌ شما به سقف مجاز (حداکثر ۱۰ بنر) رسیدید!")
        
        # ذخیره در Supabase به صورت غیرهمزمان
        await db_execute(
            supabase.table("banners").upsert({
                "user_id": user_id,
                "banner_name": banner_name,
                "banner_text": banner_content
            }, on_conflict="user_id,banner_name")
        )
        
        await event.edit(f"✅ بنر شماره **{banner_name}** با موفقیت ذخیره شد.")

    # --- ۲. ارسال بنر (کپی یا فوروارد) ---
    @client.on(events.NewMessage(pattern=r'^\*تنظیم بنر (\S+) (کپی|فور)$'))
    async def send_banner_action(event):
        user_id = event.sender_id
        banner_name = event.pattern_match.group(1).strip()
        action_type = event.pattern_match.group(2).strip()
        
        res = await db_execute(
            supabase.table("banners").select("banner_text").eq("user_id", user_id).eq("banner_name", banner_name)
        )
        if not res.data:
            return await event.edit(f"❌ بنری با نام '{banner_name}' پیدا نشد.")
        
        text = res.data[0]["banner_text"]
        
        if action_type == "کپی":
            await event.respond(text)
            await event.delete()
        elif action_type == "فور":
            if event.is_reply:
                reply_msg = await event.get_reply_message()
                await reply_msg.forward_to(event.chat_id)
            else:
                await event.respond(text)
            await event.delete()

    # --- ۳. لیست بنرها ---
    @client.on(events.NewMessage(pattern=r'^\*لیست بنر$'))
    async def list_banners(event):
        user_id = event.sender_id
        res = await db_execute(supabase.table("banners").select("banner_name").eq("user_id", user_id))
        
        if not res.data:
            return await event.edit("📭 هیچ بنری ثبت نشده است.")
        
        names = [row["banner_name"] for row in res.data]
        await event.edit(f"📋 **لیست بنرهای شما:**\n" + "\n".join([f"🔸 {name}" for name in names]))

    # --- ۴. پاکسازی ---
    @client.on(events.NewMessage(pattern=r'^\*پاکسازی لیست بنر$'))
    async def clear_banners(event):
        user_id = event.sender_id
        await db_execute(supabase.table("banners").delete().eq("user_id", user_id))
        await event.edit("🗑️ تمام بنرهای شما پاک شدند.")

    @client.on(events.NewMessage(pattern=r'^\*پاکسازی کل تبچی$'))
    async def clear_all_tabchi(event):
        user_id = event.sender_id
        if user_id in active_tabchis:
            active_tabchis[user_id].cancel()
            del active_tabchis[user_id]
            
        await db_execute(supabase.table("banners").delete().eq("user_id", user_id))
        await db_execute(supabase.table("tabchi_chats").delete().eq("user_id", user_id))
        await db_execute(supabase.table("tabchi_settings").delete().eq("user_id", user_id))
        await event.edit("⚠️ کل اطلاعات و تنظیمات تبچی شما پاک و ریست شد.")

    # --- ۵. مدیریت گپ‌ها ---
    @client.on(events.NewMessage(pattern=r'^\*تبچی گپ (@\S+)$'))
    async def add_tabchi_chat(event):
        user_id = event.sender_id
        chat_username = event.pattern_match.group(1).strip()
        
        res = await db_execute(supabase.table("tabchi_chats").select("id", count="exact").eq("user_id", user_id))
        if res.count >= 10:
            return await event.edit("❌ شما حداکثر می‌توانید ۱۰ گپ برای تبچی انتخاب کنید.")
            
        await db_execute(
            supabase.table("tabchi_chats").upsert({
                "user_id": user_id,
                "chat_username": chat_username
            }, on_conflict="user_id,chat_username")
        )
        
        await event.edit(f"✅ گپ `{chat_username}` به لیست تبچی اضافه شد.")

    @client.on(events.NewMessage(pattern=r'^\*لیست تبپی گپ$'))
    async def list_tabchi_chats(event):
        user_id = event.sender_id
        res = await db_execute(supabase.table("tabchi_chats").select("chat_username").eq("user_id", user_id))
        if not res.data:
            return await event.edit("📭 هیچ گپی در لیست تبچی نیست.")
            
        chats = [row["chat_username"] for row in res.data]
        await event.edit(f"💬 **گپ‌های تبچی شما:**\n" + "\n".join([f"🔹 {c}" for c in chats]))

    @client.on(events.NewMessage(pattern=r'^\*حذف تبچی گپ (@\S+)$'))
    async def remove_tabchi_chat(event):
        user_id = event.sender_id
        chat_username = event.pattern_match.group(1).strip()
        
        await db_execute(supabase.table("tabchi_chats").delete().eq("user_id", user_id).eq("chat_username", chat_username))
        await event.edit(f"🗑️ گپ `{chat_username}` از لیست تبچی حذف شد.")

    @client.on(events.NewMessage(pattern=r'^\*پاکسازی تبچی گپ$'))
    async def clear_tabchi_chats(event):
        user_id = event.sender_id
        await db_execute(supabase.table("tabchi_chats").delete().eq("user_id", user_id))
        await event.edit("🗑️ تمام گپ‌های تبچی پاک شدند.")

    # --- ۶. لوپ پس‌زمینه تبچی (بهینه شده برای مقیاس بالا) ---
    async def tabchi_worker(client: TelegramClient, user_id: int):
        try:
            while True:
                settings = await db_execute(supabase.table("tabchi_settings").select("delay_seconds").eq("user_id", user_id))
                delay = settings.data[0]["delay_seconds"] if settings.data and "delay_seconds" in settings.data[0] else 20
                delay = max(10, min(30, delay))
                
                chats_res = await db_execute(supabase.table("tabchi_chats").select("chat_username").eq("user_id", user_id))
                banners_res = await db_execute(supabase.table("banners").select("banner_text").eq("user_id", user_id))
                
                if chats_res.data and banners_res.data:
                    chats = [c["chat_username"] for c in chats_res.data]
                    banners = [b["banner_text"] for b in banners_res.data]
                    
                    for chat in chats:
                        for banner in banners:
                            try:
                                await client.send_message(chat, banner)
                                await asyncio.sleep(1.5) # تاخیر ایمن بین ارسال‌ها جهت جلوگیری از FloodWait
                            except Exception as e:
                                print(f"Tabchi Error [User {user_id}] -> {chat}: {e}")
                
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            pass

    @client.on(events.NewMessage(pattern=r'^\*تبچی روشن(?: (\d+))?$'))
    async def turn_on_tabchi(event):
        user_id = event.sender_id
        args = event.pattern_match.group(1)
        
        delay = int(args) if args and args.isdigit() else 20
        delay = max(10, min(30, delay))
        
        await db_execute(
            supabase.table("tabchi_settings").upsert({
                "user_id": user_id,
                "is_active": True,
                "delay_seconds": delay
            }, on_conflict="user_id")
        )
        
        if user_id in active_tabchis:
            active_tabchis[user_id].cancel()
            
        active_tabchis[user_id] = asyncio.create_task(tabchi_worker(event.client, user_id))
        await event.edit(f"🟢 **تبچی روشن شد!**\n⏱️ سرعت: هر {delay} ثانیه یک‌بار.")

    @client.on(events.NewMessage(pattern=r'^\*تبچی خاموش$'))
    async def turn_off_tabchi(event):
        user_id = event.sender_id
        
        await db_execute(
            supabase.table("tabchi_settings").upsert({
                "user_id": user_id,
                "is_active": False
            }, on_conflict="user_id")
        )
        
        if user_id in active_tabchis:
            active_tabchis[user_id].cancel()
            del active_tabchis[user_id]
            
        await event.edit("🔴 **تبچی خاموش شد.**")