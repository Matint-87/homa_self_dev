from telethon import events
import secrets
import string

def register_password_handler(client):
    
    @client.on(events.NewMessage(pattern=r'\*رمز (\d+)'))
    async def generate_password(event):
        try:
            # دریافت طول از دستور
            length = int(event.pattern_match.group(1))
            
            # محدودیت ۵۰ کاراکتر
            if length > 50:
                await event.edit("⚠️ **خطا:** حداکثر طول رمز نباید بیشتر از ۵۰ باشد.")
                return
            
            # ایجاد کاراکترها
            alphabet = string.ascii_letters + string.digits + string.punctuation

            # تولید رمز امن
            password = ''.join(secrets.choice(alphabet) for i in range(length))
            
            spoiler_password = f"<tg-spoiler><code>{password}</code></tg-spoiler>"
            # ارسال و نمایش
            await event.edit(
                        f"🔐 <b>رمز تولید شده ({length} کاراکتری):</b>\n\n`{spoiler_password}`",
                        parse_mode='html'
                    )
            
        except Exception as e:
            await event.edit(f"❌ خطایی رخ داد: {str(e)}")
