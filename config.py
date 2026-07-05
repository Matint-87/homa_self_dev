import os
from supabase import create_client, Client
from dotenv import load_dotenv


API_ID = 36368052     
API_HASH = "b81783253a3e4f323d29eff48eeb392b" 
SESSION_NAME="my_homabot"

BOT_TOKEN = "8744020577:AAFFFzq1RiqOxt8yF8TPEpt6KQ0DZHoojmE" 
PANEL_BOT_TOKEN = "8897179845:AAFrHmB7XdTKfy592fEO-A6Gr13nXsHaPs8"
BOT_USERNAME = "Homa_panel_dev_bot"

CHANNELS = [
    {'id': "@Homa_self_Ch", 'url': "https://t.me/Homa_self_Ch"},
    {'id': "@Homa_self_Gp", 'url': "https://t.me/Homa_self_Gp"},
]

SESSIONS_FILE = "sessions.json"

# supabase configuration
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
