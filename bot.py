import os
from datetime import datetime
from pyrogram import Client, filters

# -----------------------------
# إعدادات البوت
# -----------------------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROUP_ID = int(os.environ.get("GROUP_ID"))
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # يمكن وضع اسم القناة @اسم_القناة أو -ID

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

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
    from pyrogram.enums import ChatMemberStatus
    async for member in app.get_chat_members(chat_id, filter="administrators"):
        if member.user.id == user_id or member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
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

    # تحقق من صلاحية المشرف
    is_admin = await is_user_admin(message.chat.id, user_id)

    # أمر بدء التسجيل
    if text.startswith("سجل المحادثة"):
        if not is_admin:
            await message.reply("❌ ليس لديك صلاحية استخدام هذا الأمر.")
            return

        if is_recording:
            await message.reply("⚠️ التسجيل جارٍ بالفعل!")
            return

        parts = text.split(" ", 2)
        title = parts[2].strip() if len(parts) > 2 else f"جلسة_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        current_title = title
        current_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{sanitize_filename(title)}.ogg"
        is_recording = True
        await message.reply(f"✅ بدأ التسجيل: {title}")

    # أمر إيقاف التسجيل
    elif text.startswith("أوقف التسجيل"):
        if not is_admin:
            await message.reply("❌ ليس لديك صلاحية استخدام هذا الأمر.")
            return

        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        is_recording = False
        test_file = "test_audio.ogg"  # ملف تجريبي للاختبار
        if not os.path.exists(test_file):
            await message.reply("❌ حدث خطأ: الملف التجريبي غير موجود.")
            return

        try:
            caption = f"🎙 التسجيل: {current_title}\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 المجموعة: {GROUP_ID}"
            await app.send_audio(CHANNEL_ID, audio=test_file, caption=caption)
            await message.reply(f"✅ تم إرسال التسجيل للقناة: {current_title}")
        except Exception as e:
            await message.reply(f"❌ حدث خطأ أثناء إرسال الملف: {e}")

    # تجاهل أي رسالة أخرى من الأعضاء العاديين
    else:
        if not is_admin:
            return  # لا يفعل شيء للأعضاء العاديين

# -----------------------------
# تشغيل البوت
# -----------------------------
if __name__ == "__main__":
    app.run()
