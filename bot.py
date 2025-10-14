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
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # يمكن أن يكون اسم القناة @AliwAlhaq_records

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
    """
    تحقق إن كان المستخدم مشرف أو مالك
    """
    async for member in app.get_chat_members(chat_id, filter="administrators"):
        if member.user.id == user_id:
            return True
    return False

# -----------------------------
# التعامل مع الرسائل في المجموعة
# -----------------------------
@app.on_message(filters.group & filters.text)
async def handle_messages(client, message):
    global is_recording, current_title, current_file

    if str(message.chat.id) != str(GROUP_ID):
        return

    text = message.text.strip()

    # قائمة الأوامر المسموح بها
    allowed_commands = ["سجل المحادثة", "أوقف التسجيل", "/testfile"]

    # تجاهل أي رسالة غير أمر
    if not any(text.startswith(cmd) for cmd in allowed_commands):
        return

    # تحقق من الصلاحيات
    if not await is_user_admin(message.chat.id, message.from_user.id):
        await message.reply("❌ ليس لديك صلاحية استخدام هذا الأمر.")
        return

    # ---------- أمر بدء التسجيل ----------
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

    # ---------- أمر إيقاف التسجيل ----------
    elif text.startswith("أوقف التسجيل"):
        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        is_recording = False

        # تأكد أن الملف موجود للتجربة
        if not os.path.exists(current_file):
            await message.reply(f"❌ حدث خطأ: الملف {current_file} غير موجود.")
            return

        try:
            caption = f"🎙 التسجيل: {current_title}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"
            await app.send_document(CHANNEL_ID, current_file, caption=caption)
            await message.reply(f"✅ تم إيقاف التسجيل وإرسال الملف للقناة: {current_title}")
        except Exception as e:
            await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {e}")

    # ---------- أمر اختبار الإرسال ----------
    elif text.startswith("/testfile"):
        test_file = "test_audio.ogg"
        if not os.path.exists(test_file):
            await message.reply("❌ الملف التجريبي غير موجود.")
            return
        try:
            await app.send_document(CHANNEL_ID, test_file, caption="🔹 اختبار الإرسال من اليوزبوت")
            await message.reply("✅ تم إرسال الملف التجريبي للقناة.")
        except Exception as e:
            await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {e}")

# -----------------------------
# تشغيل البوت
# -----------------------------
if __name__ == "__main__":
    print("🚀 Starting userbot...")
    app.run()
