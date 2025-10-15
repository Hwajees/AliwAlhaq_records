import os
import asyncio
from pyrogram import Client
from libs.pytgcalls.pytgcalls.pytgcalls import PyTgCalls  # المسار الجديد
from pyrogram.types import Message

# ======================
# المتغيرات من بيئة Render
# ======================
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # إذا لاحقًا تحتاجه

# ======================
# إنشاء اليوزبوت
# ======================
app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# ======================
# إنشاء PyTgCalls instance
# ======================
pytgclient = PyTgCalls(app)

# ======================
# أمر الصعود إلى المحادثة الصوتية
# ======================
async def join_voice_chat():
    try:
        await pytgclient.join_group_call(GROUP_ID, "silence.mp3")  # الملف الصوتي التجريبي
        print("Bot joined the voice chat successfully!")
    except Exception as e:
        print(f"Error joining voice chat: {e}")

# ======================
# أمر الخروج من المحادثة الصوتية
# ======================
async def leave_voice_chat():
    try:
        await pytgclient.leave_group_call(GROUP_ID)
        print("Bot left the voice chat successfully!")
    except Exception as e:
        print(f"Error leaving voice chat: {e}")

# ======================
# أوامر تحكم بسيطة عبر الرسائل
# ======================
@app.on_message()
async def handle_message(client, message: Message):
    text = message.text.lower()
    if "صعد" in text:  # مثال، يمكن تغييره
        await join_voice_chat()
    elif "نزل" in text:
        await leave_voice_chat()

# ======================
# بدء البوت
# ======================
async def main():
    await app.start()
    print("Userbot started!")
    await pytgclient.start()
    print("PyTgCalls client started!")
    await asyncio.Future()  # يبقي البرنامج يعمل

if __name__ == "__main__":
    asyncio.run(main())

