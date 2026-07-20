from telethon import events
from utils import db_execute

def register_tabchi_handler(client, supabase):
    @client.on(events.NewMessage(pattern=r'^\.?(.*)'))
    async def tabchi_handler(event):
        # دریافت متن پیام و حذف فواصل اضافه
        text = event.pattern_match.group(1).strip()
        user_id = event.sender_id
        
        # ۱. تبچی روشن
        if text == "تبچی روشن":
            query = supabase.table("tabchi_settings").upsert({"user_id": user_id, "is_active": True})
            await db_execute(query)
            await event.edit("✅ تب‌چی روشن شد.")

        # ۲. تبچی خاموش
        elif text == "تبچی خاموش":
            query = supabase.table("tabchi_settings").upsert({"user_id": user_id, "is_active": False})
            await db_execute(query)
            await event.edit("❌ تب‌چی خاموش شد.")

        # ۳. تنظیم بنر (شامل تنظیم بنر 20 کپی و تنظیم بنر 20 فور)
        elif text.startswith("تنظیم بنر"):
            if not event.is_reply:
                return await event.edit("⚠️ نکته: دستور تنظیم بنر باید حتماً روی پیام ریپلای شود.")
            
            reply_msg = await event.get_reply_message()
            # تشخیص نوع: اگر در متن "فور" باشد فوروارد، در غیر این صورت کپی
            b_type = "forward" if "فور" in text else "copy"
            
            query = supabase.table("tabchi_banners").insert({
                "user_id": user_id,
                "banner_text": reply_msg.text,
                "banner_type": b_type
            })
            await db_execute(query)
            await event.edit(f"✅ بنر با موفقیت در حالت {b_type} تنظیم شد.")

        # ۴. لیست بنر
        elif text == "لیست بنر":
            query = supabase.table("tabchi_banners").select("*").eq("user_id", user_id)
            response = await db_execute(query)
            if not response.data:
                return await event.edit("⚠️ لیست بنرهای شما خالی است.")
            
            msg = "📋 لیست بنرهای شما:\n" + "\n".join([f"{b['id']}: {b['banner_type']}" for b in response.data])
            await event.edit(msg)

        # ۵. پاکسازی بنر (پاکسازی یک بنر خاص یا آخرین مورد)
        elif text == "پاکسازی بنر":
            # حذف آخرین بنر اضافه شده برای این کاربر
            query = supabase.table("tabchi_banners").delete().eq("user_id", user_id) # در اینجا می‌توان محدودیت ID هم گذاشت
            await db_execute(query)
            await event.edit("🗑 آخرین بنر تنظیم شده پاک شد.")

        # ۶. پاکسازی کل تبچی
        elif text == "پاکسازی کل تبچی":
            query = supabase.table("tabchi_banners").delete().eq("user_id", user_id)
            await db_execute(query)
            await event.edit("🗑 تمام داده‌های تب‌چی شما پاکسازی شد.")

# -- جدول برای ذخیره وضعیت تب‌چی هر کاربر
# create table tabchi_settings (
#   user_id bigint primary key,
#   is_active boolean default false
# );

# -- جدول برای ذخیره بنرها (متن/پیام)
# create table tabchi_banners (
#   id bigint generated always as identity primary key,
#   user_id bigint references tabchi_settings(user_id),
#   banner_text text,
#   banner_type text -- 'copy' or 'forward'
# );