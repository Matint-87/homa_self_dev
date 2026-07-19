from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest

def register_profile_handler(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\*(نام|فامیلی|تنظیم پروفایل)'))
    async def profile_handler(event):
        text = event.raw_text
        
        # 1. تغییر نام
        if text.startswith('*نام'):
            new_first_name = text.replace('*نام', '').strip()
            if new_first_name:
                await client(UpdateProfileRequest(first_name=new_first_name))
                await event.edit(f"✅ نام پروفایل به **{new_first_name}** تغییر یافت.")
            else:
                await event.edit("❌ لطفاً نام جدید را وارد کنید.")

        # 2. تغییر فامیلی
        elif text.startswith('*فامیلی'):
            new_last_name = text.replace('*فامیلی', '').strip()
            await client(UpdateProfileRequest(last_name=new_last_name))
            await event.edit(f"✅ نام خانوادگی به **{new_last_name}** تغییر یافت.")

        # 3. تغییر عکس پروفایل با ریپلای
        elif text == '*تنظیم پروفایل':
            if event.is_reply:
                reply_message = await event.get_reply_message()
                if reply_message.media:
                    await event.edit("⏳ در حال آپلود عکس...")
                    # دانلود فایل از ریپلای
                    photo = await client.download_media(reply_message)
                    # آپلود به عنوان عکس پروفایل
                    file = await client.upload_file(photo)
                    await client(UploadProfilePhotoRequest(file=file))
                    await event.edit("✅ عکس پروفایل با موفقیت تغییر کرد.")
                else:
                    await event.edit("❌ پیامی که ریپلای کردید حاوی عکس نیست.")
            else:
                await event.edit("❌ لطفاً روی یک عکس ریپلای کنید.")
