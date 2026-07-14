import google.generativeai as genai
from telethon import events
import io
import os

# کانفیگ گوگل
genai.configure(api_key="YOUR_GEMINI_API_KEY") # کلیدت را اینجا بگذار
model = genai.GenerativeModel('gemini-1.5-flash')

def register_anime_handler(client):
    @client.on(events.NewMessage(pattern=r"^(\.انیمه|!انیمه)$", outgoing=True))
    async def anime_converter(event):
        if not event.is_reply:
            return await event.edit("❌ لطفاً روی عکس ریپلی کن.")

        msg = await event.get_reply_message()
        if not msg.media:
            return await event.edit("❌ این پیام عکس نیست!")

        status = await event.edit("⏳ در حال پردازش با هوش مصنوعی...")
        
        try:
            # دانلود عکس به صورت بایت
            photo_bytes = await client.download_media(msg, bytes)
            
            # آماده‌سازی عکس برای Gemini
            img_data = {"mime_type": "image/jpeg", "data": photo_bytes}
            
            # درخواست تبدیل به انیمه
            response = model.generate_content([
                "تبدیل این عکس به یک نسخه انیمه با کیفیت بالا. فقط عکس را خروجی بده.", 
                img_data
            ])

            # نکته مهم: Gemini مدل متنی-تصویری است. 
            # برای تبدیل مستقیم عکس به عکس (Style Transfer)، 
            # اگر خروجی مستقیماً عکس نبود، از سرویس‌های تخصصی‌تر استفاده کن.
            # اما برای تحلیل و توصیف انیمه عالی عمل می‌کند.
            
            await event.edit("✅ پردازش انجام شد!")
            # ارسال نتیجه به کاربر
            await client.send_file(event.chat_id, response.text) # یا فایل پردازش شده

        except Exception as e:
            await event.edit(f"❌ خطا: {str(e)}")