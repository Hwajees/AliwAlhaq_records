import os
from datetime import datetime
from pyrogram import Client, filters
import subprocess
import os
from flask import Flask

app_flask = Flask(__name__)

# ===========================
# قراءة متغيرات البيئة
# ===========================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
CHANNEL_ID = os.getenv("CHANNEL_ID")      # @اسم القناة
GROUP_ID = os.getenv("GROUP_ID")          # @اسم المجموعة
SESSION_STRING = os.getenv("SESSION_STRING")  # Session String userbot

# ===========================
# إعداد Userbot باستخدام SESSION_STRING
# ===========================
app = Client(
    session_string=SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH
)

# ===========================
# متغيرات التحكم بالتسجيل
# ===========================
is_recording = False
current_title = ""
current_file = ""

# ===========================
# تنظيف العنوان ليكون اسم ملف صالح
# ===========================
def sanitize_filename(s: str) -> str:
    return "".join(c for c in s if c.isalnum() or c in " _-").strip().replace(" ", "_")

# ===========================
# التحقق إذا المستخدم مشرف
# ===========================
async def is_user_admin(chat_id, user_id):
    admins = await app.get_chat_members(chat_id, filter="administrators")
    return any(a.user.id == user_id for a in admins)

# ===========================
# أمر بدء التسجيل
# ===========================
@app.on_message(filters.chat(GROUP_ID) & filters.text)
async def start_record(client, message):
    global is_recording, current_title, current_file

    if not await is_user_admin(message.chat.id, message.from_user.id):
        await message.reply("❌ ليس لديك صلاحية استخدام هذا الأمر.")
        return

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

# ===========================
# أمر إيقاف التسجيل
# ===========================
@app.on_message(filters.chat(GROUP_ID) & filters.text)
async def stop_record(client, message):
    global is_recording, current_title, current_file

    if not await is_user_admin(message.chat.id, message.from_user.id):
        await message.reply("❌ ليس لديك صلاحية استخدام هذا الأمر.")
        return

    if message.text.startswith("أوقف التسجيل"):
        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        is_recording = False

        # تحويل raw إلى mp3 باستخدام ffmpeg
        mp3_file = current_file.replace(".raw", ".mp3")
        subprocess.run(["ffmpeg", "-y", "-i", current_file, "-vn", "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_file])

        # إرسال الملف للقناة
        caption = f"🎙 التسجيل: {current_title}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"
        await app.send_audio(CHANNEL_ID, audio=mp3_file, caption=caption)

        # حذف الملفات المؤقتة
        os.remove(current_file)
        os.remove(mp3_file)

        await message.reply(f"✅ تم إيقاف التسجيل وحفظ الملف: {current_title}")

# ===========================
# تشغيل اليوزر بوت
# ===========================

@app_flask.route("/")
def home():
    return "Userbot is running"

if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))).start()
    # تشغيل اليوزربوت
    app.run()  # هذا من Pyrogram

