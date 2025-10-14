import os
from datetime import datetime
from pyrogram import Client, filters

# -----------------------------
# إعدادات البوت
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# -----------------------------
# متغيرات تسجيل الصوت
# -----------------------------
is_recording = False
current_title = ""

# -----------------------------
# دوال مساعدة
# -----------------------------
def sanitize_filename(name):
    return "".join(c if c.isalnum() else "_" for c in name)

async def is_user_admin(chat_id, user_id):
    try:
        async for member in app.get_chat_members(chat_id, filter="administrators"):
            if member.user.id == user_id:
                return True
    except Exception as e:
        print(f"Error checking admin: {e}")
    return False

# -----------------------------
# أوامر المجموعة
# -----------------------------
@app.on_message(filters.group & filters.text)
async def handle_messages(client, message):
    global is_recording, current_title

    if str(message.chat.id) != str(GROUP_ID):
        return

    text = message.text.strip()

    # تحقق من الصلاحيات
    if not await is_user_admin(message.chat.id, message.from_user.id):
        await message.reply("❌ ليس لديك الصلاحية لاستخدام هذا الأمر.")
        return

    # بدء التسجيل
    if text.startswith("سجل المحادثة"):
        if is_recording:
            await message.reply("⚠️ التسجيل جارٍ بالفعل!")
            return

        parts = text.split(" ", 2)
        title = parts[2].strip() if len(parts) > 2 else f"جلسة_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        current_title = title
        is_recording = True
        await message.reply(f"✅ بدأ التسجيل: {title}")

    # إيقاف التسجيل وإرسال الملف التجريبي
    elif text.startswith("أوقف التسجيل"):
        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        is_recording = False
        test_file = "test_audio.ogg"

        if os.path.exists(test_file):
            caption = f"🎙 التسجيل: {current_title}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"
            await app.send_audio(CHANNEL_ID, audio=test_file, caption=caption)
            await message.reply(f"✅ تم إرسال الملف إلى القناة بنجاح: {current_title}")
        else:
            await message.reply("⚠️ ملف الاختبار غير موجود.")

# -----------------------------
# تشغيل البوت
# -----------------------------
if __name__ == "__main__":
    print("✅ Starting userbot + web server...")
    app.run()
