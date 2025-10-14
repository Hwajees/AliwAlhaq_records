import os
import subprocess
from datetime import datetime
from pyrogram import Client, filters
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
PORT = int(os.environ.get("PORT", 10000))  # ضروري للويب سيرفس

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# -----------------------------
# متغيرات التسجيل
# -----------------------------
is_recording = False
current_title = ""
current_file = ""

# -----------------------------
# دوال مساعدة
# -----------------------------
def sanitize_filename(name):
    return "".join(c if c.isalnum() else "_" for c in name)

async def is_user_admin(chat_id, user_id):
    async for member in app.get_chat_members(chat_id, filter="administrators"):
        if member.user.id == user_id:
            return True
    return False

# -----------------------------
# أوامر المجموعة
# -----------------------------
@app.on_message(filters.group & filters.text)
async def handle_messages(client, message):
    global is_recording, current_title, current_file

    if str(message.chat.id) != str(GROUP_ID):
        return

    text = message.text.strip()

    # تحقق من أن المرسل مشرف
    is_admin = await is_user_admin(message.chat.id, message.from_user.id)
    if not is_admin:
        await message.reply("❌ ليس لديك صلاحية استخدام هذا الأمر.")
        return

    # بدء التسجيل
    if text.startswith("سجل المحادثة"):
        if is_recording:
            await message.reply("⚠️ التسجيل جارٍ بالفعل!")
            return

        parts = text.split(" ", 2)
        title = parts[2].strip() if len(parts) > 2 else f"جلسة_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        current_title = title
        current_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{sanitize_filename(title)}.ogg"
        is_recording = True
        await message.reply(f"✅ بدأ التسجيل: {title}")

    # إيقاف التسجيل
    elif text.startswith("أوقف التسجيل"):
        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        is_recording = False
        caption = f"🎙 التسجيل: {current_title}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"

        # إرسال الملف كما هو (بدون تحويل)
        await app.send_audio(CHANNEL_ID, audio=current_file, caption=caption)

        # حذف الملف بعد الإرسال
        if os.path.exists(current_file):
            os.remove(current_file)

        await message.reply(f"✅ تم إيقاف التسجيل وأُرسل إلى القناة.")

# -----------------------------
# Flask للحفاظ على السيرفر حيّ
# -----------------------------
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "✅ Userbot is running!"

def run_web():
    web_app.run(host="0.0.0.0", port=PORT)

# -----------------------------
# تشغيل البوت والخادم معًا
# -----------------------------
if __name__ == "__main__":
    print("🚀 Starting userbot + web server...")
    threading.Thread(target=run_web).start()
    app.run()
