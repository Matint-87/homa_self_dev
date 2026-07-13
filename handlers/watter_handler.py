from telethon import events
import requests

def register_handler(client):
    
    @client.on(events.NewMessage(pattern=r'\*دما (.*)'))
    async def get_weather(event):
        city = event.pattern_match.group(1)
        
        await event.edit(f"🔍 در حال دریافت وضعیت آب‌وهوای {city}...")
        
        try:
            # استفاده از wttr.in با فرمت اختصاصی برای اطلاعات کامل
            url = f"https://wttr.in/{city}?format=%t+%f+%h+%w+%C&lang=fa"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                # خروجی دریافتی مثلاً: +34°C +37°C 28% 14km/h نیمه‌ابری
                data = response.text.split()
                
                # چیدمان زیبا در جدول
                table = f"""
🌤 **وضعیت آب و هوا: {city}**

| شاخص | مقدار |
| :--- | :--- |
| 🌡 دما | {data[0]} |
| 🤗 احساس | {data[1]} |
| 💧 رطوبت | {data[2]} |
| 💨 باد | {data[3]} |
| ☁️ وضعیت | {data[4]} |
"""
                await event.edit(table)
            else:
                await event.edit("❌ متأسفانه اطلاعاتی برای این شهر یافت نشد.")
                
        except Exception as e:
            await event.edit(f"⚠️ خطا: {str(e)}")