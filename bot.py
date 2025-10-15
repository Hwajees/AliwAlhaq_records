import os
import sys
from pyrogram import Client, filters

# ✅ نضيف مجلد libs لمسار البحث
sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

from pytgcalls.pytgcalls import PyTgCalls  # الآن سيجده بشكل صحيح
from pytgcalls import idle

# المتغيرات من بيئة Render
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))

# إنشاء عميل Pyrogram (جلسة يوزربوت)
app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# تهيئة PyTgCalls مع الجلسة
pytgcalls_client = PyTgCalls(app)

@app.on_message(filters.command("join", prefixes=["/", "!"]))
async def join_call(_, message):
    chat_id = GROUP_ID
    try:
        await pytgcalls_client.join_group_call(chat_id, "silence.mp3")
        await message.reply("✅ انضممت إلى المكالمة الصوتية.")
    except Exception as e:
        await message.reply(f"❌ خطأ أثناء الانضمام: {e}")

@app.on_message(filters.command("leave", prefixes=["/", "!"]))
async def leave_call(_, message):
    chat_id = GROUP_ID
    try:
        await pytgcalls_client.leave_group_call(chat_id)
        await message.reply("👋 غادرت المكالمة الصوتية.")
    except Exception as e:
        await message.reply(f"❌ خطأ أثناء المغادرة: {e}")

# تشغيل العملاء
async def main():
    await app.start()
    await pytgcalls_client.start()
    print("✅ البوت يعمل الآن وينتظر الأوامر...")
    await idle()
    await app.stop()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

