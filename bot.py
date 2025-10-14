import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.input_stream import InputStream, InputAudioStream
from pyrogram.types import Message

# ---------------------------
# إعدادات البوت
# ---------------------------
API_ID = int(os.environ.get("API_ID", 123456))  # ضع API_ID الخاص بك
API_HASH = os.environ.get("API_HASH", "your_api_hash")
SESSION_STRING = os.environ.get("SESSION_STRING", "your_session_string")
GROUP_ID = int(os.environ.get("GROUP_ID", -1001234567890))  # معرف القروب

# ملف الصوت الافتراضي عند الصعود للصوت
AUDIO_FILE = "silence.mp3"

# ---------------------------
# إنشاء العميل
# ---------------------------
app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
pytgcalls = PyTgCalls(app)

# ---------------------------
# الأحداث
# ---------------------------
@app.on_message(filters.command("joinvc") & filters.user("me") & filters.chat(GROUP_ID))
async def join_vc(client: Client, message: Message):
    """
    صعود البوت للمكالمة الصوتية
    """
    try:
        await pytgcalls.join_group_call(
            GROUP_ID,
            InputStream(
                InputAudioStream(AUDIO_FILE)
            )
        )
        await message.reply_text("✅ صعدت إلى المكالمة الصوتية!")
    except Exception as e:
        await message.reply_text(f"❌ حدث خطأ: {e}")

@app.on_message(filters.command("leavevc") & filters.user("me") & filters.chat(GROUP_ID))
async def leave_vc(client: Client, message: Message):
    """
    الخروج من المكالمة الصوتية
    """
    try:
        await pytgcalls.leave_group_call(GROUP_ID)
        await message.reply_text("✅ خرجت من المكالمة الصوتية!")
    except Exception as e:
        await message.reply_text(f"❌ حدث خطأ: {e}")

# ---------------------------
# تشغيل البوت
# ---------------------------
if __name__ == "__main__":
    print("🚀 Starting userbot...")
    app.start()
    pytgcalls.start()
    print("✅ Userbot is running")
    app.idle()
