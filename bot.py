import sys
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# أضف مجلد libs إلى مسار Python ليتم التعرف على الحزم المحلية
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs"))

# استيراد الحزم بعد إضافة المسار
from pytgcalls import PyTgCalls
from tgcalls import SomeModule  # عدّل حسب الحاجة

# -------------------------
# متغيرات البيئة
API_ID = int(os.environ.get("API_ID", 123456))  # ضع API_ID الخاص بك
API_HASH = os.environ.get("API_HASH", "your_api_hash")
SESSION_STRING = os.environ.get("SESSION_STRING", "your_session_string")
GROUP_ID = int(os.environ.get("GROUP_ID", -1001234567890))  # معرف القروب

# -------------------------
# إعدادات Pyrogram
app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# إعداد PyTgCalls
pytgcalls = PyTgCalls(app)

# -------------------------
# أوامر البوت

@app.on_message(filters.command("joinvc") & filters.user(filters.me))
async def join_voice(_, message: Message):
    try:
        await pytgcalls.join_group_call(GROUP_ID, "silence.mp3")
        await message.reply_text("تم الانضمام إلى المحادثة الصوتية ✅")
    except Exception as e:
        await message.reply_text(f"حدث خطأ: {e}")

@app.on_message(filters.command("leavevc") & filters.user(filters.me))
async def leave_voice(_, message: Message):
    try:
        await pytgcalls.leave_group_call(GROUP_ID)
        await message.reply_text("تم الخروج من المحادثة الصوتية ✅")
    except Exception as e:
        await message.reply_text(f"حدث خطأ: {e}")

# -------------------------
# تشغيل البوت
print("🚀 Starting userbot...")
app.run()

