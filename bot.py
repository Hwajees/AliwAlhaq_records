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
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

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
        current_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{sanitize_filename(title)}.ogg"
        is_recording = True
        await message.reply(f"✅ بدأ التسجيل: {title}")

    # إيقاف التسجيل
    elif text.startswith("أوقف التسجيل"):
        if not is_recording:
            await message.reply("⚠️ لا يوجد تسجيل جارٍ الآن!")
            return

        is_recording = False

        # رفع الملف كما هو إلى القناة بدون تحويل
        caption = (
            f"🎙 التسجيل: {current_title}\n"
            f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"👥 المجموعة: {GROUP_ID}"
        )
        await app.send_document(CHANNEL_ID, document=current_file, caption=caption)

        os.remove(current_file)
        await message.reply(f"✅ تم إيقاف التسجيل ورفع الملف: {current_title}")

# -----------------------------
# تسجيل الرسائل الصوتية أثناء التشغيل
# -----------------------------
@app.on_message(filters.group & filters.voice)
async def record_voice_messages(client, message):
    global is_recording, current_file

    if str(message.chat.id) != str(GROUP_ID):
        return

    if is_recording:
        # حفظ الرسالة الصوتية كما هي
        await message.download(current_file)

# -----------------------------
# تشغيل البوت
# -----------------------------
if __name__ == "__main__":
    app.run()
