import os
import sys

# أضف مجلد libs إلى sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

from pyrogram import Client
from pytgcalls import pytgcalls  # استيراد pytgcalls.py من مجلد pytgcalls

# المتغيرات من بيئة Render
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))

# تهيئة البوت
app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
pytgcalls_instance = pytgcalls.PyTgCalls(app)

# دوال بسيطة للصعود والخروج من المحادثة الصوتية
@app.on_message()
async def handle_message(client, message):
    text = message.text.lower() if message.text else ""
    
    if text == "/join":
        await pytgcalls_instance.join_group_call(GROUP_ID, "silence.mp3")
        await message.reply_text("✅ تم الصعود إلى المحادثة الصوتية")
    
    elif text == "/leave":
        await pytgcalls_instance.leave_group_call(GROUP_ID)
        await message.reply_text("✅ تم الخروج من المحادثة الصوتية")

# تشغيل البوت
app.run()
