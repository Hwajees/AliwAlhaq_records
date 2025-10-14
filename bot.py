import os
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream.input_audio import InputAudio

# -----------------------------
# إعدادات البوت
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
pytgcalls = PyTgCalls(app)

# -----------------------------
# دوال مساعدة
# -----------------------------
async def is_user_admin(chat_id, user_id):
    try:
        async for member in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if member.user.id == user_id:
                return True
        return False
    except Exception as e:
        print("Error checking admin:", e)
        return False

# -----------------------------
# أوامر المجموعة
# -----------------------------
@app.on_message(filters.group & filters.text)
async def handle_messages(client, message):
    if str(message.chat.id) != str(GROUP_ID):
        return

    user_id = message.from_user.id
    text = message.text.strip()
    is_admin = await is_user_admin(message.chat.id, user_id)

    if text.startswith("اصعد الصوت"):
        if not is_admin:
            return  # لا يرد على الأعضاء العاديين

        try:
            await pytgcalls.join_group_call(
                GROUP_ID,
                InputStream(InputAudio("silence.mp3")),  # الملف الصوتي المؤقت
            )
            await message.reply("✅ تم الانضمام للمحادثة الصوتية بنجاح!")
        except Exception as e:
            await message.reply(f"❌ فشل الانضمام للمحادثة الصوتية: {e}")

# -----------------------------
# تشغيل البوت
# -----------------------------
if __name__ == "__main__":
    app.start()
    pytgcalls.start()
    print("🚀 Userbot Voice Step 1 started")
