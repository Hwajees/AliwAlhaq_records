import sys
sys.path.append("libs")

from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

# 🔹 ضع بياناتك هنا
API_ID = int("ضع_هنا_API_ID")
API_HASH = "ضع_هنا_API_HASH"
SESSION_STRING = "ضع_هنا_STRING_SESSION"

# 🔹 إنشاء عميل Pyrogram
app = Client(
    ":memory:",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# 🔹 إنشاء عميل المكالمات الصوتية
call = PyTgCalls(app)

# 🔹 أمر الصعود للمحادثة الصوتية
@app.on_message(filters.command("صعد", prefixes=["", "/"]))
async def join_vc(client, message):
    chat_id = message.chat.id
    try:
        await call.join_group_call(chat_id, AudioPiped("silence.mp3"))
        await message.reply("✅ صعدت إلى المحادثة الصوتية.")
    except Exception as e:
        await message.reply(f"❌ حدث خطأ أثناء الصعود: {e}")

# 🔹 أمر النزول من المحادثة الصوتية
@app.on_message(filters.command("انزل", prefixes=["", "/"]))
async def leave_vc(client, message):
    chat_id = message.chat.id
    try:
        await call.leave_group_call(chat_id)
        await message.reply("⬇️ نزلت من المحادثة الصوتية.")
    except Exception as e:
        await message.reply(f"❌ حدث خطأ أثناء النزول: {e}")

# 🔹 تشغيل البوت
if __name__ == "__main__":
    call.start()
    print("🚀 البوت يعمل الآن وينتظر الأوامر...")
    app.run()
