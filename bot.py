import os
import subprocess
from datetime import datetime
from threading import Thread
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from flask import Flask

# -----------------------------
# إعدادات البوت
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # يمكن وضع اسم القناة مثل "@AliwAlhaq_records"

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# -----------------------------
# متغيرات تسجيل الصوت
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
    global is_recording, current_title, current_file

    if str(message.chat.id) != str(GROUP_ID):
        return

    user_id = message.from_user.id
    text = message.text.strip()

    # تحقق من صلاحية المشرف
    is_admin = await is_user_admin(message.chat.id, user_id)

    if not is_admin:
        # لا نرد على الأعضاء العاديين
        return

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

    elif text.startswith("أوقف التسجيل"):
        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        is_recording = False

        # إرسال الملف التجريبي بدل التسجيل الحقيقي
        test_file = "test_audio.ogg"  # يجب رفعه في مجلد المشروع
        if not os.path.exists(test_file):
            await message.reply("❌ حدث خطأ: الملف التجريبي غير موجود.")
            return

        try:
            caption = f"🎙 التسجيل: {current_title}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"
            await app.send_audio(CHANNEL_ID, audio=test_file, caption=caption)
            await message.reply(f"✅ تم إرسال التسجيل للقناة: {current_title}")
        except Exception as e:
            await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {e}")

# -----------------------------
# Flask Web Server صغير
# -----------------------------
flask_app = Flask("")

@flask_app.route("/")
def home():
    return "Userbot is running."

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

# -----------------------------
# تشغيل البوت والسيرفر
# -----------------------------
if __name__ == "__main__":
    print("🚀 Starting userbot...")
    # شغل Flask server في Thread منفصل
    Thread(target=run_flask).start()
    # شغل Pyrogram
    app.run()
