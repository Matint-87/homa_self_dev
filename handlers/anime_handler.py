
import os
from telethon import events
from google import genai
from google.genai import types
from dotenv import load_dotenv

client_gemini = genai.Client(api_key="AQ.Ab8RN6KZ-7s7Lwwvc2jWeNYBna7CPIc3UhUs38gyMU9iuiG6pw")


def register_anime_handler(client):
    @client.on(events.NewMessage(pattern=r"^(\.انیمه|!انیمه)$", outgoing=True))
    async def anime_converter(event):
        if not event.is_reply:
            return await event.edit("❌ لطفاً روی یک عکس ریپلی کن.")

        msg = await event.get_reply_message()
        if not msg.media:
            return await event.edit("❌ این پیام عکس نیست!")

        # استفاده از متد edit برای نمایش وضعیت
        status = await event.edit("⏳ در حال پردازش با هوش مصنوعی...")
        
        try:
            # دانلود فایل به صورت Bytes
            photo_bytes = await client.download_media(msg, bytes)
            
            # آماده‌سازی تصویر با ساختار جدید گوگل
            image_part = types.Part.from_bytes(
                data=photo_bytes,
                mime_type='image/jpeg'
            )
            
            # ارسال درخواست به جمینای
            # نکته: مدل Flash برای سرعت بالا بهینه شده است
            response = client_gemini.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    "تبدیل این عکس به یک نسخه انیمه با کیفیت بالا. فقط توصیف کن یا اگر امکان دارد یک تصویر انیمه‌ای متناسب با این عکس ایجاد کن.",
                    image_part
                ]
            )
            
            # ارسال پاسخ نهایی
            await event.edit("✅ پردازش انجام شد!")
            # محدود کردن متن برای جلوگیری از خطای تلگرام
            result_text = response.text[:4000] if response.text else "محتوایی تولید نشد."
            await client.send_message(event.chat_id, result_text, reply_to=msg.id)

        except Exception as e:
            # خطا را لاگ کن که در ترمینال ببینی
            print(f"DEBUG ERROR: {str(e)}")
            await event.edit("❌ خطا در پردازش تصویر. لطفاً دوباره تلاش کنید.")            