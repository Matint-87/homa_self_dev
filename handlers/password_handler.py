from telethon import events
import secrets
import string
import html # این کتابخانه را در بالای فایل ایمپورت کنید

def register_password_handler(client):
    
    @client.on(events.NewMessage(pattern=r'\*رمز (\d+)'))
    async def generate_password(event):
        try:
            # دریافت طول از دستور
            length = int(event.pattern_match.group(1))
                
            # محدودیت ۵۰ کاراکتر
            if length > 50:
                await event.edit("⚠️ **خطا:** حداکثر ۵۰.")
                return
                
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
            password = ''.join(secrets.choice(alphabet) for i in range(length))
            
            # رمز را Escape می‌کنیم تا تداخلی نداشته باشد
            safe_password = html.escape(password)
            
            # فقط از تگ اسپویلر استفاده می‌کنیم (بدون تگ کد)
            text = f"🔐 <b>رمز شما ({length} کاراکتری):</b>\n\n<tg-spoiler>{safe_password}</tg-spoiler>"
            
            await event.edit(text, parse_mode='html')
            
        except Exception as e:
            await event.edit(f"❌ خطایی رخ داد: {str(e)}")
