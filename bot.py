import sys
import os
from pyrogram import Client, filters

# أضف مجلد libs للمسار ليتمكن Python من إيجاد pytgcalls و tgcalls
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs"))

from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pyrogram.types import Message

# =======================
# إعداد المتغيرات البيئية
# =======================
API_ID = int(os.environ.get("API_ID", 123456))  # ضع رقم API_ID الافتراضي إذا لم يكن موجود
API_HASH = os.environ.get("API_HASH", "your_api_hash")
SESSION_STRING = os.environ.get("SESSION_STRING", "your_session_string")
GROUP_ID = int(os.environ.get("GROUP_ID", -1001234567890))  # معرف القروب

# =======================
# تهيئة العميل والPyTgCalls
# =======================
app = Client(session_name=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
pytg = PyTgCalls(app)

# =======================
# أوامر البوت
# =======================
@app.on_message(filters.user("me") & filters.command("joinvc", prefixes="/"))
async def join_vc(client: Client, message: Message):
    """
    الأمر: /joinvc
    يجعل البوت يصعد للمكالمة الصوتية في القروب
    """
    try:
        await pytg.join_group_call(
            GROUP_ID,
            "silence.mp3"  # الملف الصوتي الصامت
        )
        await message.reply_text("✅ تم صعود البوت للمكالمة الصوتية.")
    except Exception as e:
        await message.reply_text(f"❌ حدث خطأ: {e}")

@app.on_message(filters.user("me") & filters.command("leavevc", prefixes="/"))
async def leave_vc(client: Client, message: Message):
    """
    الأمر: /leavevc
    يجعل البوت يغادر المكالمة الصوتية
    """
    try:
        await pytg.leave_group_call(GROUP_ID)
        await message.reply_text("✅ تم خروج البوت من المكالمة الصوتية.")
    except Exception as e:
        await message.reply_text(f"❌ حدث خطأ: {e}")

# =======================
# بدء البوت
# =======================
print("🚀 Starting userbot...")
app.start()
pytg.start()
print("✅ Userbot started. Listening for commands...")

# إبقاء البوت يعمل
import asyncio
asyncio.get_event_loop().run_forever()
