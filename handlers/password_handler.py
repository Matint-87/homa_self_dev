from telethon import events
import secrets
import string

def register_password_handler(client):
    
    @client.on(events.NewMessage(pattern=r'\*رمز (\d+)'))
    async def generate_password(event):
        # gereftan adad az dastor (masalan 8)
        length = int(event.pattern_match.group(1))
        
        # sakht-e karaktr-haye majaz (horoof-e bozorg, koochak va adad)
        alphabet = string.ascii_letters + string.digits + string.punctuation
        
        # tolid-e ramz-e amni
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        
        # ersal-e ramz be soorat-e edit
        await event.edit(f"🔐 **Ramz-e tolid shode ({length} ragami):**\n\n`{password}`")

    print("✅ Password handler registered successfully!")