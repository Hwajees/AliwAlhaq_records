import os
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import PeerIdInvalid

# -----------------------------
# إعدادات البوت
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # مثال: @AliwAlhaq_records

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

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
    async for member in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
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

    user_id = message.from_user.id
    text = message.text.strip()

    # تحقق من صلاحية المستخدم
    if not await is_user_admin(message.chat.id, user_id):
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
        try:
            await app.send_audio(CHANNEL_ID, audio=current_file, caption=caption)
            await message.reply(f"✅ تم إيقاف التسجيل وإرساله للقناة: {current_title}")
        except PeerIdInvalid:
            await message.reply("❌ حدث خطأ أثناء إرسال الملف: تحقق من اسم القناة أو صلاحيات البوت.")
        except Exception as e:
            await message.reply(f"❌ حدث خطأ: {e}")

    # إرسال ملف اختبار
    elif text.startswith("/testfile"):
        test_file = "test_audio.ogg"
        try:
            await app.send_audio(CHANNEL_ID, audio=test_file, caption="🔹 اختبار الإرسال من اليوزبوت")
            await message.reply("✅ تم إرسال الملف التجريبي للقناة.")
        except PeerIdInvalid:
            await message.reply("❌ حدث خطأ: تحقق من اسم القناة أو صلاحيات البوت.")
        except Exception as e:
            await message.reply(f"❌ حدث خطأ: {e}")

# -----------------------------
# تشغيل البوت
# -----------------------------
if __name__ == "__main__":
    print("✅ Starting userbot + web server...")
    app.run()
