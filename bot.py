import os
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from datetime import datetime

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
# أوامر الاختبار
# -----------------------------
@app.on_message(filters.command("testfile") & filters.group)
async def send_test_file(client, message):
    if not await is_user_admin(message.chat.id, message.from_user.id):
        await message.reply("❌ ليس لديك صلاحية استخدام هذا الأمر.")
        return

    test_file_path = "test_audio.ogg"  # تأكد من وجود الملف في مجلد المشروع
    caption = "🔹 اختبار الإرسال من اليوزبوت"
    try:
        await app.send_document(CHANNEL_ID, test_file_path, caption=caption)
        await message.reply("✅ تم إرسال الملف التجريبي إلى القناة بنجاح!")
    except Exception as e:
        await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {e}")

# -----------------------------
# أوامر المجموعة (تسجيل صوت)
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
        # هنا نجرب رفع ملف صوت تجريبي بدل التسجيل الحقيقي
        test_file_path = "test_audio.ogg"
        caption = f"🎙 التسجيل: {current_title}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"
        try:
            await app.send_document(CHANNEL_ID, test_file_path, caption=caption)
            await message.reply(f"✅ تم إيقاف التسجيل وإرسال الملف التجريبي للقناة: {current_title}")
        except Exception as e:
            await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {e}")

# -----------------------------
# تشغيل البوت
# -----------------------------
if __name__ == "__main__":
    print("🚀 Starting userbot...")
    app.run()
