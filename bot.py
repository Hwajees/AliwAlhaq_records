import os
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from flask import Flask
import threading

# -----------------------------
# إعدادات اليوزربوت
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
USERNAME = os.environ.get("USERNAME")  # اسم المستخدم بدون @ مثلاً: AliwAlhaqUserbot

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# -----------------------------
# دالة التحقق من المشرف
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
# استقبال المقاطع الصوتية في المجموعة
# -----------------------------
@app.on_message(filters.group & filters.audio | filters.voice)
async def handle_audio(client, message):
    if message.chat.id != GROUP_ID:
        return

    user_id = message.from_user.id
    if not await is_user_admin(GROUP_ID, user_id):
        return

    # إنشاء رابط خاص للمتابعة
    private_url = f"https://t.me/{USERNAME}?start=archive_{message.audio.file_unique_id if message.audio else message.voice.file_unique_id}"

    caption = (
        "تم استلام المقطع الصوتي ✅\n"
        f"[اضغط هنا للمحادثة الخاصة مع البوت]({private_url})"
    )

    await message.reply_text(
        caption,
        disable_web_page_preview=True,
        parse_mode="markdown"
    )


# -----------------------------
# معالجة الأوامر في الخاص
# -----------------------------
@app.on_message(filters.private & filters.command("start"))
async def start_command(client, message):
    if len(message.command) > 1 and message.command[1].startswith("archive_"):
        await message.reply("🎧 تم استقبال طلب الأرشفة! أرسل لي الآن:\n\n1️⃣ عنوان المقطع\n2️⃣ اسم المتحدث الرئيسي")
    else:
        await message.reply("👋 أهلًا! أرسل /start archive من المجموعة بعد رفع مقطع صوتي.")


# -----------------------------
# Flask لإبقاء Render مستيقظًا
# -----------------------------
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Userbot is running ✅"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    print("🚀 Starting userbot...")
    threading.Thread(target=run_flask).start()
    app.run()
