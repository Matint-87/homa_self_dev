from telethon import events
import requests

def register_watter_handler(client):
    
    @client.on(events.NewMessage(pattern=r'\*دما (.*)'))
    async def get_weather(event):
        # دریافت نام شهر از دستور
        city = event.pattern_match.group(1)
        
        await event.edit(f"🔍 در حال دریافت وضعیت آب‌وهوای {city}...")
        
        try:
            # استفاده از API رایگان و متنی wttr.in
            # پارامترهای ?format=3 یعنی فقط یک خط خلاصه برگرداند
            # lang=fa برای زبان فارسی
            url = f"https://wttr.in/{city}?format=3&lang=fa"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                await event.edit(f"🌤 وضعیت آب و هوا:\n\n{response.text}")
            else:
                await event.edit("❌ متأسفانه اطلاعاتی برای این شهر یافت نشد.")
                
        except Exception as e:
            await event.edit(f"⚠️ خطا در اتصال به سرور آب‌وهوا: {str(e)}")