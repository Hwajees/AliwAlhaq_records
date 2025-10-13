import os
from datetime import datetime
import subprocess
from threading import Thread

from flask import Flask
from pyrogram import Client, filters
from pytgcalls import PyTgCall

# -----------------------------
# قراءة متغيرات البيئة من Render
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))  # تأكد أنه رقم وليس @username
GROUP_ID = int(os.environ.get("GROUP_ID"))
PORT = int(os.environ.get("PORT", 10000))

# -----------------------------
# إعداد Pyrogram و PyTgCalls
# -----------------------------
app = Client(SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
pytgcalls = PyTgCall(app)

# -----------------------------
# Flask لمراقبة البوت
# -----------------------------
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Userbot is running ✅"

# -----------------------------
# متغيرات التحكم بالتسجيل
# -----------------------------
is_recording = False
current_title = ""
current_file = ""

def sanitize_filename(s: str) -> str:
    return "".join(c for c in s if c.isalnum() or c in " _-").strip().replace(" ", "_")

async def is_user_admin(chat_id, user_id):
    admins = [a async for a in app.get_chat_members(chat_id, filter="administrators")]
    return any(a.user.id == user_id for a in admins)

# -----------------------------
# أوامر المجموعة
# -----------------------------
@app.on_message(filters.group & filters.text)
async def handle_messages(client, message):
    global is_recording, current_title, current_file

    if str(message.chat.id) != str(GROUP_ID):
        return

    if not await is_user_admin(message.chat.id, message.from_user.id):
        await message.reply("❌ ليس لديك صلاحية استخدام هذا الأمر.")
        return

    text = message.text.strip()

    # بدء التسجيل
    if text.startswith("سجل المحادثة"):
        if is_recording:
            await message.reply("⚠️ التسجيل جارٍ بالفعل!")
            return

        parts = text.split(" ", 2)
        title = parts[2].strip() if len(parts) > 2 else f"جلسة_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        current_title = title
        current_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{sanitize_filename(title)}.raw"
        is_recording = True
        await message.reply(f"✅ بدأ التسجيل: {title}")

    # إيقاف التسجيل
    elif text.startswith("أوقف التسجيل"):
        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        is_recording = False
        mp3_file = current_file.replace(".raw", ".mp3")
        subprocess.run([
            "ffmpeg", "-y", "-i", current_file, "-vn", "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_file
        ])

        caption = f"🎙 التسجيل: {current_title}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"
        await app.send_audio(CHANNEL_ID, audio=mp3_file, caption=caption)

        os.remove(current_file)
        os.remove(mp3_file)
        await message.reply(f"✅ تم إيقاف التسجيل وحفظ الملف: {current_title}")

# -----------------------------
# تشغيل Flask + البوت
# -----------------------------
def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("✅ Userbot جاهز للعمل")
    app.run()
