import os
from telethon import events
from google import genai
from dotenv import load_dotenv

# بارگذاری متغیرها از فایل .env
load_dotenv()

client_gemini = genai.Client(api_key="AQ.Ab8RN6LyT2UnZ7EYty4sYGs6c2KCay77tUihd-xesjSu8Yw8ww")

def register_anime_handler(client):
    @client.on(events.NewMessage(pattern=r"^(\.انیمه|!انیمه)$", outgoing=True))
    async def anime_converter(event):
        if not event.is_reply:
            return await event.edit("❌ لطفاً روی یک عکس ریپلی کن.")

        msg = await event.get_reply_message()
        if not msg.media:
            return await event.edit("❌ این پیام عکس نیست!")

        status = await event.edit("⏳ در حال پردازش تصویر با هوش مصنوعی...")
        
        try:
            # 1. دانلود عکس به صورت بایت
            photo_bytes = await client.download_media(msg, bytes)
            
            # 2. فراخوانی مدل با ساختار جدید google-genai
            # نکته: مدل‌های جمینای متن تولید می‌کنند. برای خروجی تصویر، 
            # مدل باید قابلیت تولید فایل داشته باشد یا از APIهای تخصصی تصویر استفاده شود.
            response = client_gemini.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    "Analyze this image and provide a highly detailed anime-style description, or if the model supports, generate an image based on this input.",
                    {"data": photo_bytes, "mime_type": "image/jpeg"}
                ]
            )
            
            # 3. ارسال نتیجه به کاربر
            await event.edit("✅ پردازش انجام شد!")
            await client.send_message(event.chat_id, response.text, reply_to=msg.id)

        except Exception as e:
            await event.edit(f"❌ خطا در پردازش: {str(e)}")