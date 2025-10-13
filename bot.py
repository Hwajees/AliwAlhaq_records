import os
from datetime import datetime
import subprocess
from threading import Thread

from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from flask import Flask

# =======================
# قراءة متغيرات البيئة
# =======================
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
GROUP_ID = os.environ.get("GROUP_ID")
PORT = int(os.environ.get("PORT", 10000))  # يمكنك تحديد البورت في المتغيرات

# =======================
# إعداد اليوزربوت
# =======================
app = Client(session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
pytgcalls = PyTgCalls(app)

# =======================
# متغيرات التحكم
# =======================
is_recording = False
current_title = ""
current_file = ""

# =======================
# Flask للتأكد أن البوت يعمل
# =======================
app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "Userbot is running"

def run_flask():
    app_flask.run(host="0.0.0.0", port=PORT)

# =======================
# دوال مساعدة
# =======================
def sanitize_filename(s: str) -> str:
    """تحويل النص إلى اسم ملف صالح"""
    return "".join(c for c in s if c.isalnum() or c in " _-").strip().replace(" ", "_")

async def is_user_admin(chat_id, user_id):
    admins = await app.get_chat_members(chat_id, filter="administrators")
    return any(a.user.id == user_id for a in admins)

# =======================
# أوامر التسجيل
# =======================
@app.on_message(filters.group & filters.text)
async def handle_messages(client, message):
    global is_recording, current_title, current_file

    if str(message.chat.id) != str(GROUP_ID):
        return

    if not await is_user_admin(message.chat.id, message.from_user.id):
        await message.reply("❌ ليس لديك صلاحية استخدام هذا الأمر.")
        return

    # بدء التسجيل
    if message.text.startswith("سجل المحادثة"):
        if is_recording:
            await message.reply("⚠️ التسجيل جارٍ بالفعل!")
            return
        parts = message.text.split(" ", 2)
        title = parts[2].strip() if len(parts) > 2 else f"جلسة_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        current_title = title
        current_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{sanitize_filename(title)}.raw"
        is_recording = True
        await message.reply(f"✅ بدأ التسجيل: {title}")
        return

    # إيقاف التسجيل
    if message.text.startswith("أوقف التسجيل"):
        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return
        is_recording = False

        # تحويل raw إلى mp3
        mp3_file = current_file.replace(".raw", ".mp3")
        subprocess.run([
            "ffmpeg", "-y", "-i", current_file, "-vn",
            "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_file
        ])

        # إرسال الملف للقناة
        caption = f"🎙 التسجيل: {current_title}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"
        await app.send_audio(CHANNEL_ID, audio=mp3_file, caption=caption)

        # حذف الملفات المؤقتة
        os.remove(current_file)
        os.remove(mp3_file)

        await message.reply(f"✅ تم إيقاف التسجيل وحفظ الملف: {current_title}")

# =======================
# تشغيل Flask و البوت
# =======================
if __name__ == "__main__":
    print("✅ اليوزر بوت جاهز للعمل")
    # تشغيل Flask في Thread منفصل
    Thread(target=run_flask).start()
    # تشغيل Pyrogram
    app.run()
