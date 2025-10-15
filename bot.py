import os
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from flask import Flask
import threading

# -----------------------------
# إعدادات Userbot
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
USERNAME = os.environ.get("USERNAME")  # اسم المستخدم بدون @

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

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
# استقبال أي رسالة صوتية أو voice من المشرف
# -----------------------------
@app.on_message(filters.chat(GROUP_ID) & (filters.audio | filters.voice))
async def handle_audio(client, message):
    user = message.from_user
    if not user:
        return

    if not await is_user_admin(GROUP_ID, user.id):
        return

    # رابط النصي للخاص
    private_url = f"https://t.me/{USERNAME}?start=archive_{message.from_user.id}"

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
# اختبار الوصول للخاص
# -----------------------------
@app.on_message(filters.private & filters.command("start"))
async def handle_private(client, message):
    if len(message.command) > 1 and message.command[1].startswith("archive_"):
        await message.reply_text("🎧 لقد دخلت للخاص! هنا يمكنك متابعة الأرشفة لاحقًا.")
    else:
        await message.reply_text("👋 أهلاً! استخدم الرابط من المجموعة لبدء الأرشفة.")

# -----------------------------
# Flask لإبقاء Render مستيقظ
# -----------------------------
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Userbot is running ✅"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

# -----------------------------
# تشغيل اليوزربوت + Flask
# -----------------------------
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    app.run()
