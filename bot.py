import os
import sys

# إضافة مجلد libs إلى مسار البحث
sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

from pyrogram import Client
from pytgcalls.pytgcalls import PyTgCalls  # الآن سيجده Python

# =========================
# متغيرات البيئة
# =========================
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # إذا لاحقًا تحتاجه

# =========================
# إنشاء اليوزبوت
# =========================
app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# =========================
# إعداد PyTgCalls
# =========================
pytgcalls = PyTgCalls(app)

# =========================
# مثال على الانضمام إلى المحادثة الصوتية
# =========================
async def join_voice_chat():
    await pytgcalls.join_group_call(
        GROUP_ID,
        "silence.mp3"  # الملف الصوتي الصامت لتشغيله
    )

# =========================
# مثال على الخروج من المحادثة الصوتية
# =========================
async def leave_voice_chat():
    await pytgcalls.leave_group_call(GROUP_ID)

# =========================
# تشغيل اليوزبوت
# =========================
if __name__ == "__main__":
    app.run()
